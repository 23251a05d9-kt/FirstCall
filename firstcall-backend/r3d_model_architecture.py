import torch
import torch.nn as nn
from torchvision.models.video import r3d_18

class R3DModel(nn.Module):
    def __init__(self, num_classes=4):
        super(R3DModel, self).__init__()

        self.model = r3d_18(pretrained=False)

        # Replace classifier
        self.model.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(self.model.fc.in_features, num_classes)
        )

    def forward(self, x):
        return self.model(x)
