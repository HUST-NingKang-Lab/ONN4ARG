#!/opt/miniconda3/bin/python3 -B

import sys
import h5py
import numpy as np
import torch as pt

from torch import nn
from torch.autograd import Variable
from torch.utils.data import TensorDataset, DataLoader

from glob import glob
from tqdm import tqdm
from getopt import getopt

from model import *


batch_size = 60 * 8
size_label = [0, 1, 3, 34, 193]  # used by both besthit and onn4arg
mfn, ifp, ofn = 'model-small.sav', 'input', 'output.hdf5'

optlst, arglst = getopt(sys.argv[1:], 'm:i:o:', ['model=', 'input=', 'output='])
for k, v in optlst:
  if k in ('-m', '--model'):
    mfn = v
  elif k in ('-i', '--input'):
    ifp = v
  elif k in ('-o', '--output'):
    ofn = v


idx2lab = {}
with open('tree.out', 'r') as f:
  for l in f.readlines():
    key, idx, lst = l.strip().split('\t')
    parent = l.split(',')
    idx0, idx1 = idx.split(',')
    idx0, idx1 = int(idx0), int(idx1)
    idx = idx0 * 1000 + idx1
    idx2lab[idx] = key
idx2lab = [idx2lab[i] for i in sorted(idx2lab.keys())]
idx2lab = [idx2lab[i] for i in [1, 0, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 39, 40, 42, 48, 50, 51, 52, 54, 55, 58, 62, 64, 67, 69, 71, 72, 73, 74, 75, 77, 78, 79, 84, 86, 89, 92, 93, 96, 97, 99, 104, 109, 110, 113, 115, 116, 118, 120, 121, 123, 125, 127, 128, 131, 132, 133, 134, 137, 138, 141, 142, 143, 144, 146, 147, 150, 151, 152, 153, 154, 158, 159, 162, 163, 165, 167, 168, 170, 171, 173, 175, 176, 177, 180, 181, 182, 187, 188, 189, 191, 192, 195, 196, 197, 202, 203, 204, 205, 207, 209, 210, 211, 212, 213, 214, 216, 218, 219, 221, 222, 223, 225, 226, 230, 231, 232, 236, 237, 238, 239, 240, 244, 245, 246, 247, 250, 251, 252, 253, 256, 257, 258, 260, 261, 262, 266, 267, 268, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 285, 288, 289, 291, 292, 294, 295, 296, 298, 300, 301, 302, 304, 305, 308, 310, 312, 313]]

size_seq, size_prof = 0, 0
with open('model.lst') as f:
  for l in f.readlines():
    if l.startswith('model'): size_prof += 1
    else: size_seq += 1

with open(ifp + '-seq.txt', 'r') as f:
  l = f.readline()
  d = l.strip().split('\t')
  shape = [int(v) for v in d[1:]]
  shape[0] = 1
  host_seq = np.zeros(shape, dtype=np.float16)
  for l in f.readlines():
    d = l.strip().split('\t')
    di = int(d[1])
    dv = [float(v) for v in d[2:]]
    host_seq[0, di] = dv
host_seq = host_seq[:, :size_seq, :]


with open(ifp + '-prof.txt', 'r') as f:
  l = f.readline()
  d = l.strip().split('\t')
  shape = [int(v) for v in d[1:]]
  shape[0] = 1
  host_prof = np.zeros(shape, dtype=np.float16)
  for l in f.readlines():
    d = l.strip().split('\t')
    di = int(d[1])
    dv = [float(v) for v in d[2:]]
    host_prof[0, di] = dv
host_prof = host_prof[:, -size_prof:, :]


state = pt.load(mfn, map_location=pt.device('cpu'))
tree = state['tree']
mode = state['mode']

shape_seq = state['shape_seq']
shape_prof = state['shape_prof']
shape_label = state['shape_label'][0]

model = ONN4ARG(mode, shape_seq, shape_prof, shape_label, tree)
model.load_state_dict(state['model'])
model.eval()

host_pred, dev_size = [], batch_size * 1024
for begin in range(0, len(host_seq), dev_size):
  end = min(begin + dev_size, len(host_seq))
  print("#working on %d:%d/%d ..." % (begin, end, len(host_seq)))

  dev_seq = pt.from_numpy(host_seq[begin:end, :, (3,4,5,8)]).float()
  dev_seq[:, :, -1] *= dev_seq[:, :, -2] / state['norm_seq']
  dev_prof = pt.from_numpy(host_prof[begin:end, :, (3,4,5,8)]).float()
  dev_prof[:, :, -1] *= dev_prof[:, :, -2] / state['norm_prof']
  dev_loader = DataLoader(TensorDataset(dev_seq, dev_prof), batch_size=batch_size, num_workers=1, shuffle=False, drop_last=False)

  for i, (x0, x1) in tqdm(enumerate(dev_loader)):
    x0 = Variable(x0)
    x1 = Variable(x1)
    yy = pt.ge(model(x0, x1), 0.5)
    host_pred.append(yy.cpu().detach().numpy())
  dev_seq = dev_prof = dev_loader = None

host_pred = np.concatenate(host_pred, axis=0)

with open(ofn, 'w') as f:
  for i in range(len(host_pred)):
    l = [idx2lab[i+1] for i in np.where(host_pred[i])[0]]
    if not l: l = [idx2lab[0]]
    f.write(','.join(l))

print('#done!!!')

