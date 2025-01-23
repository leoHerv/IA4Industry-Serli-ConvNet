import torch
from torch.utils.data import DataLoader, random_split
import torch.nn as nn
import torchvision.models as models
import torch.optim as optim
import torchvision.transforms as T
import copy
from codecarbon import EmissionsTracker

from src.dataset.dataset import MyDataset

tracker = EmissionsTracker()
tracker.start()


BATCH_SIZE = 32

transform = T.Compose([
    T.Resize((600, 600)),
    T.ToTensor(),
])

dataset = MyDataset(csv_file='dataset.csv', root_dir='./resizeDataSet', transform=transform)

total_size = len(dataset)
train_size = int(0.70 * total_size)
val_size   = total_size - train_size
# val_size   = int(0.15 * total_size)
# test_size  = total_size - train_size - val_size

train_dataset, val_dataset = random_split(
    dataset,
    [train_size, val_size]
)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
val_loader   = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)
# test_loader  = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

class KartResNet50(nn.Module):
    def __init__(self, pretrained=True):
        super(KartResNet50, self).__init__()

        # self.backbone = models.resnet50(weights=models.ResNet50_Weights.DEFAULT if pretrained else None)
        self.backbone = models.efficientnet_b7(weights=models.EfficientNet_B7_Weights.DEFAULT)

        # remove top
        self.backbone.classifier = nn.Identity()

        # freeze
        for param in self.backbone.parameters():
            param.requires_grad = False

        self.classifier = nn.Sequential(
            nn.Linear(2560, 1024),
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
        out = self.classifier(features)
        return out


model = KartResNet50(pretrained=True)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

# criterion = nn.MSELoss()
criterion = nn.L1Loss()
optimizer = optim.Adam(model.classifier.parameters(), lr=1e-2)


num_epochs = 50
patience = 5

best_val_loss = float('inf')
epochs_no_improve = 0

best_model_weights = copy.deepcopy(model.state_dict())

best_model_path = "best_model.pth"

for epoch in range(num_epochs):
    model.train()
    running_train_loss = 0.0
    correct_train = 0
    running_train_mse = 0.0

    for images, labels in train_loader:
        images = images.to(device)
        labels = labels.to(device)

        outputs = model(images)
        loss = criterion(outputs, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        running_train_loss += loss.item() * images.size(0)


        batch_mse = torch.mean((outputs - labels) ** 2, dim=1)
        running_train_mse += batch_mse.sum().item()

    epoch_train_loss = running_train_loss / len(train_loader.dataset)
    epoch_train_mse = running_train_mse / len(train_loader.dataset)


    model.eval()
    running_val_loss = 0.0
    running_val_mse = 0.0
    with torch.no_grad():
        for images, labels in val_loader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)
            running_val_loss += loss.item() * images.size(0)


            batch_mse = torch.mean((outputs - labels) ** 2, dim=1)
            running_val_mse += batch_mse.sum().item()

    epoch_val_loss = running_val_loss / len(val_loader.dataset)
    epoch_val_mse = running_val_mse / len(val_loader.dataset)



    print(f'Epoch [{epoch+1}/{num_epochs}] '
          f'Train Loss: {epoch_train_loss:.4f} | Train MAE: {epoch_train_mse:.4f} '
          f'Val Loss: {epoch_val_loss:.4f} | Val MAE: {epoch_val_mse:.4f}')
    
    if epoch_val_loss < best_val_loss:
        best_val_loss = epoch_val_loss
        epochs_no_improve = 0
        
        best_model_weights = copy.deepcopy(model.state_dict())

        torch.save(model.state_dict(), best_model_path)
        print(f"  --> New best model saved at epoch {epoch+1} with val_loss = {best_val_loss:.4f}")
    else:
        epochs_no_improve += 1

    if epochs_no_improve >= patience:
        print(f"Early stopping triggered after {epoch+1} epochs!")
        break

tracker.stop()

model.load_state_dict(best_model_weights)

dummy_input = torch.randn(1, 3, 600, 600, device=device)

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

# model.eval()
# running_test_loss = 0.0
# running_test_mae = 0.0
# with torch.no_grad():
#     for images, labels in test_loader:
#         images = images.to(device)
#         labels = labels.to(device)

#         outputs = model(images)
#         loss = criterion(outputs, labels)
#         running_test_loss += loss.item() * images.size(0)


#         batch_mae = torch.mean(torch.abs(outputs - labels), dim=1)
#         running_test_mae += batch_mae.sum().item()

# epoch_test_loss = running_test_loss / len(test_loader.dataset)
# epoch_test_mae = running_test_mae / len(test_loader.dataset)


# print(f'Test Loss: {epoch_test_loss:.4f} | Test MAE: {epoch_test_mae:.4f}')

