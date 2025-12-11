"""
YOLO Logo Detector Training Script
Trains YOLOv8 model on the collected logo dataset
"""

from ultralytics import YOLO
from pathlib import Path
import yaml

def create_dataset_yaml():
    """Create dataset configuration file"""
    dataset_config = {
        'path': str(Path('../data/logo_dataset').absolute()),
        'train': 'images/train',
        'val': 'images/val',
        'nc': 50,  # Number of classes
        'names': [
            # Financial (15)
            'paypal', 'chase', 'bankofamerica', 'wellsfargo', 'citibank',
            'americanexpress', 'capitalone', 'hsbc', 'barclays', 'venmo',
            'cashapp', 'zelle', 'stripe', 'square', 'coinbase',
            
            # Tech Giants (15)
            'google', 'microsoft', 'apple', 'facebook', 'amazon',
            'twitter', 'linkedin', 'instagram', 'whatsapp', 'telegram',
            'adobe', 'dropbox', 'zoom', 'slack', 'github',
            
            # Streaming (10)
            'netflix', 'spotify', 'disney', 'hulu', 'hbomax',
            'youtube', 'twitch', 'primevideo', 'appletv', 'paramount',
            
            # E-commerce (10)
            'ebay', 'alibaba', 'etsy', 'walmart', 'target',
            'bestbuy', 'homedepot', 'ikea', 'costco', 'fedex',
        ]
    }
    
    yaml_path = Path('../data/logo_dataset/dataset.yaml')
    yaml_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(yaml_path, 'w') as f:
        yaml.dump(dataset_config, f, default_flow_style=False)
    
    print(f"✅ Created dataset config: {yaml_path}")
    return yaml_path

def train_model():
    """Train YOLOv8 model on logo dataset"""
    print("🚀 Starting YOLO training...\n")
    
    # Create dataset config
    dataset_yaml = create_dataset_yaml()
    
    # Load pretrained YOLOv8 nano model
    model = YOLO('yolov8n.pt')
    
    # Training parameters
    results = model.train(
        data=str(dataset_yaml),
        epochs=50,              # Number of training epochs
        imgsz=640,              # Image size
        batch=16,               # Batch size (adjust based on your GPU/RAM)
        patience=10,            # Early stopping patience
        save=True,              # Save checkpoints
        project='logo_detection',
        name='phishguard_v2',
        device='cpu',           # Use 'cuda' if you have GPU
        verbose=True,
        plots=True,             # Generate training plots
    )
    
    print("\n✅ Training complete!")
    print(f"📊 Results saved to: logo_detection/phishguard_v2/")
    
    # Validate the model
    print("\n🔍 Validating model...")
    metrics = model.val()
    
    print(f"\n📈 Performance Metrics:")
    print(f"  mAP50: {metrics.box.map50:.3f}")
    print(f"  mAP50-95: {metrics.box.map:.3f}")
    print(f"  Precision: {metrics.box.mp:.3f}")
    print(f"  Recall: {metrics.box.mr:.3f}")
    
    # Copy best model to models directory
    best_model_path = Path('logo_detection/phishguard_v2/weights/best.pt')
    if best_model_path.exists():
        target_path = Path('../models/logo_detector_v2.pt')
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        import shutil
        shutil.copy(best_model_path, target_path)
        print(f"\n✅ Model saved to: {target_path}")
    
    return results

if __name__ == "__main__":
    print("=" * 60)
    print("YOLO Logo Detector Training")
    print("=" * 60)
    print("\n⚠️  Prerequisites:")
    print("  1. Dataset images in: data/logo_dataset/images/train/")
    print("  2. YOLO labels in: data/logo_dataset/labels/train/")
    print("  3. Validation set in: data/logo_dataset/images/val/")
    print("\n")
    
    input("Press Enter to start training (or Ctrl+C to cancel)...")
    
    try:
        train_model()
        print("\n🎉 All done! Your model is ready to use.")
        print("\n🎯 Next Steps:")
        print("  1. Update yolo_detector.py to use the new model")
        print("  2. Test with: python test_logo_detection.py")
        print("  3. Reload the extension and try scanning!")
    except KeyboardInterrupt:
        print("\n\n❌ Training cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Error during training: {e}")
        print("💡 Tip: Make sure your dataset is properly organized")
