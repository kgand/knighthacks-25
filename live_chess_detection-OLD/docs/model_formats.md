# Model Format Support

The Chess Vision Live system now supports multiple model formats for maximum flexibility.

## Supported Formats

### 1. PyTorch Models (.pt)
- **Default format** for YOLO models
- Requires: `torch`, `ultralytics`
- Full support for training, validation, prediction, and export
- Recommended for new projects

### 2. TensorFlow/Keras Models (.h5)
- **Alternative format** for compatibility with TensorFlow models
- Requires: `tensorflow` (install with `pip install tensorflow`)
- Supports: prediction and validation
- Useful for models trained with TensorFlow/Keras

## Usage

### Loading PyTorch Models

```python
from models.detector_yolo import YOLOChessDetector

# Load trained PyTorch model
detector = YOLOChessDetector(
    model_path='models/yolo/trained/best.pt',
    conf_threshold=0.45,
    device='auto'
)

# Or use pretrained model
detector = YOLOChessDetector(
    model_size='yolov8s',
    device='auto'
)
```

### Loading TensorFlow Models

```python
from models.detector_yolo import YOLOChessDetector

# Load .h5 TensorFlow model
detector = YOLOChessDetector(
    model_path='models/yolo/trained/best.h5',
    conf_threshold=0.45,
    device='auto'
)
```

### Running Inference

The API is identical regardless of model format:

```python
import cv2

# Load image
image = cv2.imread('chess_board.jpg')

# Run detection
results = detector.detect(image, img_size=1024, visualize=True)

# Access results
boxes = results['boxes']          # Bounding boxes [N, 4] (x1, y1, x2, y2)
classes = results['classes']      # Class IDs [N]
confidences = results['confidences']  # Confidence scores [N]
class_names = results['class_names']  # Class name mapping

# Visualize (if visualize=True)
annotated_image = results['image']
cv2.imshow('Detections', annotated_image)
```

## Installation

### For PyTorch Models Only
```bash
pip install torch torchvision ultralytics
```

### For Both PyTorch and TensorFlow Models
```bash
pip install torch torchvision ultralytics tensorflow
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

## Model Format Conversion

If you have a model in one format and need to convert it:

### PyTorch → TensorFlow
```python
from ultralytics import YOLO

# Load PyTorch model
model = YOLO('models/yolo/trained/best.pt')

# Export to TensorFlow formats
model.export(format='saved_model')  # TensorFlow SavedModel
model.export(format='pb')           # TensorFlow GraphDef
model.export(format='tflite')       # TensorFlow Lite
```

### TensorFlow → PyTorch
Converting TensorFlow models to PyTorch is more complex and may require manual implementation or tools like `onnx`.

## Architecture Notes

### PyTorch Implementation
- Uses `ultralytics.YOLO` directly
- Native YOLO operations
- Optimal performance

### TensorFlow Implementation
- Uses `tensorflow.keras.models.load_model`
- Custom preprocessing and postprocessing
- Assumes YOLO-style output format: `[batch, num_predictions, 5+num_classes]`
- Output format: `[x_center, y_center, width, height, objectness, class_scores...]`

## GPU Support

### PyTorch
- CUDA (NVIDIA)
- ROCm (AMD)
- MPS (Apple Silicon)

### TensorFlow
- CUDA (NVIDIA) - automatically detected
- CPU fallback if no GPU available

Set device explicitly:
```python
detector = YOLOChessDetector(
    model_path='model.h5',
    device='cuda'  # or 'cpu'
)
```

## Troubleshooting

### TensorFlow Not Installed
```
ImportError: TensorFlow is not installed. Install it with: pip install tensorflow
```
**Solution**: Install TensorFlow: `pip install tensorflow`

### Model Format Mismatch
```
ValueError: Unsupported model format: model.onnx. Use .pt or .h5
```
**Solution**: Use `.pt` (PyTorch) or `.h5` (TensorFlow/Keras) format

### Output Shape Mismatch
If the TensorFlow model has a different output format, you may need to modify the `_detect_tensorflow` method in `models/detector_yolo.py` to match your specific model architecture.

## Performance Comparison

| Format     | Load Time | Inference Speed | Memory Usage |
|------------|-----------|-----------------|--------------|
| PyTorch    | Fast      | Fastest         | Moderate     |
| TensorFlow | Moderate  | Fast            | Moderate     |

*Note: Actual performance depends on hardware, model size, and batch size.*

## Testing

Run the test script to verify both formats work:

```bash
python test_h5_support.py
```

This will test:
1. PyTorch model loading and inference
2. TensorFlow model loading and inference
3. Output format consistency

## Examples

See working examples in:
- `test_system.py` - System-wide testing
- `test_h5_support.py` - Format-specific testing
- `inference/live_detector.py` - Live detection demo

