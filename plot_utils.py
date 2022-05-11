"""
Plot Train and Validation Result, final project
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
from scipy.interpolate import make_interp_spline


TRAIN_index = ['train_accuracy', 'train_losses', 'train_top1', 'train_top3', 'train_top5']
VAL_index = ['accuracy_accuracy', 'accuracy_losses', 'accuracy_top1', 'accuracy_top3', 'accuracy_top5']

# read a whole folder of tensorflow log files
def tabulate_events(dpath):
    summary_iterators = [EventAccumulator(os.path.join(dpath, dname)).Reload() for dname in os.listdir(dpath)]
    tags = summary_iterators[0].Tags()['scalars']
    for it in summary_iterators:
        assert it.Tags()['scalars'] == tags
    out = defaultdict(list)
    steps = []
    for tag in tags:
        steps = [e.step for e in summary_iterators[0].Scalars(tag)]
        for events in zip(*[acc.Scalars(tag) for acc in summary_iterators]):
            assert len(set(e.step for e in events)) == 1
            out[tag].append([e.value for e in events])
    return out, steps



def read_log(dpath):
    print('Current Reading --> ', dpath)
    # remove extra event log file
    for file_name in os.listdir(dpath):
        full_path = os.path.join(dpath, file_name)
        if not os.path.isdir(full_path):
            os.remove(full_path)
    dirs = os.listdir(dpath)
    d, steps = tabulate_events(dpath)
    tags, values = zip(*d.items())
    np_values = np.array(values)

    for index, tag in enumerate(tags):
        df = pd.DataFrame(np_values[index], index=steps, columns=dirs)
    return df

def smooth_traj(scalar_line, num_points=30):
    xold = np.arange(len(scalar_line))
    X_Y_Spline = make_interp_spline(xold, scalar_line)

    xnew = np.linspace(xold.min(), xold.max(), num_points)
    ynew = X_Y_Spline(xnew)
    return xnew, ynew

def plt_res(train_res, val_res, smooth=True):  # smooth would smooth the accuracy plot or not 
    train_acc, train_losses, train_1, train_3, train_5 = train_res
    val_acc, val_losses, val_1, val_3, val_5 = val_res
    print(f'train_top1: {train_1.max()}, train_top3: {train_3.max()}, train_top5: {train_5.max()}')
    print(f'validation_top1: {val_1.max()}, validation_top3: {val_3.max()}, validation_top5: {val_5.max()}')
    fontsize = 25
    x_index = np.arange(len(train_acc))
    if smooth:
        x_index, train_acc = smooth_traj(train_acc)
        x_index, val_acc = smooth_traj(val_acc)
        fig, axes = plt.subplots(1, figsize=(20, 10))
        first = axes
    ############# plot train, val accuracy and loss ##################
    first2 = first.twinx()
    first.plot(train_losses, '--', linewidth=6, markersize=20, label='Train Loss', color='b')
    first.plot(val_losses, '--', linewidth=6, markersize=20, label='Validation Loss', color='gray')
    first2.plot(x_index, train_acc * 100, '-o', linewidth=6, markersize=18, label='Train Accuracy', color='green')
    first2.plot(x_index, val_acc * 100, '-*', linewidth=6, markersize=26, label='Validation Accuracy', color='red')

    first.set_xlabel('Epochs', fontsize=fontsize); first.set_ylabel('Loss', fontsize=fontsize);
    first2.set_ylabel('Accuracy %', fontsize=fontsize)
    # first.set_title('Train & Validation Results', fontsize=fontsize+10)
    first.grid(); first.legend(fontsize=fontsize, loc='upper center'); first2.legend(fontsize=fontsize, loc='best')
    first.tick_params(axis="x", labelsize=fontsize); first.tick_params(axis="y", labelsize=fontsize); first2.tick_params(axis='y', labelsize=fontsize)

    plt.tight_layout()
    plt.show()

dpath = 'Hyperbolic_train'  # could be "euclidean_train" or "hyperbolic_train"
dpath_train = os.path.join(dpath, 'train')
dpath_val = os.path.join(dpath, 'val')

df_train = read_log(dpath_train)
df_val = read_log(dpath_val)
train_res = [df_train[col].to_numpy() for col in TRAIN_index]
val_res = [df_val[col].to_numpy() for col in VAL_index]
plt_res(train_res, val_res)