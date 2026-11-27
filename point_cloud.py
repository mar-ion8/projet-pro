"""
Version 2 (SANS rig) : insv -> vues perspectives -> COLMAP, appariement sequentiel.

Les images sont dans un seul dossier, instant AVANT la vue (t00001_0c.png, ...),
car l'appariement sequentiel de COLMAP trie les images par nom.

Usage :
    python test_colmap_v2.py --insv "/chemin/video.insv" --out /chemin/runs/run_02
Options : --fps 2  --size 960  --max-features 8192  --peak 0.005
"""
import argparse
import json
import subprocess
from pathlib import Path

import pycolmap

# Un fisheye couvre ~198 deg : on ne peut pas viser plus loin que ~100 deg de l'axe.
# Chaque vue fait 90 deg de champ. Centre + 4 vues decalees de 55 deg
# -> recouvrement de ~35 deg entre vues voisines (necessaire pour les matches),
# couverture jusqu'a ~100 deg. 5 vues x 2 objectifs = 10 vues par instant.
# nom -> (yaw, pitch) en degres
VIEWS = {
    "c": (0,    0),
    "l": (-55,  0),
    "r": (55,   0),
    "u": (0,   55),
    "d": (0,  -55),
}
VIEW_FOV = 90


def insv_to_views(insv, out_dir, fps=2, fov=198.5, size=960, per_camera_folders=False):
    """
    Extrait les vues perspectives des deux fisheyes d'un .insv.

    per_camera_folders=False : out_dir/t00001_0c.png  (un dossier, instant d'abord)
    per_camera_folders=True  : out_dir/0c/t00001.png  (un dossier par camera, pour les rigs)
    """
    insv, out_dir = str(insv), Path(out_dir)

    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=index",
         "-of", "json", insv], capture_output=True, text=True, check=True)
    if len(json.loads(probe.stdout)["streams"]) < 2:
        raise ValueError("2 flux video attendus (un par fisheye)")

    parts, outs = [], []
    for s in (0, 1):
        labels = "".join(f"[{s}x{k}]" for k in VIEWS)
        parts.append(f"[0:v:{s}]fps={fps},split={len(VIEWS)}{labels}")
        for k, (yaw, pitch) in VIEWS.items():
            parts.append(
                f"[{s}x{k}]v360=input=fisheye:output=flat"
                f":ih_fov={fov}:iv_fov={fov}:h_fov={VIEW_FOV}:v_fov={VIEW_FOV}:roll=180"
                f":yaw={yaw}:pitch={pitch}:w={size}:h={size}:interp=cubic[o{s}{k}]")
            outs.append((f"o{s}{k}", f"{s}{k}"))

    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", insv,
           "-filter_complex", ";".join(parts)]
    out_dir.mkdir(parents=True, exist_ok=True)
    for label, name in outs:
        if per_camera_folders:
            (out_dir / name).mkdir(exist_ok=True)
            target = out_dir / name / "t%05d.png"
        else:
            target = out_dir / f"t%05d_{name}.png"
        cmd += ["-map", f"[{label}]", str(target)]
    subprocess.run(cmd, check=True)
    return out_dir


def extract_sift(db, views, camera_mode, size=960, max_features=8192, peak=0.005,
                 image_names=()):
    """Extrait les features SIFT. Camera PINHOLE de focale size/2 (vue de 90 deg)."""
    f = size / 2

    reader = pycolmap.ImageReaderOptions()
    reader.camera_model = "PINHOLE"
    reader.camera_params = f"{f},{f},{f},{f}"

    ext = pycolmap.FeatureExtractionOptions()
    ext.sift.max_num_features = max_features
    ext.sift.peak_threshold = peak

    pycolmap.extract_features(db, views, image_names=list(image_names),
                              camera_mode=camera_mode,
                              reader_options=reader, extraction_options=ext)


def mapping_options():
    """Reconstruction avec focale et distorsion figees (vues deja sans distorsion)."""
    opts = pycolmap.IncrementalPipelineOptions()
    opts.ba_refine_focal_length = False
    opts.ba_refine_extra_params = False
    return opts


def export_models(maps, sparse):
    for i, rec in maps.items():
        print(f"Modele {i} : {rec.num_reg_images()} images recalees, {rec.num_points3D()} points 3D")
        rec.export_PLY(str(sparse / f"nuage_{i}.ply"))


def run_colmap(base, views, size=960, max_features=8192, peak=0.005):
    base, views = Path(base), Path(views)
    db, sparse = base / "db.db", base / "sparse"
    sparse.mkdir(exist_ok=True)

    if db.exists():
        raise FileExistsError(f"{db} existe deja : choisir un autre dossier --out ou la supprimer")

    extract_sift(db, views, pycolmap.CameraMode.SINGLE, size, max_features, peak)

    # Appariement sequentiel (images triees par nom : t00001_0c, t00001_0d, ...).
    # Images par instant = 2 objectifs x len(VIEWS). Mode lineaire : chaque image est
    # comparee aux `overlap` suivantes ; 2 instants -> toutes les vues du meme instant
    # + celles de l'instant suivant. Suit automatiquement le nombre de VIEWS.
    pairing = pycolmap.SequentialPairingOptions()
    pairing.quadratic_overlap = False
    pairing.overlap = 2 * (2 * len(VIEWS))
    pycolmap.match_sequential(db, pairing_options=pairing)

    maps = pycolmap.incremental_mapping(db, views, sparse, options=mapping_options())
    export_models(maps, sparse)
    return maps


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--insv", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--fps", type=float, default=2)
    ap.add_argument("--size", type=int, default=960)
    ap.add_argument("--max-features", type=int, default=8192)
    ap.add_argument("--peak", type=float, default=0.005)
    a = ap.parse_args()

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    views = insv_to_views(a.insv, out / "views", fps=a.fps, size=a.size)
    run_colmap(out, views, size=a.size, max_features=a.max_features, peak=a.peak)