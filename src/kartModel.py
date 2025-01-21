import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
import torch.optim as optim

class KartPositioningModel(nn.Module):
    def __init__(self, embedding_dim=128):
        super(KartPositioningModel, self).__init__()
        # Utiliser ResNet-18 comme backbone
        resnet = models.resnet18(pretrained=True)
        self.feature_extractor = nn.Sequential(*list(resnet.children())[:-1])  # Extraire les caractéristiques sans la dernière couche
        self.fc_embed = nn.Linear(resnet.fc.in_features, embedding_dim)  # Couche d'embedding
        self.fc_coord = nn.Sequential(  # Prédiction des coordonnées
            nn.Linear(embedding_dim, 1024),
            nn.ReLU(),
            nn.Linear(1024, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 2)  # Sortie : longitude et latitude
        )

    def forward(self, x):
        # Extraire les caractéristiques
        features = self.feature_extractor(x)
        features = features.view(features.size(0), -1)  # Applatir les dimensions
        embedding = F.normalize(self.fc_embed(features), p=2, dim=1)  # Normalisation L2
        coords = self.fc_coord(embedding)  # Prédire les coordonnées
        return embedding, coords


class TripletLoss(nn.Module):
    def __init__(self, margin=1.0):
        super(TripletLoss, self).__init__()
        self.margin = margin

    def forward(self, anchor, positive, negative):
        # Distance entre paires positives et négatives
        pos_dist = F.pairwise_distance(anchor, positive, p=2)
        neg_dist = F.pairwise_distance(anchor, negative, p=2)
        # Calcul de la triplet loss
        loss = F.relu(pos_dist - neg_dist + self.margin)
        return loss.mean()


def train_model(model, dataloader, optimizer, triplet_criterion, coord_criterion, num_epochs=10, device='cuda'):
    model.to(device)
    for epoch in range(num_epochs):
        model.train()
        total_loss = 0.0

        for batch in dataloader:
            # Chargement des données
            anchor, positive, negative, target_coords = batch
            anchor = anchor.to(device)
            positive = positive.to(device)
            negative = negative.to(device)
            target_coords = target_coords.to(device)

            optimizer.zero_grad()

            # Passer les données dans le modèle
            anchor_embed, pred_coords = model(anchor)
            positive_embed, _ = model(positive)
            negative_embed, _ = model(negative)

            # Calcul des pertes
            triplet_loss = triplet_criterion(anchor_embed, positive_embed, negative_embed)
            coord_loss = coord_criterion(pred_coords, target_coords)

            # Combiner les pertes
            loss = triplet_loss + coord_loss
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print(f"Epoch [{epoch + 1}/{num_epochs}], Loss: {total_loss / len(dataloader):.4f}")


if __name__ == "__main__":
    # Hyperparamètres
    embedding_dim = 128
    learning_rate = 1e-4
    margin = 1.0
    num_epochs = 10

    # Création du modèle, de la loss et de l'optimiseur
    model = KartPositioningModel(embedding_dim=embedding_dim)
    triplet_criterion = TripletLoss(margin=margin)
    coord_criterion = nn.MSELoss()  # Perte pour les coordonnées
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # Exemple de DataLoader (à remplacer par un vrai DataLoader)
    # DataLoader doit retourner (anchor, positive, negative, target_coords)
    # Exemple fictif :
    # dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

    dataloader = ...  # Définissez votre DataLoader ici

    # Entraînement du modèle
    train_model(model, dataloader, optimizer, triplet_criterion, coord_criterion, num_epochs=num_epochs)
