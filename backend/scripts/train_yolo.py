"""
YOLOv8 Logo Detection Training Script
Train a custom YOLO model to detect brand logos for phishing detection
"""

from ultralytics import YOLO
import os
import yaml

def train_logo_detector(
    data_yaml='data/logos/dataset.yaml',
    epochs=100,
    batch_size=16,
    img_size=640,
    model_size='s',  # n, s, m, l, x
    device='cpu',
    project='runs/train',
    name='logo_detector'
):
    """
    Train YOLOv8 model for logo detection
    
    Args:
        data_yaml: Path to dataset YAML file
        epochs: Number of training epochs
        batch_size: Batch size for training
        img_size: Input image size
        model_size: YOLO model size (n=nano, s=small, m=medium, l=large, x=xlarge)
        device: Device to use ('cpu' or 'cuda')
        project: Project directory for saving results
        name: Name of the training run
    """
    
    print("=" * 60)
    print("YOLOv8 Logo Detector Training")
    print("=" * 60)
    
    # Load pretrained model
    model_name = f'yolov8{model_size}.pt'
    print(f"\n📦 Loading pretrained model: {model_name}")
    model = YOLO(model_name)
    
    # Verify dataset exists
    if not os.path.exists(data_yaml):
        raise FileNotFoundError(f"Dataset YAML not found: {data_yaml}")
    
    print(f"📊 Dataset config: {data_yaml}")
    
    # Training parameters
    print(f"\n⚙️  Training Configuration:")
    print(f"   - Epochs: {epochs}")
    print(f"   - Batch size: {batch_size}")
    print(f"   - Image size: {img_size}")
    print(f"   - Device: {device}")
    print(f"   - Model: YOLOv8{model_size}")
    
    # Start training
    print(f"\n🚀 Starting training...")
    print("-" * 60)
    
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=img_size,
        batch=batch_size,
        name=name,
        project=project,
        patience=20,  # Early stopping patience
        save=True,
        device=device,
        workers=4,
        verbose=True,
        plots=True,  # Generate training plots
        val=True,  # Validate during training
        # Augmentation
        hsv_h=0.015,  # Hue augmentation
        hsv_s=0.7,    # Saturation augmentation
        hsv_v=0.4,    # Value augmentation
        degrees=10,   # Rotation augmentation
        translate=0.1,  # Translation augmentation
        scale=0.5,    # Scale augmentation
        fliplr=0.5,   # Horizontal flip probability
        mosaic=1.0,   # Mosaic augmentation
    )
    
    print("\n" + "=" * 60)
    print("✅ Training Complete!")
    print("=" * 60)
    
    # Validation
    print("\n📊 Running validation...")
    metrics = model.val()
    
    print(f"\n📈 Performance Metrics:")
    print(f"   - mAP@50: {metrics.box.map50:.4f}")
    print(f"   - mAP@50-95: {metrics.box.map:.4f}")
    print(f"   - Precision: {metrics.box.mp:.4f}")
    print(f"   - Recall: {metrics.box.mr:.4f}")
    
    # Save best model
    best_model_path = f"{project}/{name}/weights/best.pt"
    print(f"\n💾 Best model saved to: {best_model_path}")
    
    # Export to ONNX for faster inference (optional)
    try:
        print("\n🔄 Exporting to ONNX format...")
        onnx_path = model.export(format='onnx')
        print(f"✅ ONNX model saved to: {onnx_path}")
    except Exception as e:
        print(f"⚠️  ONNX export failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 All done! Copy best.pt to backend/models/logo_detector.pt")
    print("=" * 60)
    
    return results, metrics


def quick_test(model_path, test_image_path):
    """Quick test of trained model"""
    print(f"\n🧪 Testing model: {model_path}")
    model = YOLO(model_path)
    
    results = model(test_image_path)
    
    for result in results:
        boxes = result.boxes
        print(f"\n📸 Detections in {test_image_path}:")
        for box in boxes:
            brand_id = int(box.cls[0])
            confidence = float(box.conf[0])
            brand_name = model.names[brand_id]
            print(f"   - {brand_name}: {confidence:.2%}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Train YOLOv8 logo detector')
    parser.add_argument('--data', default='data/logos/dataset.yaml', help='Dataset YAML path')
    parser.add_argument('--epochs', type=int, default=100, help='Number of epochs')
    parser.add_argument('--batch', type=int, default=16, help='Batch size')
    parser.add_argument('--img-size', type=int, default=640, help='Image size')
    parser.add_argument('--model', default='s', choices=['n', 's', 'm', 'l', 'x'], help='Model size')
    parser.add_argument('--device', default='cpu', help='Device (cpu or cuda)')
    parser.add_argument('--name', default='logo_detector', help='Run name')
    
    args = parser.parse_args()
    
    # Train model
    train_logo_detector(
        data_yaml=args.data,
        epochs=args.epochs,
        batch_size=args.batch,
        img_size=args.img_size,
        model_size=args.model,
        device=args.device,
        name=args.name
    )
