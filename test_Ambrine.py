import os
import json
import subprocess
from pathlib import Path

#import du module FFmpeg
os.environ["PATH"] += os.pathsep + r"C:/Users/ambri/anaconda3/envs/projet_hydracos/Library/bin" #!! à changer : chemin qui pointe vers ffmpeg.exe

#import des données
data = os.path.join('C:/Users/ambri/Desktop/Master TELENVI/S3/PPro/projet_pro_telenvi_donnees/FFMPEG_TEST')
video_test = os.path.join(data, 'DO-Blum-trim-5s.insv')


def insv_to_equirect_frames(
    insv, out_dir= data,
        fps=5, fov=198.5,
    w=3840, h=1920, swap=False, fmt="png"):

    """
    Effectue la conversion des vidéos dual fisheye .insv en images équirectangulaires .png


    :param insv: chemin pointant vers la vidéo
    :param out_dir: chemin pointant vers le dossier d'export
    :param fps: nombre de frames extraites par secinde
    :param fov: angle de capture de la caméra pour 1 fisheye (avantage : 195 permet un recouvrement)

    Les deux paramètres suivants sont définis fonction des données produites par Insta360
    :param w: paramètre width = largeur en pixels de l'image de sortie
    :param h: paramètre height = hauteur en pixels de l'image de sortie

    :param swap: False = ordre par défaut des flux
                 True = inverse flux 0 et 1 (si raccord avant/arrière inversé)
    :param fmt: format d'export

    :return:
    """

    insv, out_dir = str(insv), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # vérification du nb de flux vidéos
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v",
         "-show_entries", "stream=index,width,height",
         "-of", "json", insv],
        capture_output=True, text=True, check=True,
    )
    streams = json.loads(probe.stdout)["streams"]
    if len(streams) < 2:
        raise ValueError(f"{len(streams)} flux vidéo, 2 attendus")

    #choix de l'ordre des flux (des deux pov des fisheyes)
    a, b = ("0:v:1", "0:v:0") if swap else ("0:v:0", "0:v:1")
    graph = (
        f"[{a}][{b}]hstack=inputs=2,"
        f"v360=dfisheye:e:ih_fov={fov}:iv_fov={fov}:w={w}:h={h}:roll=180,"
        f"fps={fps}[out]"
    )

    #commande Python pour effectuer le Bash
    cmd = [
        "ffmpeg",
        "-y", #écrase les fichiers si déjà existants !!
        "-i", insv,
        "-filter_complex", graph, "-map", "[out]",
        str(out_dir / f"img_%05d.{fmt}"),
    ]
    subprocess.run(cmd, check=True)

    return out_dir

insv_to_equirect_frames(video_test, fps=5)

