#!/usr/bin/env bash
set -euo pipefail

: "${HY_VLA_ROOT:?Set HY_VLA_ROOT to the Hy-Embodied-0.5-VLA checkout}"
: "${HDF5_ROOT:?Set HDF5_ROOT to the RoboDojo HDF5 root}"
: "${EXP_ROOT:?Set EXP_ROOT to the experiment root}"

OUTPUT=${NORM_PATH:-"${EXP_ROOT}/goai_track1_hyvla/norm_stats.pkl"}
mkdir -p "$(dirname "${OUTPUT}")"

cd "${HY_VLA_ROOT}"
python scripts/compute_norm_robodojo.py \
  --hdf5-dir "${HDF5_ROOT}" \
  --output "${OUTPUT}" \
  --downsample-rate 1 \
  --chunk-size 25 \
  --umi-coord-frame

sha256sum "${OUTPUT}"
