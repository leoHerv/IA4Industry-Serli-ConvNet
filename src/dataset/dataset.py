import os
import csv
from PIL import Image
import torch
from torch.utils.data import Dataset

class MyDataset(Dataset):
    def __init__(self, csv_file, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.samples = []

        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                file_name = row['file_name']
                lat = float(row['lat'])
                lon = float(row['lon'])
                self.samples.append((file_name, lat, lon))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        file_name, label1, label2 = self.samples[idx]
        img_path = os.path.join(self.root_dir, file_name)

        image = Image.open(img_path).convert('RGB')

        if self.transform:
            image = self.transform(image)

        labels = torch.tensor([label1, label2], dtype=torch.float)
        return image, labels

