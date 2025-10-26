"""YOLO training script with AMD GPU support."""

import argparse
from models.detector_yolo import setup_yolo_training


def main():
    parser = argparse.ArgumentParser(description='Train YOLO chess detector')
    parser.add_argument('--data', default='config/yolo_data.yaml', help='Dataset config')
    parser.add_argument('--epochs', type=int, default=50)
    parser.add_argument('--batch-size', type=int, default=4)
    parser.add_argument('--img-size', type=int, default=1024)
    parser.add_argument('--device', default='rocm')
    parser.add_argument('--model', default='yolov8s')
    
    args = parser.parse_args()
    
    # Start training
    model = setup_yolo_training(
        data_yaml=args.data,
        model_size=args.model,
        epochs=args.epochs,
        batch_size=args.batch_size,
        img_size=args.img_size,
        device=args.device,
    )
    
    print("✅ YOLO training complete!")


if __name__ == "__main__":
    main()
