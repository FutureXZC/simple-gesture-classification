import os
from pathlib import Path
import time

import torch
from tensorboardX import SummaryWriter
import torchvision.transforms as transforms

from dataset import *
from model import ResNet
from utils import *

BATCH_SIZE = 128
EPOCH = 80
log = Logger('log.txt')


class ShapeRecognitionTrainer:
    """Implementation of the training process.

    Attributes:
        classes: Total classes.

    """
    def __init__(self, classes: int) -> None:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.backbone = ResNet(num_class=classes).to(device)
        self.backbone = torch.nn.DataParallel(self.backbone, device_ids=[0, 1])
        self.optimizer = torch.optim.SGD(list(self.backbone.parameters()), lr=0.001, weight_decay=1e-4, momentum=0.9)
        self.scheduler = torch.optim.lr_scheduler.StepLR(self.optimizer, step_size=20, gamma=0.1)
        self.device = device
        self.classes = classes
        self.batch_size = BATCH_SIZE
        self.epochs = EPOCH
        self.save_model = True
        self.tb = SummaryWriter(os.path.join('.', 'events'))

    def train(self, num_workers: int = 0):
        """Train the student model.
        
        Args:
            batch_size: Batch size.
            num_workers: How many subprocesses to use for data loading. 0 means that the data will be loaded in the main process.
        
        """
        transform_train = transforms.Compose([
            transforms.RandomChoice([transforms.RandomCrop(224),
                                     transforms.RandomRotation(degrees=(0, 180), fill=255)]),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomVerticalFlip(p=0.5),
            transforms.ToTensor(),
            transforms.Normalize(mean=0.9910072088241577, std=0.07824398577213287),
        ])
        transform_test = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=0.9910072088241577, std=0.07824398577213287),
        ])
        log.logger.info("----- Start loading data -----")
        train_data = SketchDataset(split='train', transform=transform_train)
        test_data = SketchDataset(split='test', transform=transform_test)
        train_loader = DataLoader(dataset=train_data, batch_size=64, shuffle=True, num_workers=num_workers)
        test_loader = DataLoader(dataset=test_data, batch_size=64, shuffle=True, num_workers=num_workers)
        log.logger.info("----- Loading data completed -----")

        max_acc = 99.75
        metrics = MetricFactory(self.classes, self.device)
        log.logger.info("----- Start training -----")
        for epoch in range(self.epochs):
            # train
            loss_rec = AverageMeter()
            start = time.time()
            for batch in train_loader:
                query, label = batch
                query = query.to(self.device)
                label = label.to(self.device)

                loss = self.update(query, label, metrics)
                loss_rec.update(loss, self.batch_size)

                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()

            run_time = time.time() - start
            self.log_record(epoch + 1, run_time, loss_rec.avg, metrics, 'train')

            metrics.reset()

            # test
            with torch.no_grad():
                loss_rec = AverageMeter()
                start = time.time()
                for batch in test_loader:
                    query, label = batch
                    query = query.to(self.device)
                    label = label.to(self.device)

                    loss = self.update(query, label, metrics)
                    loss_rec.update(loss, self.batch_size)

                run_time = time.time() - start

                self.log_record(epoch + 1, run_time, loss_rec.avg, metrics, 'test')

            cur_acc = metrics.get('ACC')
            self.store_model(cur_acc, max_acc, epoch)
            max_acc = max(cur_acc, max_acc)

            metrics.reset()

            self.scheduler.step()

        log.logger.info("Max ACC: {}".format(max_acc))
        log.logger.info("----- Complete the training -----")

    def update(self, query: torch.tensor, label: torch.tensor, metrics: MetricFactory):
        """Update parameters and metrics.

        Args:
            query: Query sketches, tensor shape of b, 1, W, H.
            label: Labels correspond to x, tensor shape of b.
            metrics: ACC, NN, FT, ST.

        """
        predictions, features = self.backbone(query, return_features=True)
        loss = cross_entropy_loss(predictions, label)

        metrics.update(predictions, label)

        return loss

    def log_record(self, epoch: int, run_time, loss: torch.tensor, metrics: MetricFactory, mode: str):
        """Print logs to the console, record logs to log.txt file, record loss and accuracy to tensorboardX.

        Args:
            epoch: Current epoch.
            run_time: Run time of current epoch.
            loss: Total loss = triple loss + classification loss.
            metrics: Accuracy, Recall, Precision.
            mode: 'train' or 'test'.        
        
        """
        m = metrics.compute()
        info = "Epoch-{}: {:03d}/{:03d}\t run_time:{:.4f}\tloss: {:.4f}\tACC:{:.4f}\tNN: {:.4f}\tFT: {:.4f}".format(
            mode, epoch, self.epochs, run_time, loss, m['ACC'], m['NN'], m['FT'])
        if mode == 'test':
            info += '\n'
        log.logger.info(info)
        self.tb.add_scalar(mode + '/loss', loss, epoch)
        self.tb.add_scalar(mode + '/ACC', m['ACC'], epoch)
        self.tb.add_scalar(mode + '/NN', m['NN'], epoch)
        self.tb.add_scalar(mode + '/FT', m['FT'], epoch)

    def store_model(self, acc: float, max_acc: float, epoch: int):
        """Save the model as .pth file.
        
        Args:
            acc: Accuracy of current epoch.
            max_acc: Max accuracy.
            epoch: Current epoch.
        
        """
        if (self.save_model and acc >= max_acc) or (epoch % 20 == 0):
            Path("checkpoints").mkdir(parents=True, exist_ok=True)
            torch.save(
                {
                    'resnet18_state_dict': self.backbone.state_dict(),
                    'optimizer_state_dict': self.optimizer.state_dict(),
                }, os.path.join('.', 'checkpoints',
                                str(epoch) + '_' + str(acc) + '.pth'))


if __name__ == '__main__':
    trainer = ShapeRecognitionTrainer(classes=4)
    trainer.train(num_workers=2)