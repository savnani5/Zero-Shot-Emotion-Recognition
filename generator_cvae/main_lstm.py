import argparse
import os
import numpy as np
import shutil
from utils import loader_lstm as loader, processor_lstm as processor

import torch
import torchlight


base_path = os.path.dirname(os.path.realpath(__file__))
data_path = os.path.join(base_path, '../data')
ftype = ''
coords = 3
joints = 16
cycles = 1
info_path = os.path.join(base_path, 'model_gait_cvae_lstm')
model_path = os.path.join(info_path, 'features'+ftype)


parser = argparse.ArgumentParser(description='Gait Gen')
parser.add_argument('--train', type=bool, default=False, metavar='T',
                    help='train the model (default: True)')
parser.add_argument('--batch-size', type=int, default=8, metavar='B',
                    help='input batch size for training (default: 8)')
parser.add_argument('--num-worker', type=int, default=4, metavar='W',
                    help='input batch size for training (default: 4)')
parser.add_argument('--start_epoch', type=int, default=0, metavar='SE',
                    help='starting epoch of training (default: 0)')
parser.add_argument('--num_epoch', type=int, default=100, metavar='NE',
                    help='number of epochs to train (default: 1000)')
parser.add_argument('--optimizer', type=str, default='Adam', metavar='O',
                    help='optimizer (default: Adam)')
parser.add_argument('--base-lr', type=float, default=0.1, metavar='L',
                    help='base learning rate (default: 0.1)')
parser.add_argument('--step', type=list, default=[0.5, 0.75, 0.875], metavar='[S]',
                    help='fraction of steps when learning rate will be decreased (default: [0.5, 0.75, 0.875])')
parser.add_argument('--nesterov', action='store_true', default=True,
                    help='use nesterov')
parser.add_argument('--momentum', type=float, default=0.9, metavar='M',
                    help='momentum (default: 0.9)')
parser.add_argument('--weight-decay', type=float, default=5e-4, metavar='D',
                    help='Weight decay (default: 5e-4)')
parser.add_argument('--eval-interval', type=int, default=1, metavar='EI',
                    help='interval after which model is evaluated (default: 1)')
parser.add_argument('--log-interval', type=int, default=100, metavar='LI',
                    help='interval after which log is printed (default: 100)')
parser.add_argument('--delete-previous', type=bool, default=True, metavar='DP',
                    help='delete previously save models (default: True)')
parser.add_argument('--no-cuda', action='store_true', default=False,
                    help='disables CUDA training')
parser.add_argument('--pavi-log', action='store_true', default=False,
                    help='pavi log')
parser.add_argument('--print-log', action='store_true', default=True,
                    help='print log')
parser.add_argument('--save-log', action='store_true', default=True,
                    help='save log')
parser.add_argument('--data-dir', type=str, default=data_path, metavar='WD',
                    help='path to save data')
parser.add_argument('--work-dir', type=str, default=model_path, metavar='WD',
                    help='path to save model')
# TO ADD: save_result

args = parser.parse_args()
device = 'cuda:0'

if args.train:
    data_train, data_test, labels_train, labels_test =\
        loader.load_data(data_path, ftype, coords, joints, cycles=cycles)
    tsteps = data_train.shape[1]
    features = data_train.shape[2]
    data_train, data_max, data_min = loader.scale(data_train)
    data_test, _, _ = loader.scale(data_test)
    num_classes = np.unique(labels_train).shape[0]
    np.savetxt(info_path+'/info.txt', np.array([tsteps, features, data_max, data_min, num_classes]), delimiter='\n')
    data_loader = {
        'train': torch.utils.data.DataLoader(
            dataset=loader.TrainTestLoader(data_train, labels_train, joints, coords, num_classes),
            batch_size=args.batch_size,
            shuffle=True,
            drop_last=True),
        'test': torch.utils.data.DataLoader(
            dataset=loader.TrainTestLoader(data_test, labels_test, joints, coords, num_classes),
            batch_size=args.batch_size,
            shuffle=True,
            drop_last=True)}
    pr = processor.Processor(args, ftype, data_loader, data_max, data_min,
                             coords, tsteps, joints, features, num_classes, device=device)
    if args.delete_previous:
        shutil.rmtree(model_path)
        os.mkdir(model_path)
    pr.train()
else:
    data_loader = list()
    info = np.loadtxt(info_path+'/info.txt')
    tsteps = int(info[0])
    features = int(info[1])
    data_max = info[2]
    data_min = info[3]
    num_classes = int(info[4])
    pr = processor.Processor(args, ftype, data_loader, data_max, data_min,
                             coords, tsteps, joints, features, num_classes, device=device)

pr.generate(total_samples=10)
