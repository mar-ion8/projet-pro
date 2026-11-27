# SPDX-License-Identifier: BSD-3-Clause

"""Run Structure-from-Motion on 360-degree panorama images."""

import argparse
from pathlib import Path

from pycolmap.panorama import (
    Mapper,
    Matcher,
    PanoramaReconstructionOptions,
    PanoRenderType,
    reconstruct,
)

# --- À modifier ---
INPUT_IMAGE_PATH = Path(r"C:\Users\ambri\Desktop\Master TELENVI\S3\PPro\projet_pro_telenvi_donnees\0_img")
OUTPUT_PATH = Path(r"C:\Users\ambri\Desktop\Master TELENVI\S3\PPro\projet_pro_telenvi_donnees\0_img\out")
USE_GPU = True  # True si tu as un GPU CUDA
# ------------------


def main() -> None:
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    reconstruct(
        INPUT_IMAGE_PATH,
        OUTPUT_PATH,
        PanoramaReconstructionOptions(
            matcher=Matcher.SEQUENTIAL,
            mapper=Mapper.INCREMENTAL,
            render_type=PanoRenderType.PERSPECTIVE_OVERLAPPING,
            random_seed=0,
            num_threads=-1,
            gpu_index="-1",
            use_gpu=USE_GPU,
        ),
    )


if __name__ == "__main__":
    main()