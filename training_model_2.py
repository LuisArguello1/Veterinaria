import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
import os

# =====================
# CONFIGURACIÓN
# =====================
DATA_DIR = "dataset"   # Ruta a tu dataset organizado en carpetas
BATCH_SIZE = 4
EPOCHS = 3
LR = 0.001
NUM_CLASSES = 4  # puppy, young, adult, senior
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# =====================
# TRANSFORMACIONES
# =====================
transform = {
    "train": transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ]),
    "val": transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ])
}

# =====================
# DATASETS Y DATALOADERS
# =====================
train_dataset = datasets.ImageFolder(os.path.join(DATA_DIR, "train"), transform=transform["train"])
val_dataset = datasets.ImageFolder(os.path.join(DATA_DIR, "val"), transform=transform["val"])

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

print("Clases detectadas:", train_dataset.classes)  # ['adult', 'puppy', 'senior', 'young']

# =====================
# MODELO PRE-ENTRENADO
# =====================
model = models.resnet18(pretrained=True)  # ResNet18 para transfer learning
model.fc = nn.Linear(model.fc.in_features, NUM_CLASSES)  # Ajustamos la última capa
model = model.to(DEVICE)

# =====================
# OPTIMIZADOR Y CRITERIO
# =====================
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LR)

# =====================
# LOOP DE ENTRENAMIENTO
# =====================
for epoch in range(EPOCHS):
    print(f"Epoch {epoch+1}/{EPOCHS}")
    model.train()
    running_loss, running_corrects = 0.0, 0

    for inputs, labels in train_loader:
        inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)

        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        _, preds = torch.max(outputs, 1)
        running_loss += loss.item() * inputs.size(0)
        running_corrects += torch.sum(preds == labels.data)

    epoch_loss = running_loss / len(train_dataset)
    epoch_acc = running_corrects.double() / len(train_dataset)
    print(f"Train Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}")

    # =====================
    # VALIDACIÓN
    # =====================
    model.eval()
    val_loss, val_corrects = 0.0, 0
    with torch.no_grad():
        for inputs, labels in val_loader:
            inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
            outputs = model(inputs)
            loss = criterion(outputs, labels)

            _, preds = torch.max(outputs, 1)
            val_loss += loss.item() * inputs.size(0)
            val_corrects += torch.sum(preds == labels.data)

    val_loss /= len(val_dataset)
    val_acc = val_corrects.double() / len(val_dataset)
    print(f"Val Loss: {val_loss:.4f} Acc: {val_acc:.4f}")

# =====================
# GUARDAR MODELO
# =====================
torch.save(model.state_dict(), "dog_age_classifier.pth")
print("Modelo guardado como dog_age_classifier.pth")