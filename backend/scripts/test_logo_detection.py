"""
Test Logo Detection Script
Tests the trained YOLO model on sample images
"""

from pathlib import Path
import cv2
from ultralytics import YOLO

def test_model():
    """Test the logo detection model"""
    
    # Load the trained model
    model_path = Path('../models/logo_detector_v2.pt')
    
    if not model_path.exists():
        print(f"❌ Model not found: {model_path}")
        print("💡 Run train_logo_detector.py first!")
        return
    
    print(f"📦 Loading model: {model_path}")
    model = YOLO(str(model_path))
    
    # Test on sample images
    test_dir = Path('../data/test_images')
    if not test_dir.exists():
        print(f"\n⚠️  No test images found in: {test_dir}")
        print("💡 Add some phishing page screenshots to test!")
        return
    
    test_images = list(test_dir.glob('*.png')) + list(test_dir.glob('*.jpg'))
    
    if not test_images:
        print(f"\n⚠️  No images found in: {test_dir}")
        return
    
    print(f"\n🔍 Testing on {len(test_images)} images...\n")
    
    for img_path in test_images:
        print(f"Testing: {img_path.name}")
        
        # Run detection
        results = model(str(img_path), conf=0.5)
        
        # Print detections
        for result in results:
            boxes = result.boxes
            if len(boxes) > 0:
                for box in boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    brand = model.names[cls]
                    print(f"  ✅ Detected: {brand} (confidence: {conf:.2f})")
            else:
                print(f"  ⚪ No logos detected")
        
        print()
    
    print("✅ Testing complete!")

if __name__ == "__main__":
    test_model()
