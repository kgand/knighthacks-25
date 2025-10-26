"""Utilities for AMD GPU training with ROCm."""

import os
import torch
import psutil


def setup_amd_device(device_id=0):
    """
    Configure PyTorch for AMD GPU.
    
    Sets environment variables and verifies ROCm availability.
    """
    # Check if CUDA (ROCm) is available
    if not torch.cuda.is_available():
        print("⚠️  ROCm/CUDA not detected, falling back to CPU")
        return 'cpu'
    
    # Set device
    torch.cuda.set_device(device_id)
    device = torch.device(f'cuda:{device_id}')
    
    # Print GPU info
    gpu_name = torch.cuda.get_device_name(device_id)
    gpu_mem = torch.cuda.get_device_properties(device_id).total_memory / 1e9
    
    print(f"🎮 Using GPU: {gpu_name}")
    print(f"💾 GPU Memory: {gpu_mem:.1f} GB")
    
    # Enable optimizations
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.benchmark = True
    
    return device


def get_optimal_batch_size(model, input_size, device, start_batch=32):
    """
    Find optimal batch size by binary search.
    
    Starts with a guess and reduces until it fits in memory.
    Useful for AMD GPUs where optimal batch varies by model.
    """
    model.to(device)
    model.train()
    
    batch_size = start_batch
    
    while batch_size > 1:
        try:
            # Try to run forward and backward pass
            dummy_input = torch.randn(batch_size, 3, *input_size).to(device)
            dummy_target = torch.randint(0, 13, (batch_size,)).to(device)
            
            output = model(dummy_input)
            loss = torch.nn.functional.cross_entropy(output, dummy_target)
            loss.backward()
            
            # Clear cache
            del dummy_input, dummy_target, output, loss
            torch.cuda.empty_cache()
            
            print(f"✅ Batch size {batch_size} fits in memory")
            return batch_size
            
        except RuntimeError as e:
            if "out of memory" in str(e):
                batch_size = batch_size // 2
                torch.cuda.empty_cache()
                print(f"⚠️  OOM with batch size {batch_size*2}, trying {batch_size}")
            else:
                raise e
    
    return 1


def get_system_info():
    """Get system information for logging."""
    info = {
        'cpu_count': psutil.cpu_count(),
        'ram_gb': psutil.virtual_memory().total / 1e9,
        'gpu_available': torch.cuda.is_available(),
    }
    
    if torch.cuda.is_available():
        info['gpu_name'] = torch.cuda.get_device_name(0)
        info['gpu_memory_gb'] = torch.cuda.get_device_properties(0).total_memory / 1e9
    
    return info
