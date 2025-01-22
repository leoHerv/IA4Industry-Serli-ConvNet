import torch
from torch.utils.data import DataLoader, random_split
import torch.nn as nn
import torchvision.models as models
import torch.optim as optim

from dataset.dataset import MyDataset

BATCH_SIZE = 32

dataset = MyDataset(csv_file='csv', root_dir='./compactedDataSet')

total_size = len(dataset)
train_size = int(0.70 * total_size)
val_size   = int(0.15 * total_size)
test_size  = total_size - train_size - val_size

train_dataset, val_dataset, test_dataset = random_split(
    dataset,
    [train_size, val_size, test_size]
)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
val_loader   = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)
test_loader  = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)


class KartResNet50(nn.Module):
    def __init__(self, pretrained=True):
        super(KartResNet50, self).__init__()

        self.backbone = models.resnet50(weights=models.ResNet50_Weights.DEFAULT if pretrained else None)

        # remove top
        self.backbone.fc = nn.Identity()

        # freeze
        for param in self.backbone.parameters():
            param.requires_grad = False

        self.fc = nn.Sequential(
            nn.Linear(2048, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, 2)
        )

    def forward(self, x):
        features = self.backbone(x)
        out = self.fc(features)
        return out


model = KartResNet50(pretrained=True)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

criterion = nn.MSELoss() # TODO: correct loss function
optimizer = optim.Adam(model.fc.parameters(), lr=1e-3)


num_epochs = 10

for epoch in range(num_epochs):
    model.train()
    running_train_loss = 0.0
    for images, labels in train_loader:
        images = images.to(device)
        labels = labels.to(device)

        outputs = model(images)
        loss = criterion(outputs, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        running_train_loss += loss.item() * images.size(0)

    epoch_train_loss = running_train_loss / len(train_loader.dataset)

    model.eval()
    running_val_loss = 0.0
    with torch.no_grad():
        for images, labels in val_loader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)
            running_val_loss += loss.item() * images.size(0)

    epoch_val_loss = running_val_loss / len(val_loader.dataset)

    print(f'Epoch [{epoch+1}/{num_epochs}] '
          f'Train Loss: {epoch_train_loss:.4f} | '
          f'Val Loss: {epoch_val_loss:.4f}')


model.eval()
running_test_loss = 0.0
with torch.no_grad():
    for images, labels in test_loader:
        images = images.to(device)
        labels = labels.to(device)

        outputs = model(images)
        loss = criterion(outputs, labels)
        running_test_loss += loss.item() * images.size(0)

epoch_test_loss = running_test_loss / len(test_loader.dataset)

print(f'Test Loss: {epoch_test_loss:.4f}')
