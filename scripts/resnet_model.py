import torch
from torchvision import models
import torch.nn as nn


class Net(nn.Module):
    def __init__(self):
        super().__init__()
        # Use a pretrained model
        self.network = models.resnet50(pretrained=True)
        # Replace last layer
        num_ftrs = self.network.fc.in_features
        self.network.fc = nn.Linear(num_ftrs, 6)

    def forward(self, xb):
        return torch.sigmoid(self.network(xb))