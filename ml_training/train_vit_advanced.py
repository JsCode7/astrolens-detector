import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
import time
from tqdm import tqdm
import os

try:
    import torch_directml
    dml_available = torch_directml.is_available()
except ImportError:
    dml_available = False

def main():
    if dml_available:
        device = torch_directml.device()
        print(f"Using AMD GPU via DirectML: {device}")
    else:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"DirectML not found. Using device: {device}")

    train_transform = transforms.Compose([
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.RandomRotation(90),
        transforms.ColorJitter(contrast=0.4, brightness=0.2),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                             std=[0.229, 0.224, 0.225]),
        transforms.RandomErasing(p=0.4, scale=(0.02, 0.12)),
    ])

    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                             std=[0.229, 0.224, 0.225])
    ])

    base_dir = "dataset"
    if not os.path.exists(base_dir):
        print(f"Error: {base_dir} not found. Please run generate_dataset_disk.py first.")
        return

    train_dataset = datasets.ImageFolder(os.path.join(base_dir, 'train'), transform=train_transform)
    val_dataset = datasets.ImageFolder(os.path.join(base_dir, 'val'), transform=val_transform)

    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False, num_workers=0)

    print("Initializing ResNet18 model with Pretrained Weights...")
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    model.fc = nn.Linear(model.fc.in_features, 2)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    
    optimizer = optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)
    
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=2)

    epochs = 30
    best_acc = 0.0

    print("Starting Advanced Training Loop...")
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        
        for inputs, labels in tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs} [Train]"):
            inputs, labels = inputs.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for inputs, labels in tqdm(val_loader, desc=f"Epoch {epoch+1}/{epochs} [Val]"):
                inputs, labels = inputs.to(device), labels.to(device)
                
                outputs = model(inputs)
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

        val_acc = 100 * correct / total
        avg_loss = running_loss / len(train_loader)
        print(f"Epoch [{epoch+1}/{epochs}] - Loss: {avg_loss:.4f} - Val Accuracy: {val_acc:.2f}%")
        
        scheduler.step(val_acc)

        epoch_model_name = f"lens_epoch_{epoch+1}_acc_{val_acc:.2f}.pth"
        torch.save(model.state_dict(), epoch_model_name)

        if val_acc > best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), "lens_real_weights_best.pth")
            print(f"*** New BEST model saved as lens_real_weights_best.pth with {best_acc:.2f}% accuracy! ***")

if __name__ == "__main__":
    main()
