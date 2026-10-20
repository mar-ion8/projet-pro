import json
import os
import subprocess
import pycolmap
from pathlib import Path

# Pour que Python trouve ffmpeg/ffprobe (à adapter)
os.environ["PATH"] += os.pathsep + r"C:/Users/ambri/anaconda3/envs/projet_hydracos/Library/bin"

# Vues prises dans CHAQUE fisheye : nom -> (yaw, pitch) en degrés.
# 5 vues de 90° décalées de 45° : elles se recouvrent à moitié (bon pour le matching)
# et restent dans le cercle image (< ~95° de l'axe de l'objectif).
VIEWS = {
    "c": (0, 0),
    "l": (-45, 0),
    "r": (45, 0),
    "u": (0, 45),
    "d": (0, -45),
    "L": (-70, 0),
    "R": (70, 0),
}


def insv_to_views(insv, out_dir, fps= 10, fov=198.5, size=960):
    """
    Extrait des vues perspectives (sans distorsion) directement depuis les deux
    fisheyes d'un .insv, SANS recoller les deux objectifs : plus de couture,
    donc plus de décalage dû à la parallaxe entre les deux objectifs.

    :param insv: chemin du .insv
    :param out_dir: dossier de sortie (un sous-dossier par vue : 0c, 0l, ..., 1d)
    :param fps: images extraites par seconde (2 suffit largement pour du SfM)
    :param fov: champ de vision réel d'un fisheye (mesuré ~196° sur ce fichier)
    :param size: côté d'une vue carrée en pixels
    """
    insv, out_dir = str(insv), Path(out_dir)

    print("etape_1")

    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v",
         "-show_entries", "stream=index,width,height", "-of", "json", insv],
        capture_output=True, text=True, check=True,
    )
    streams = json.loads(probe.stdout)["streams"]
    if len(streams) < 2:
        raise ValueError(f"{len(streams)} flux vidéo, 2 attendus")
    print("etape_2")
    parts, outs = [], []
    for s in (0, 1):

        labels = "".join(f"[{s}x{k}]" for k in VIEWS)
        # fps AVANT le reste : ffmpeg ne calcule que les images gardées (24x plus rapide)
        parts.append(f"[0:v:{s}]fps={fps},split={len(VIEWS)}{labels}")
        for k, (yaw, pitch) in VIEWS.items():
            parts.append(
                f"[{s}x{k}]v360=input=fisheye:output=flat"
                f":ih_fov={fov}:iv_fov={fov}:h_fov=90:v_fov=90:roll=180"
                f":yaw={yaw}:pitch={pitch}:w={size}:h={size}:interp=cubic[o{s}{k}]"
            )
            outs.append((f"o{s}{k}", f"{s}{k}"))

    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", insv,
           "-filter_complex", ";".join(parts)]
    for label, name in outs:
        (out_dir / name).mkdir(parents=True, exist_ok=True)
        cmd += ["-map", f"[{label}]", str(out_dir / name / "img_%05d.png")]
    subprocess.run(cmd, check=True)
    print("etape_3")
    # Intrinsèques à donner à COLMAP (vues rectilignes de 90° => f = size/2, pas de distorsion)
    f = size / 2
    print(f"COLMAP : --ImageReader.single_camera 1 --ImageReader.camera_model PINHOLE "
          f'--ImageReader.camera_params "{f},{f},{f},{f}"')
    return out_dir

def run_colmap(base, size=960):
    base = Path(base)
    print("etape_4")
    db, views, sparse = base / "db.db", base / "views", base / "sparse"
    sparse.mkdir(exist_ok=True)
    f = size / 2

    # 1. points d'intérêt (seulement si la base n'existe pas déjà)
    if not db.exists():
        reader = pycolmap.ImageReaderOptions()
        reader.camera_model = "PINHOLE"
        reader.camera_params = f"{f},{f},{f},{f}"

        ext = pycolmap.FeatureExtractionOptions()
        ext.sift.max_num_features = 32768     # défaut : 8192
        ext.sift.peak_threshold = 0.003       # défaut : ~0.0067, plus bas = plus de points

        pycolmap.extract_features(
            db, views,
            camera_mode=pycolmap.CameraMode.SINGLE,
            reader_options=reader,
            extraction_options=ext,
        )
    else:
        print("db.db existe : extraction sautée")

    # 2. mise en correspondance
    pycolmap.match_exhaustive(db)
    print("etape_6")

    # 3. reconstruction (sans modifier la focale)
    opts = pycolmap.IncrementalPipelineOptions()
    opts.ba_refine_focal_length = False
    opts.ba_refine_extra_params = False
    maps = pycolmap.incremental_mapping(db, views, sparse, options=opts)
    print("etape_7")

    # 4. résultat
    for i, rec in maps.items():
        print(f"Modèle {i} : {rec.num_reg_images()} images recalées, {rec.num_points3D()} points 3D")
        rec.export_PLY(str(sparse / f"nuage_{i}.ply"))
    return maps


if __name__ == "__main__":
    base = r"C:\Users\ambri\Desktop\Master TELENVI\S3\PPro\projet_pro_telenvi_donnees\COLMAP_TEST_2"
    insv_to_views(base + "/DO-Blum-trim-5s.insv", base + "/views", fps=2)
    run_colmap(base)