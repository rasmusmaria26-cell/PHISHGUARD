"""
YOLOv8 Logo Detector Module
Detects brand logos in screenshots for phishing detection
"""

from ultralytics import YOLO
import cv2
import numpy as np
import logging
import os
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class LogoDetector:
    """YOLOv8-based logo detector for brand impersonation detection"""
    
    def __init__(self, model_path: str = 'models/logo_detector.pt', confidence_threshold: float = 0.5):
        """
        Initialize logo detector
        
        Args:
            model_path: Path to trained YOLO model
            confidence_threshold: Minimum confidence for detections (0-1)
        """
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.model_loaded = False
        
        # Try to load model
        if os.path.exists(model_path):
            try:
                self.model = YOLO(model_path)
                self.model_loaded = True
                logger.info(f"YOLO model loaded from {model_path}")
            except Exception as e:
                logger.error(f"Failed to load YOLO model: {e}")
        else:
            logger.warning(f"YOLO model not found at {model_path}. Using fallback detection.")
    
    def detect_logos(self, image: np.ndarray) -> List[Dict]:
        """
        Detect logos in image
        
        Args:
            image: Input image (BGR or grayscale)
            
        Returns:
            List of detections with format:
            [
                {
                    'brand': 'paypal',
                    'confidence': 0.95,
                    'bbox': [x1, y1, x2, y2]
                },
                ...
            ]
        """
        if not self.model_loaded:
            return []
        
        try:
            # Convert grayscale to BGR if needed
            if len(image.shape) == 2:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            
            # Run inference
            results = self.model(image, conf=self.confidence_threshold, verbose=False)
            
            detections = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    brand_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    bbox = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                    
                    brand_name = self.model.names[brand_id]
                    
                    detections.append({
                        'brand': brand_name,
                        'confidence': confidence,
                        'bbox': bbox
                    })
                    
                    logger.debug(f"Detected {brand_name} with confidence {confidence:.2f}")
            
            return detections
            
        except Exception as e:
            logger.error(f"Logo detection error: {e}")
            return []
    
    def get_dominant_brand(self, detections: List[Dict]) -> Optional[Dict]:
        """
        Get brand with highest confidence from detections
        
        Args:
            detections: List of detection dictionaries
            
        Returns:
            Detection with highest confidence, or None if empty
        """
        if not detections:
            return None
        
        return max(detections, key=lambda x: x['confidence'])
    
    def filter_by_position(self, detections: List[Dict], image_height: int, top_fraction: float = 0.3) -> List[Dict]:
        """
        Filter detections to only those in top portion of image
        (logos typically appear in header)
        
        Args:
            detections: List of detection dictionaries
            image_height: Height of image in pixels
            top_fraction: Fraction of image height to consider (0-1)
            
        Returns:
            Filtered list of detections
        """
        threshold_y = image_height * top_fraction
        
        filtered = []
        for det in detections:
            bbox = det['bbox']
            center_y = (bbox[1] + bbox[3]) / 2
            
            if center_y <= threshold_y:
                filtered.append(det)
        
        return filtered
    
    def is_available(self) -> bool:
        """Check if YOLO model is loaded and available"""
        return self.model_loaded


# Global instance (lazy loaded)
_detector_instance = None

def get_detector() -> LogoDetector:
    """Get or create global detector instance"""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = LogoDetector()
    return _detector_instance
