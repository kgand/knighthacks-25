"""InceptionV3 training script."""

import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

from models.detector_inception import create_inception_model, get_inception_transforms
from training.amd_utils import setup_amd_device


def train_inception_detector(
    data_dir='data/recorded_dataset',
    epochs=10,
    batch_size=12,
    device='rocm'
):
    """Train Inception model for piece detection."""
    
    # Setup device
    device = setup_amd_device() if device == 'rocm' else torch.device(device)
    
    # Create model
    model = create_inception_model(num_classes=13, device=device)
    
    # Setup training
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # TODO: Load actual dataset
    print("📦 Loading dataset...")
    # train_loader = ...
    # val_loader = ...
    
    # Training loop
    print(f"🏋️ Starting training for {epochs} epochs")
    for epoch in range(epochs):
        # Training
        model.train()
        print(f"\nEpoch {epoch+1}/{epochs}")
        # TODO: Actual training loop
    
    print("✅ Training complete!")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs', type=int, default=10)
    parser.add_argument('--batch-size', type=int, default=12)
    parser.add_argument('--device', default='rocm')
    
    args = parser.parse_args()
    
    train_inception_detector(
        epochs=args.epochs,
        batch_size=args.batch_size,
        device=args.device
    )


if __name__ == "__main__":
    main()
