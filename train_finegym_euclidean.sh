#!/usr/bin/env bash
CUDA_VISIBLE_DEVICES=0 PYTORCH_JIT=0 NCCL_LL_THRESHOLD=0 python \
  -W ignore \
  -i \
  -m torch.distributed.launch \
  --master_port=9999 \
  --nproc_per_node=1 \
  main.py \
  --pred_step 3 \
  --network_feature resnet18 \
  --dataset finegym \
  --seq_len 5 \
  --num_seq 8 \
  --ds 3 \
  --batch_size 16 \
  --img_dim 128 \
  --epochs 200 \
  --fp16 \
  --num_workers 15 \
  --cross_gpu_score \
  --lr 0.001 \
  --prefix train_finegym_euclidean \
  --path_dataset dataset_info/finegym \
  --path_data_info dataset_info
