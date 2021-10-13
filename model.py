import torch
import torch.nn as nn
from torchvision import models


class ResNet(nn.Module):
    """Student model."""
    def __init__(self, num_class: int) -> None:
        super().__init__()
        backbone = models.resnet18(pretrained=True)
        self.encoder = nn.Sequential(*list(backbone.children())[:-1])
        self.encoder[0] = nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)
        self.cls = nn.Sequential(nn.Linear(512, num_class))

    def forward(self, x: torch.tensor, return_features: bool = False):
        features = self.encoder(x)
        features = features.view(features.shape[0], features.shape[1])
        if return_features:
            return self.cls(features), features
        return self.cls(features)
