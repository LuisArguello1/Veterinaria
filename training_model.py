import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
import os

# =====================
# CONFIGURACIÓN MEJORADA
# =====================
DATA_DIR = "dataset"   # Ruta a tu dataset organizado en carpetas
BATCH_SIZE = 16        # Aumentado para mejor aprendizaje
EPOCHS = 25            # Más épocas para mejor convergencia
LR = 0.0005           # Learning rate más conservador
NUM_CLASSES = 3        # delgado, normal, obeso
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print(f"🎯 Usando dispositivo: {DEVICE}")
print(f"📊 Configuración: Batch={BATCH_SIZE}, Epochs={EPOCHS}, LR={LR}")

# =====================
# TRANSFORMACIONES MEJORADAS
# =====================
transform = {
    "train": transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.RandomGrayscale(p=0.1),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ]),
    "val": transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.CenterCrop(224),
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

print("Clases detectadas:", train_dataset.classes)  # ['delgado', 'normal', 'obeso']

# =====================
# MODELO PRE-ENTRENADO MEJORADO
# =====================
model = models.resnet50(pretrained=True)  # ResNet50 para mayor capacidad

# Congelar las primeras capas para transfer learning
for param in model.parameters():
    param.requires_grad = False

# Descongelar las últimas capas para fine-tuning
for param in model.layer4.parameters():
    param.requires_grad = True

# Modificar el clasificador final con dropout
model.fc = nn.Sequential(
    nn.Dropout(0.5),
    nn.Linear(model.fc.in_features, 512),
    nn.ReLU(),
    nn.Dropout(0.3),
    nn.Linear(512, NUM_CLASSES)
)

model = model.to(DEVICE)

# =====================
# OPTIMIZADOR Y CRITERIO MEJORADOS
# =====================
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LR, weight_decay=1e-4)
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)

# =====================
# LOOP DE ENTRENAMIENTO MEJORADO
# =====================
best_val_acc = 0.0
train_losses, train_accs = [], []
val_losses, val_accs = [], []

print("\n🚀 Iniciando entrenamiento...")
print("="*60)

for epoch in range(EPOCHS):
    print(f"\n📅 Epoch {epoch+1}/{EPOCHS}")
    print("-" * 30)
    
    # =====================
    # FASE DE ENTRENAMIENTO
    # =====================
    model.train()
    running_loss, running_corrects = 0.0, 0
    total_samples = 0

    for batch_idx, (inputs, labels) in enumerate(train_loader):
        inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)

        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        _, preds = torch.max(outputs, 1)
        running_loss += loss.item() * inputs.size(0)
        running_corrects += torch.sum(preds == labels.data)
        total_samples += inputs.size(0)
        
        # Progreso cada 10 batches
        if (batch_idx + 1) % 10 == 0:
            current_acc = running_corrects.double() / total_samples
            print(f"  Batch {batch_idx+1}/{len(train_loader)} - Loss: {loss.item():.4f} - Acc: {current_acc:.4f}")

    epoch_loss = running_loss / len(train_dataset)
    epoch_acc = running_corrects.double() / len(train_dataset)
    train_losses.append(epoch_loss)
    train_accs.append(epoch_acc.item())

    # =====================
    # FASE DE VALIDACIÓN
    # =====================
    model.eval()
    val_loss, val_corrects = 0.0, 0
    class_correct = [0] * NUM_CLASSES
    class_total = [0] * NUM_CLASSES
    
    with torch.no_grad():
        for inputs, labels in val_loader:
            inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
            outputs = model(inputs)
            loss = criterion(outputs, labels)

            _, preds = torch.max(outputs, 1)
            val_loss += loss.item() * inputs.size(0)
            val_corrects += torch.sum(preds == labels.data)
            
            # Estadísticas por clase
            for i in range(labels.size(0)):
                label = labels[i].item()
                class_correct[label] += (preds[i] == labels[i]).item()
                class_total[label] += 1

    val_loss /= len(val_dataset)
    val_acc = val_corrects.double() / len(val_dataset)
    val_losses.append(val_loss)
    val_accs.append(val_acc.item())
    
    # Actualizar learning rate
    scheduler.step()
    
    # Mostrar resultados del epoch
    print(f"\n📊 Resultados Epoch {epoch+1}:")
    print(f"   🔹 Train Loss: {epoch_loss:.4f} | Train Acc: {epoch_acc:.4f}")
    print(f"   🔸 Val Loss: {val_loss:.4f}   | Val Acc: {val_acc:.4f}")
    
    # Accuracy por clase
    print("   📈 Accuracy por clase:")
    for i, class_name in enumerate(['delgado', 'normal', 'obeso']):
        if class_total[i] > 0:
            class_acc = class_correct[i] / class_total[i]
            print(f"      {class_name:8}: {class_acc:.4f} ({class_correct[i]}/{class_total[i]})")
    
    # Guardar mejor modelo
    if val_acc > best_val_acc:
        best_val_acc = val_acc
        torch.save(model.state_dict(), "best_dog_body_condition_classifier.pth")
        print(f"   ⭐ Nuevo mejor modelo guardado! Val Acc: {best_val_acc:.4f}")
    
    print("="*60)

# =====================
# GUARDAR MODELO FINAL Y ESTADÍSTICAS
# =====================
torch.save(model.state_dict(), "dog_body_condition_classifier.pth")
print(f"\n🎉 Entrenamiento completado!")
print(f"📁 Modelo final guardado como: dog_body_condition_classifier.pth")
print(f"⭐ Mejor modelo guardado como: best_dog_body_condition_classifier.pth")
print(f"🏆 Mejor accuracy de validación: {best_val_acc:.4f}")

# Mostrar evolución del entrenamiento
print(f"\n📈 Evolución del entrenamiento:")
print(f"   Accuracy inicial: Train={train_accs[0]:.4f}, Val={val_accs[0]:.4f}")
print(f"   Accuracy final:   Train={train_accs[-1]:.4f}, Val={val_accs[-1]:.4f}")
print(f"   Mejora total:     Train={train_accs[-1]-train_accs[0]:.4f}, Val={val_accs[-1]-val_accs[0]:.4f}")

print("\n✅ ¡Listo para usar el modelo para predicciones!")