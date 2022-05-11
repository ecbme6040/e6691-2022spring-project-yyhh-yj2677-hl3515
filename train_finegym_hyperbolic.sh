#!/usr/bin/env bash
CUDA_VISIBLE_DEVICES=0 PYTORCH_JIT=0 NCCL_LL_THRESHOLD=0 python \
  -W ignore \
  -i \
  main.py \
  --pred_step 3 \
  --hyperbolic \
  --hyperbolic_version 1 \
  --distance squared \
  --network_feature resnet18 \
  --dataset finegym \
  --seq_len 5 \
  --num_seq 8 \
  --ds 3 \
  --batch_size 16 \
  --img_dim 128 \
  --epochs 200 \
  --fp16 \
  --fp64_hyper \
  --num_workers 15 \
  --lr 0.001 \
  --prefix train_finegym_hyperbolic \
  --path_dataset dataset_info/finegym \
  --path_data_info dataset_info


  # -m torch.distributed.launch \
  # --master_port=8888 \
  # --nproc_per_node=1 \