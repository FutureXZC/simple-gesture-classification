import os
from pathlib import Path
import time

from caffe2.python.onnx.backend import Caffe2Backend as onnx_caffe2_backend
import numpy as np
import onnx
import torch
from tensorboardX import SummaryWriter
import torchvision.transforms as transforms

from dataset import *
from model import AlexNet, VGG
from utils import *

BATCH_SIZE = 64
EPOCH = 120
log = Logger('log.txt')


class ShapeRecognitionTrainer:
    """Implementation of the training process.

    Attributes:
        classes: Total classes.
        backbone: 'AlexNet' or 'VGG'.

    """
    def __init__(self, num_classes: int, backbone: str = 'AlexNet') -> None:
        device = 'cpu'
        if backbone == 'AlexNet':
            self.backbone = AlexNet(num_classes=num_classes).to(device)
            log.logger.info("----- Use AlexNet as backbone -----")
        else:
            self.backbone = VGG(num_classes=num_classes).to(device)
            log.logger.info("----- Use VGG as backbone -----")
        self.optimizer = torch.optim.Adam(list(self.backbone.parameters()))
        self.scheduler = torch.optim.lr_scheduler.StepLR(self.optimizer, step_size=20, gamma=0.1)
        self.device = device
        self.classes = num_classes
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
            transforms.RandomChoice([transforms.RandomCrop(227),
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

        max_acc = 83
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
        predictions = self.backbone(query)
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
            torch.save({
                'state_dict': self.backbone.state_dict(),
                'optimizer_state_dict': self.optimizer.state_dict(),
            }, os.path.join('.', 'checkpoints', 'best.pth'))

    def convert2onnx(self, use_trained_model=False):
        '''Convert pytorch model to onnx model.
        Args:
            use_trained_model: Whether to use trained best model.

        Output:
            .onnx file.
        
        '''
        log.logger.info("----- Start convert model to onnx -----")
        if use_trained_model:
            pthfile = os.path.join('.', 'checkpoints', 'best.pth')
            loaded_model = torch.load(pthfile)
            self.backbone.load_state_dict(loaded_model['state_dict'])
        # input size
        dummy_input = torch.randn(1, 3, 224, 224)
        torch_out = torch.onnx._export(self.backbone,
                                       dummy_input,
                                       "cls-alexnet.onnx",
                                       export_params=True,
                                       keep_initializers_as_inputs=True,
                                       opset_version=10)
        log.logger.info('torch out: ' + str(torch_out))

        onnx_model = onnx.load("cls-alexnet.onnx")
        prepared_backend = onnx_caffe2_backend.prepare(onnx_model)
        W = {onnx_model.graph.input[0].name: dummy_input.data.numpy()}
        c2_out = prepared_backend.run(W)[0]
        log.logger.info('onnx out: ' + str(c2_out))

        np.testing.assert_almost_equal(torch_out.data.cpu().numpy(), c2_out, decimal=3)


if __name__ == '__main__':
    trainer = ShapeRecognitionTrainer(num_classes=4, backbone='AlexNet')
    trainer.train(num_workers=2)
    trainer.convert2onnx()