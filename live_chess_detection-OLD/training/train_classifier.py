"""Training script for piece classifier on synthetic data."""

import argparse
import yaml
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from tqdm import tqdm
import mlflow

from models.piece_classifier import PieceClassifierNet
from datasets.multi_source_loader import MultiSourceChessDataset
from training.amd_utils import setup_amd_device


def train_epoch(model, loader, criterion, optimizer, device):
    """Train for one epoch."""
    model.train()
    total_loss = 0
    correct = 0
    total = 0
    
    pbar = tqdm(loader, desc="Training")
    for batch_idx, (images, labels) in enumerate(pbar):
        images = images.to(device)
        labels = labels.to(device)
        
        # Forward pass
        outputs = model(images)
        loss = criterion(outputs, labels)
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        # Statistics
        total_loss += loss.item()
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()
        
        # Update progress bar
        pbar.set_postfix({
            'loss': f'{loss.item():.4f}',
            'acc': f'{100.*correct/total:.2f}%'
        })
    
    avg_loss = total_loss / len(loader)
    accuracy = 100. * correct / total
    return avg_loss, accuracy


def validate(model, loader, criterion, device):
    """Validate model."""
    model.eval()
    total_loss = 0
    correct = 0
    total = 0
    
    with torch.no_grad():
        for images, labels in tqdm(loader, desc="Validation"):
            images = images.to(device)
            labels = labels.to(device)
            
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            total_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
    
    avg_loss = total_loss / len(loader)
    accuracy = 100. * correct / total
    return avg_loss, accuracy


def train_piece_classifier(config_path='config/amd_training.yaml'):
    """Main training function."""
    # Load config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Setup device
    device = setup_amd_device()
    
    # Create model
    model = PieceClassifierNet(input_dim=64, num_classes=13)
    model = model.to(device)
    
    # Load datasets
    print("📦 Loading datasets...")
    # TODO: Load actual dataset config
    train_dataset = None  # Placeholder
    val_dataset = None  # Placeholder
    
    # Create dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=config['memory']['rx7900xtx']['classifier_batch'],
        shuffle=True,
        num_workers=config['memory']['rx7900xtx']['num_workers']
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=config['memory']['rx7900xtx']['classifier_batch'],
        shuffle=False,
        num_workers=config['memory']['rx7900xtx']['num_workers']
    )
    
    # Setup training
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(
        model.parameters(),
        lr=config['optimizer']['classifier']['lr']
    )
    
    # Training loop
    num_epochs = config['epochs']['classifier']
    best_acc = 0
    
    mlflow.set_experiment("PieceClassifier")
    with mlflow.start_run():
        mlflow.log_params(config)
        
        for epoch in range(num_epochs):
            print(f"\nEpoch {epoch+1}/{num_epochs}")
            
            train_loss, train_acc = train_epoch(
                model, train_loader, criterion, optimizer, device
            )
            val_loss, val_acc = validate(
                model, val_loader, criterion, device
            )
            
            # Log metrics
            mlflow.log_metrics({
                'train_loss': train_loss,
                'train_acc': train_acc,
                'val_loss': val_loss,
                'val_acc': val_acc,
            }, step=epoch)
            
            # Save best model
            if val_acc > best_acc:
                best_acc = val_acc
                torch.save({
                    'epoch': epoch,
                    'model_state_dict': model.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                    'val_acc': val_acc,
                }, 'models/classifier_best.pth')
                print(f"✅ Saved new best model (acc: {val_acc:.2f}%)")
    
    print(f"\n🎉 Training complete! Best val accuracy: {best_acc:.2f}%")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='config/amd_training.yaml')
    parser.add_argument('--device', default='rocm', choices=['rocm', 'cuda', 'cpu'])
    args = parser.parse_args()
    
    train_piece_classifier(args.config)
