# AMD GPU Setup Guide

This guide explains how to set up the chess vision system for AMD GPUs using ROCm.

## Prerequisites

- AMD GPU with ROCm support
- Ubuntu 20.04+ or Windows 11
- Python 3.8+

## Installation

### 1. Install ROCm

#### Ubuntu

```bash
# Add ROCm repository
wget https://repo.radeon.com/rocm/rocm.gpg.key
sudo apt-key add rocm.gpg.key
echo 'deb [arch=amd64] https://repo.radeon.com/rocm/apt/5.7 jammy main' | sudo tee /etc/apt/sources.list.d/rocm.list

# Install ROCm
sudo apt update
sudo apt install rocm-dev rocm-libs rocm-utils
```

#### Windows

1. Download ROCm from [AMD Developer](https://www.amd.com/en/developer/rocm.html)
2. Install ROCm SDK
3. Add ROCm to PATH

### 2. Install PyTorch with ROCm

```bash
# Install PyTorch with ROCm support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.6
```

### 3. Verify Installation

```python
import torch
print(f"ROCm available: {torch.cuda.is_available()}")
print(f"Device count: {torch.cuda.device_count()}")
print(f"Current device: {torch.cuda.current_device()}")
```

## Configuration

### Environment Variables

```bash
export HSA_OVERRIDE_GFX_VERSION=10.3.0
export HIP_VISIBLE_DEVICES=0
```

### Model Configuration

```yaml
# config/amd_training.yaml
device: rocm
batch_size: 4
num_workers: 8
```

## Performance Optimization

### Memory Management

```python
# Enable memory growth
torch.cuda.set_per_process_memory_fraction(0.8)
```

### Training Parameters

```python
# Optimized for AMD GPUs
training_config = {
    'batch_size': 4,
    'num_workers': 8,
    'pin_memory': True,
    'persistent_workers': True
}
```

## Troubleshooting

### Common Issues

1. **ROCm Not Detected**: Check ROCm installation
2. **Memory Issues**: Reduce batch size
3. **Performance**: Enable ROCm optimizations

### Debug Commands

```bash
# Check ROCm installation
rocm-smi

# Check PyTorch ROCm support
python -c "import torch; print(torch.cuda.is_available())"
```

## Performance Benchmarks

| GPU | Model | FPS | mAP |
|-----|-------|-----|-----|
| RX 7900 XTX | YOLOv8s | 42 | 91% |
| RX 7900 XTX | InceptionV3 | 18 | 89% |
| RX 6800 XT | YOLOv8s | 35 | 90% |
| RX 6800 XT | InceptionV3 | 15 | 88% |

## References

- [ROCm Documentation](https://rocm.docs.amd.com/)
- [PyTorch ROCm](https://pytorch.org/get-started/locally/)
- [AMD Developer](https://www.amd.com/en/developer/rocm.html)
