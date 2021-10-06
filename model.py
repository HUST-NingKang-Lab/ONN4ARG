#!/opt/anaconda3/bin/python3 -B

import h5py
import numpy as np
import torch as pt

from torch import nn
from torch.autograd import Variable
from torch.nn.parameter import Parameter


class FeatLayer(nn.Module):
  def __init__(self, cin, cout):
    super(FeatLayer, self).__init__()
    chid = cout * 4
    print('#FeatureLayer:', cin, chid, cout)

    self.feat = nn.Sequential(
        nn.Flatten(), nn.Linear(cin, chid),
        nn.GroupNorm(chid//16, chid), nn.GELU(), nn.Linear(chid, cout))

  def forward(self, x):
    return self.feat(x)

class ResLayer(nn.Module):
  def __init__(self, cio, dropout=0.5):
    super(ResLayer, self).__init__()
    chid = cio // 4
    print('#ResidualLayer:', cio, chid, cio)

    self.res = nn.Sequential(
        nn.GroupNorm(cio//16, cio), nn.GELU(), nn.Linear(cio, chid),
        nn.GroupNorm(chid//16, chid), nn.GELU(), nn.Linear(chid, chid),
        nn.GroupNorm(chid//16, chid), nn.GELU(), nn.Linear(chid, chid),
        nn.GroupNorm(chid//16, chid), nn.GELU(), nn.Linear(chid, cio),
        nn.Dropout(dropout))

  def forward(self, x):
    return x + self.res(x)

class ResBlock(nn.Module):
  def __init__(self, cio, depth, dropout=0.5):
    super(ResBlock, self).__init__()
    layers = [ResLayer(cio, dropout=dropout) for i in range(depth)]
    self.block = nn.Sequential(*layers)

  def forward(self, x):
    return self.block(x)

class CompLayer(nn.Module):
  def __init__(self, cin, cout):
    super(CompLayer, self).__init__()
    print('#CompressLayer:', cin, cout)

    self.comp = nn.Sequential(
        nn.GroupNorm(cin//16, cin), nn.GELU(), nn.Linear(cin, cout))

  def forward(self, x):
    return self.comp(x)

class OntLayer(nn.Linear):
  def __init__(self, cio, ontology, dropout=0.5):
    super(OntLayer, self).__init__(cio, cio)
    self.pre = nn.Sequential(nn.LayerNorm(cio), nn.GELU())
    self.mask = ontology
    self.post = nn.Dropout(dropout)
    print('#OntologyLayer:', cio, cio)


  def forward(self, x):
    #xx = self.post(nn.functional.linear(self.pre(x), self.weight * self.mask.cuda(), self.bias))
    xx = self.post(nn.functional.linear(self.pre(x), self.weight * self.mask, self.bias))
    return x + xx

class OntBlock(nn.Module):
  def __init__(self, cio, ontology, depth, dropout=0.5):
    super(OntBlock, self).__init__()
    layers = [OntLayer(cio, ontology, dropout=dropout) for i in range(depth)]
    self.block = nn.Sequential(*layers)

  def forward(self, x):
    return self.block(x)


class ONN4ARG(nn.Module):
  def __init__(self, mode, size_seq, size_prof, size_out, ontology, dropout=0.5):
    super(ONN4ARG, self).__init__()
    self.mode = mode
    if self.mode//10%10: width, depth = 1024, 4
    else: width, depth = 512, 1

    # sequence to feature
    self.embed0 = nn.Sequential(
        FeatLayer(size_seq[0]*size_seq[1], width),
        ResBlock(width, depth, dropout=dropout))

    # profile to feature
    if self.mode//100%10:
      self.embed1 = nn.Sequential(
          FeatLayer(size_prof[0]*size_prof[1], width),
          ResBlock(width, depth, dropout=dropout))
      self.compress = nn.Sequential(
          CompLayer(width*2, width),
          ResBlock(width, depth, dropout=dropout))
    else:
      self.compress = nn.Sequential(
          CompLayer(width, width),
          ResBlock(width, depth, dropout=dropout))

    if self.mode%10:
      # with ontology
      self.head = nn.Sequential(
          CompLayer(width, size_out),
          OntBlock(size_out, ontology, depth, dropout=dropout))
    else:
      # without ontology
      self.head = nn.Sequential(
          CompLayer(width, size_out))

  def forward(self, x0, x1):
    xx = self.embed0(x0)
    if self.mode//100%10: xx = self.compress(pt.cat((xx, self.embed1(x1)), axis=-1))
    else: xx = self.compress(xx)
    xx = self.head(xx)
    return xx


def loadTree():
  with h5py.File('../data/tree.hdf5', 'r') as f:
    label0to1 = f['label0to1'][()] > 0
    label1to2 = f['label1to2'][()] > 0
    label2to3 = f['label2to3'][()] > 0
  size = [len(label0to1), len(label1to2), len(label2to3), len(label2to3[0])]
  tree = [[None, None, None, None], [None, None, None, None], [None, None, None, None], [None, None, None, None]]
  tree[0][0] = np.zeros((size[0], size[0]), dtype=np.bool)
  tree[0][1] = np.ones((size[0], size[1]), dtype=np.bool)
  tree[0][2] = np.zeros((size[0], size[2]), dtype=np.bool)
  tree[0][3] = np.zeros((size[0], size[3]), dtype=np.bool)
  tree[0] = np.concatenate(tree[0], axis=1)
  tree[1][0] = np.zeros((size[1], size[0]), dtype=np.bool)
  tree[1][1] = np.zeros((size[1], size[1]), dtype=np.bool)
  tree[1][2] = label1to2
  tree[1][3] = np.zeros((size[1], size[3]), dtype=np.bool)
  tree[1] = np.concatenate(tree[1], axis=1)
  tree[2][0] = np.zeros((size[2], size[0]), dtype=np.bool)
  tree[2][1] = np.zeros((size[2], size[1]), dtype=np.bool)
  tree[2][2] = np.zeros((size[2], size[2]), dtype=np.bool)
  tree[2][3] = label2to3
  tree[2] = np.concatenate(tree[2], axis=1)
  tree[3][0] = np.zeros((size[3], size[0]), dtype=np.bool)
  tree[3][1] = np.zeros((size[3], size[1]), dtype=np.bool)
  tree[3][2] = np.zeros((size[3], size[2]), dtype=np.bool)
  tree[3][3] = np.zeros((size[3], size[3]), dtype=np.bool)
  tree[3] = np.concatenate(tree[3], axis=1)
  tree = np.concatenate(tree, axis=0)
  return tree


def augment(chk, seq, prof, label, mask):
  aug_seq, aug_prof, aug_label = [], [], []
  for m in mask:
    tmp_seq, tmp_prof, tmp_label = np.copy(seq), prof, label
    tmp_seq[chk > m] = 0
    idx = np.any(tmp_seq.reshape((len(tmp_seq), -1)) > 0, axis=-1)  # remove data with no input signals
    aug_seq.append(tmp_seq[idx])
    aug_prof.append(tmp_prof[idx])
    aug_label.append(tmp_label[idx])
  return aug_seq, aug_prof, aug_label

