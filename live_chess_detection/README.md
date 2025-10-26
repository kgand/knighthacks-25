# Chess Vision Live

Real-time chess piece detection and move tracking powered by deep learning.

## Features

- **Real-time Detection**: Live piece tracking from webcam
- **Multiple Models**: YOLO and Inception architectures
- **AMD GPU Support**: Optimized for ROCm
- **Multi-source Training**: Diverse dataset for robustness
- **Web Interface**: Modern Gradio-based UI
- **Chess Logic**: Full move validation and position analysis

## Performance

- **YOLOv8s**: 91% mAP @ 42 FPS (AMD RX 7900 XTX)
- **InceptionV3**: 89% mAP @ 18 FPS (AMD RX 7900 XTX)

## Installation

### Prerequisites

- Python 3.8+
- CUDA/ROCm compatible GPU (recommended)
- 8GB+ RAM

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd live_chess_detection
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. For AMD GPU support, see [AMD Setup Guide](docs/setup_amd.md)

## Quick Start

### Web Interface

Launch the web interface:
```bash
python run_app.py
```

Open your browser to `http://localhost:7860`

### Command Line

Run live detection:
```bash
python -m inference.live_detector --model models/yolo/trained/best.pt --camera 0
```

## Usage

### Web Interface

1. **Load Model**: Enter path to trained model weights
2. **Upload Image**: Upload chess board image for detection
3. **View Results**: See detected pieces with confidence scores

### Live Detection

The live detector provides:
- Real-time piece detection from webcam
- Board state tracking
- Move validation
- Position analysis

### Model Training

Train your own models:

```python
from models.detector_yolo import setup_yolo_training

# Train YOLO model
model = setup_yolo_training(
    data_yaml='data/chess_dataset.yaml',
    epochs=50,
    batch_size=4
)
```

## Architecture

### Models

- **YOLOv8**: Real-time object detection
- **InceptionV3**: Alternative architecture
- **Piece Classifier**: Individual piece recognition

### Inference Pipeline

1. **Frame Capture**: Webcam input
2. **Preprocessing**: Image enhancement
3. **Detection**: Piece localization
4. **Classification**: Piece type identification
5. **Board Mapping**: Square assignment
6. **Validation**: Move legality checking

## Dataset

Multi-source dataset combining:
- **Synthetic** (35%): Generated from Chess.com games
- **Roboflow** (30%): Real-world annotations
- **Kaggle** (25%): Diverse board styles
- **YouTube** (10%): Tournament footage

## Configuration

### Model Settings

```yaml
# config/models.yaml
yolo:
  model_size: yolov8s
  conf_threshold: 0.45
  device: auto

inception:
  backbone: resnet18
  num_classes: 12
  dropout_rate: 0.5
```

### Training Parameters

```yaml
# config/amd_training.yaml
training:
  epochs: 50
  batch_size: 4
  learning_rate: 0.001
  device: rocm
```

## Development

### Project Structure

```
live_chess_detection/
├── models/           # Model implementations
├── inference/        # Detection and validation
├── utils/           # Utility functions
├── ui/              # Web interface
├── training/        # Training scripts
├── data/            # Dataset and cache
├── config/          # Configuration files
└── docs/            # Documentation
```

### Testing

Run the test suite:
```bash
pytest test_*.py
```

### Code Quality

Format code:
```bash
black .
flake8 .
```

## Troubleshooting

### Common Issues

1. **CUDA Out of Memory**: Reduce batch size
2. **Model Loading Error**: Check model path and format
3. **Detection Issues**: Adjust confidence threshold

### Performance Tips

1. Use GPU acceleration when available
2. Optimize image resolution for your use case
3. Enable model caching for repeated inference

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [python-chess](https://github.com/niklasf/python-chess)
- [Gradio](https://github.com/gradio-app/gradio)
- [PyTorch](https://pytorch.org/)

## Citation

If you use this project in your research, please cite:

```bibtex
@software{chess_vision_live,
  title={Chess Vision Live: Real-time Chess Piece Detection},
  author={Your Name},
  year={2024},
  url={https://github.com/your-username/chess-vision-live}
}
```
