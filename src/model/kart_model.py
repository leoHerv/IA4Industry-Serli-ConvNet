import torch
from torch.utils.data import DataLoader, random_split
import torch.nn as nn
import torchvision.models as models
import torch.optim as optim
import torchvision.transforms as T


from src.dataset.dataset import MyDataset

BATCH_SIZE = 32

transform = T.Compose([
    T.Resize((224, 224)),  # typical input size for ResNet
    T.ToTensor(),
])

dataset = MyDataset(csv_file='dataset.csv', root_dir='./resizeDataSet', transform=transform)

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

def threshold_accuracy(outputs, labels, threshold=0.1):
    distances = torch.norm(outputs - labels, dim=1)  # shape: [batch_size]

    # Count how many are below threshold
    correct = (distances < threshold).float().sum()

    # Return average over the batch
    return correct / outputs.size(0)

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
            nn.Linear(2048, 1024),
            nn.ReLU(),
            nn.Linear(1024, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            # nn.Dropout(0.5),
            nn.Linear(64, 2)
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


num_epochs = 20

for epoch in range(num_epochs):
    model.train()
    running_train_loss = 0.0
    correct_train = 0
    running_acc = 0
    running_train_mae = 0.0

    for images, labels in train_loader:
        images = images.to(device)
        labels = labels.to(device)

        outputs = model(images)
        loss = criterion(outputs, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        running_train_loss += loss.item() * images.size(0)

        acc = threshold_accuracy(outputs, labels, threshold=0.1)
        running_acc += acc.item() * images.size(0)

        batch_mae = torch.mean(torch.abs(outputs - labels), dim=1)
        running_train_mae += batch_mae.sum().item()

    epoch_train_loss = running_train_loss / len(train_loader.dataset)
    epoch_acc = running_acc / len(train_loader.dataset)
    epoch_train_mae = running_train_mae / len(train_loader.dataset)



    model.eval()
    running_val_loss = 0.0
    running_val_acc = 0
    running_val_mae = 0.0
    with torch.no_grad():
        for images, labels in val_loader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)
            running_val_loss += loss.item() * images.size(0)

            acc = threshold_accuracy(outputs, labels, threshold=0.1)
            running_val_acc += acc.item() * images.size(0)

            batch_mae = torch.mean(torch.abs(outputs - labels), dim=1)
            running_val_mae += batch_mae.sum().item()

    epoch_val_loss = running_val_loss / len(val_loader.dataset)
    epoch_val_acc = running_val_acc / len(val_loader.dataset)
    epoch_val_mae = running_val_mae / len(val_loader.dataset)



    print(f'Epoch [{epoch+1}/{num_epochs}] '
          f'Train Loss: {epoch_train_loss:.4f} | Train MAE: {epoch_train_mae:.4f} '
          f'Val Loss: {epoch_val_loss:.4f} | Val MAE: {epoch_val_mae:.4f}')


dummy_input = torch.randn(1, 3, 224, 224, device=device)

onnx_model_path = "kart_resnet50.onnx"

torch.onnx.export(
    model,                      # Model to be exported
    dummy_input,                # Example input tensor
    onnx_model_path,            # Path to save the ONNX model
    export_params=True,         # Store the trained parameter weights inside the model file
    opset_version=12,           # The ONNX version to export the model to
    do_constant_folding=True,   # Whether to execute constant folding for optimization
    input_names=['input'],      # The model's input names
    output_names=['output'],    # The model's output names
    dynamic_axes={
        'input': {0: 'batch_size'},   # Variable batch size
        'output': {0: 'batch_size'}
    }
)

print(f"Model has been exported to {onnx_model_path}")

model.eval()
running_test_loss = 0.0
acc_test = 0
running_test_mae = 0.0
with torch.no_grad():
    for images, labels in test_loader:
        images = images.to(device)
        labels = labels.to(device)

        outputs = model(images)
        loss = criterion(outputs, labels)
        running_test_loss += loss.item() * images.size(0)

        acc = threshold_accuracy(outputs, labels, threshold=0.1)
        running_val_acc += acc.item() * images.size(0)

        batch_mae = torch.mean(torch.abs(outputs - labels), dim=1)
        running_test_mae += batch_mae.sum().item()

epoch_test_loss = running_test_loss / len(test_loader.dataset)
acc_test = running_val_acc / len(test_loader.dataset)
epoch_test_mae = running_test_mae / len(test_loader.dataset)


print(f'Test Loss: {epoch_test_loss:.4f} | Test MAE: {epoch_test_mae:.4f}')

