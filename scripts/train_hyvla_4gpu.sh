#!/usr/bin/env bash
set -euo pipefail

: "${HY_VLA_ROOT:?Set HY_VLA_ROOT to the Hy-Embodied-0.5-VLA checkout}"
: "${BASE_MODEL:?Set BASE_MODEL to Hy-Embodied-0.5-VLA-UMI}"
: "${HDF5_ROOT:?Set HDF5_ROOT to the RoboDojo HDF5 root}"
: "${EXP_ROOT:?Set EXP_ROOT to the experiment root}"

EXP_ID=${EXP_ID:-goai_track1_hyvla_200k}
RUN_DIR=${RUN_DIR:-"${EXP_ROOT}/${EXP_ID}"}
NORM_PATH=${NORM_PATH:-"${EXP_ROOT}/goai_track1_hyvla/norm_stats.pkl"}
LOG_ROOT=${LOG_ROOT:-"${EXP_ROOT}/logs"}
MAIN_PORT=${MAIN_PORT:-6690}

export HF_HUB_OFFLINE=${HF_HUB_OFFLINE:-1}
export TRANSFORMERS_OFFLINE=${TRANSFORMERS_OFFLINE:-1}
export HF_DATASETS_OFFLINE=${HF_DATASETS_OFFLINE:-1}
export WANDB_MODE=${WANDB_MODE:-offline}
export TOKENIZERS_PARALLELISM=${TOKENIZERS_PARALLELISM:-false}
export PYTHONNOUSERSITE=${PYTHONNOUSERSITE:-1}
export PYTHONPATH="${HY_VLA_ROOT}${PYTHONPATH:+:${PYTHONPATH}}"
export CUDA_DEVICE_ORDER=${CUDA_DEVICE_ORDER:-PCI_BUS_ID}
export CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-0,1,2,3}
export NCCL_DEBUG=${NCCL_DEBUG:-WARN}
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-8}

test -f "${NORM_PATH}" || {
  echo "Missing norm stats: ${NORM_PATH}" >&2
  exit 1
}

mkdir -p "${RUN_DIR}" "${LOG_ROOT}"
cd "${HY_VLA_ROOT}"

python -m accelerate.commands.launch \
  --multi_gpu \
  --num_machines 1 \
  --num_processes 4 \
  --main_process_ip 127.0.0.1 \
  --main_process_port "${MAIN_PORT}" \
  --machine_rank 0 \
  --mixed_precision bf16 \
  --dynamo_backend no \
  hy_vla/train.py \
  debug=False \
  exp_id="${EXP_ID}" \
  ckpt_save_dir="${RUN_DIR}" \
  dataset=robodojo_hdf5 \
  dataset.hdf5_dir="${HDF5_ROOT}" \
  dataset.mean_std_path="${NORM_PATH}" \
  model.pretrain_source=vla \
  model.vla_model_path="${BASE_MODEL}" \
  training.mixed_precision=bf16 \
  training.batch_size=8 \
  training.grad_accumulation_steps=1 \
  training.optimizer_lr=5e-5 \
  training.max_training_steps=200000 \
  training.scheduler_warmup_steps=1000 \
  training.scheduler_decay_steps=150000 \
  training.scheduler_decay_lr=5e-6 \
  training.ckpt_frequency=10000 \
  training.eval_frequency=5000 \
  training.max_evaluation_steps=100 \
  dataloader.num_workers=8 \
  save_training_state=False \
  2>&1 | tee "${LOG_ROOT}/${EXP_ID}.log"
