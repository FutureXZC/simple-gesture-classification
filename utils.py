import logging
from logging import handlers

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchmetrics import Accuracy, Recall, Precision


class Logger(object):
    """Print logs to the console, record logs to log.txt file.

    Attributes:
        filename: Log file name.
        level: Log level.
        when: The time interval.
        backupCount: Number of retained backup files.
        fmt: Log format.
    
    """
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }

    def __init__(self,
                 filename='./log/log.txt',
                 level='info',
                 when='D',
                 backupCount=3,
                 fmt='%(asctime)s %(levelname)s: %(message)s'):
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)
        self.logger.setLevel(self.level_relations.get(level))
        sh = logging.StreamHandler()
        sh.setFormatter(format_str)
        th = handlers.TimedRotatingFileHandler(filename=filename, when=when, backupCount=backupCount, encoding='utf-8')
        th.setFormatter(format_str)
        self.logger.addHandler(sh)
        self.logger.addHandler(th)


class MetricFactory():
    """Metrics factory.

    Contains Accuracy(ACC), Nearest Neighbor(NN), First Tier(FT), Second Tier(ST),
    E-Measure(E), Discounted Cumulated Gain(DCG) and Mean Average Precision(mAP).

    """
    def __init__(self, classes, device):
        self.metrics = {
            'ACC': Accuracy(top_k=1, num_classes=classes).to(device),
            'NN': Precision(top_k=1, average='macro', num_classes=classes).to(device),
            'FT': Recall(top_k=1, average='macro', num_classes=classes).to(device),
            'ST': Recall(top_k=2, average='macro', num_classes=classes).to(device),
        }

    def get(self, m):
        return self.metrics[m].compute().item() * 100

    def update(self, x, y):
        for k, v in self.metrics.items():
            v.update(x, y)

    def compute(self):
        res = dict()
        for k, v in self.metrics.items():
            res[k] = v.compute().item() * 100
        return res

    def reset(self):
        for k, v in self.metrics.items():
            v.reset()


class AverageMeter(object):
    """
    Computes and stores the average and current value
    """
    def __init__(self):
        self.reset()

    def reset(self):
        self.count = 0
        self.sum = 0.0
        self.val = 0.0
        self.avg = 0.0

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count


def regression_loss(x: torch.tensor, y: torch.tensor):
    """Calculate regression loss."""
    x = F.normalize(x, dim=1)
    y = F.normalize(y, dim=1)
    return 2 - 2 * (x * y).sum(dim=-1)


def cross_entropy_loss(x: torch.tensor, y: torch.tensor):
    """Calculate cross entropy loss."""
    criteria = nn.CrossEntropyLoss()
    return criteria(x, y)


def get_euclidean_distance(x: torch.Tensor, y: torch.Tensor):
    """Calculate Euclidean distance"""
    criteria = nn.PairwiseDistance(p=2)
    return criteria(x, y)
