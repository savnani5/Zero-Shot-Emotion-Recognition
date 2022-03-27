import matplotlib
import matplotlib.pyplot as plt
from matplotlib import gridspec
import numpy as np
from torch.autograd import Variable
import torch


def get_X_batch(data_loader, params, size=None):
    if size is None:
        size = data_loader.batch_size
    for X, target in data_loader:
        break

    train_batch_size = params['train_batch_size']
    X_dim = params['X_dim']
    cuda = params['cuda']

    X = X * 0.3081 + 0.1307

    X = X[:size]
    target = target[:size]

    X.resize_(train_batch_size, X_dim)
    X, target = Variable(X), Variable(target)

    if cuda:
        X, target = X.cuda(), target.cuda()

    return X


def create_reconstruction(Q, P, data_loader, params):
    Q.eval()
    P.eval()
    X = get_X_batch(data_loader, params, size=1)

    z_c, z_g = Q(X)
    z = torch.cat((z_c, z_g), 1)
    x = P(z)

    img_orig = np.array(X[0].data.tolist()).reshape(28, 28)
    img_rec = np.array(x[0].data.tolist()).reshape(28, 28)
    plt.subplot(1, 2, 1)
    plt.imshow(img_orig)
    plt.subplot(1, 2, 2)
    plt.imshow(img_rec)


def grid_plot(Q, P, data_loader, params):
    Q.eval()
    P.eval()
    X = get_X_batch(data_loader, params, size=10)
    _, z_g = Q(X)

    n_classes = params['n_classes']
    cuda = params['cuda']
    z_dim = params['z_dim']

    z_cat = np.arange(0, n_classes)
    z_cat = np.eye(n_classes)[z_cat].astype('float32')
    z_cat = torch.from_numpy(z_cat)
    z_cat = Variable(z_cat)
    if cuda:
        z_cat = z_cat.cuda()

    nx, ny = 5, n_classes
    plt.subplot()
    gs = gridspec.GridSpec(nx, ny, hspace=0.05, wspace=0.05)

    for i, g in enumerate(gs):
        z_gauss = z_g[i / ny].resize(1, z_dim)
        z_gauss0 = z_g[i / ny].resize(1, z_dim)

        for _ in range(n_classes - 1):
            z_gauss = torch.cat((z_gauss, z_gauss0), 0)

        z = torch.cat((z_cat, z_gauss), 1)
        x = P(z)

        ax = plt.subplot(g)
        img = np.array(x[i % ny].data.tolist()).reshape(28, 28)
        ax.imshow(img, )
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_aspect('auto')


def grid_plot2d(Q, P, data_loader, params):
    Q.eval()
    P.eval()

    cuda = params['cuda']

    z1 = Variable(torch.from_numpy(np.arange(-10, 10, 1.5).astype('float32')))
    z2 = Variable(torch.from_numpy(np.arange(-10, 10, 1.5).astype('float32')))
    if cuda:
        z1, z2 = z1.cuda(), z2.cuda()

    nx, ny = len(z1), len(z2)
    plt.subplot()
    gs = gridspec.GridSpec(nx, ny, hspace=0.05, wspace=0.05)

    for i, g in enumerate(gs):
        z = torch.cat((z1[i / ny], z2[i % nx])).resize(1, 2)
        x = P(z)

        ax = plt.subplot(g)
        img = np.array(x.data.tolist()).reshape(28, 28)
        ax.imshow(img, )
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_aspect('auto')