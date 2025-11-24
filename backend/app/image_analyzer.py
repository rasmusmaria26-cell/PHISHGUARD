import cv2
import numpy as np
import base64
import os
import logging

logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BRANDS_DIR = os.path.join(BASE_DIR, "../data/brands")

# Constants
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
ORB_FEATURES = 2000  # Reduced from 5000 for better performance
MIN_INLIERS = 10
MARGIN_MULTIPLIER = 1.5

REFERENCE_LOGOS = {}
orb = cv2.ORB_create(nfeatures=ORB_FEATURES)

# Brand whitelist: brand_name -> list of legitimate domains
BRAND_WHITELIST = {
    "google": ["youtube", "google", "gmail", "gstatic"],
    "microsoft": ["microsoft", "live.com", "office", "bing", "msn"],
    "facebook": ["facebook", "fb.com", "meta", "instagram"],
    "netflix": ["netflix.com"],
    "paypal": ["paypal.com"],
    "amazon": ["amazon.com", "aws"],
    "apple": ["apple.com", "icloud"],
}

def load_references():
    """Loads logos from the data/brands folder."""
    if not os.path.exists(BRANDS_DIR):
        logger.warning(f"Brands folder not found at {BRANDS_DIR}")
        return

    for filename in os.listdir(BRANDS_DIR):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            brand_name = os.path.splitext(filename)[0]
            path = os.path.join(BRANDS_DIR, filename)
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                REFERENCE_LOGOS[brand_name] = img
                logger.info(f"Loaded brand logo: {brand_name}")

load_references()

# --- YOLO INTEGRATION ---
try:
    from .yolo_detector import get_detector
    yolo_detector = get_detector()
    USE_YOLO = yolo_detector.is_available()
    if USE_YOLO:
        logger.info("YOLO logo detector loaded successfully")
    else:
        logger.info("YOLO model not found, using ORB fallback")
except ImportError as e:
    logger.warning(f"YOLO detector not available: {e}")
    USE_YOLO = False

def analyze_screenshot(base64_string: str, url: str) -> dict:
    try:
        # 1. Validate and Decode Image
        if "," in base64_string:
            base64_string = base64_string.split(",")[1]
        
        # Size validation
        if len(base64_string) > MAX_IMAGE_SIZE:
            logger.warning("Image too large, rejecting")
            return {"score": 0, "verdict": "Error", "reason": "Image too large"}
            
        img_data = base64.b64decode(base64_string)
        np_arr = np.frombuffer(img_data, np.uint8)
        screen_img = cv2.imdecode(np_arr, cv2.IMREAD_GRAYSCALE)
        
        if screen_img is None:
            return {"score": 0, "verdict": "Error", "reason": "Invalid image"}

        # --- YOLO DETECTION (Primary Method) ---
        if USE_YOLO:
            try:
                detections = yolo_detector.detect_logos(screen_img)
                
                if detections:
                    # Get dominant brand (highest confidence)
                    dominant = yolo_detector.get_dominant_brand(detections)
                    brand = dominant['brand']
                    confidence = dominant['confidence']
                    
                    logger.info(f"YOLO detected: {brand} (confidence: {confidence:.2%})")
                    
                    # Verify URL matches detected brand
                    url_lower = url.lower()
                    brand_lower = brand.lower()
                    
                    # Check whitelist
                    if brand_lower in BRAND_WHITELIST:
                        legitimate_domains = BRAND_WHITELIST[brand_lower]
                        if any(domain in url_lower for domain in legitimate_domains):
                            return {
                                "score": 0,
                                "verdict": "Safe",
                                "reason": f"Verified {brand} branding (YOLO: {confidence:.0%})",
                                "method": "YOLO"
                            }
                    
                    # PHISHING: Brand detected but URL doesn't match
                    if brand_lower not in url_lower:
                        return {
                            "score": 95,
                            "verdict": "Phishing",
                            "reason": f"Visuals show '{brand}' (confidence: {confidence:.0%}) but URL is different",
                            "method": "YOLO"
                        }
                    else:
                        return {
                            "score": 0,
                            "verdict": "Safe",
                            "reason": f"Verified {brand} branding (YOLO: {confidence:.0%})",
                            "method": "YOLO"
                        }
                        
            except Exception as e:
                logger.error(f"YOLO detection failed: {e}, falling back to ORB")

        # --- ORB DETECTION (Fallback Method) ---
        # 2. Detect Features
        kp_screen, des_screen = orb.detectAndCompute(screen_img, None)
        if des_screen is None or len(des_screen) < 2:
            return {"score": 0, "verdict": "Safe", "reason": "No features"}

        # 3. Matching Logic
        bf = cv2.BFMatcher(cv2.NORM_HAMMING)
        
        brand_scores = {}
        
        logger.info("Scanning for brand impersonation (ORB)")
        
        for brand, ref_img in REFERENCE_LOGOS.items():
            kp_ref, des_ref = orb.detectAndCompute(ref_img, None)
            if des_ref is None: continue
            
            matches = bf.knnMatch(des_ref, des_screen, k=2)
            
            good_points = []
            for m, n in matches:
                if m.distance < 0.75 * n.distance:
                    good_points.append(m)
            
            # Geometry Check
            if len(good_points) > 10:
                src_pts = np.float32([kp_ref[m.queryIdx].pt for m in good_points]).reshape(-1, 1, 2)
                dst_pts = np.float32([kp_screen[m.trainIdx].pt for m in good_points]).reshape(-1, 1, 2)

                M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
                
                if mask is not None:
                    inliers = np.sum(mask)
                    logger.debug(f"Brand {brand}: {inliers} inliers")
                    
                    # Threshold check
                    if inliers > MIN_INLIERS: 
                        brand_scores[brand] = inliers

        # 4. Pick Winner (Winner Takes All Logic)
        detected_brand = None
        highest_score = 0
        
        if brand_scores:
            sorted_brands = sorted(brand_scores.items(), key=lambda item: item[1], reverse=True)
            winner_name, winner_score = sorted_brands[0]
            
            # MARGIN CHECK: Does the winner truly dominate the runner-up?
            if len(sorted_brands) > 1:
                runner_up_score = sorted_brands[1][1]
                
                # If winner is significantly better OR has high absolute score
                if winner_score > (runner_up_score * MARGIN_MULTIPLIER) or winner_score > 40:
                    detected_brand = winner_name
                    highest_score = winner_score
                else:
                    logger.info("Ambiguous visual match, dropping result")
            else:
                detected_brand = winner_name
                highest_score = winner_score

        # 5. Verdict
        if detected_brand:
            logger.info(f"Visual match: {detected_brand} with {highest_score} inliers (ORB)")
            
            url_lower = url.lower()
            brand_lower = detected_brand.lower()

            # Check whitelist using dictionary
            if brand_lower in BRAND_WHITELIST:
                legitimate_domains = BRAND_WHITELIST[brand_lower]
                if any(domain in url_lower for domain in legitimate_domains):
                    return {
                        "score": 0,
                        "verdict": "Safe",
                        "reason": f"Verified visual branding for {detected_brand}",
                        "method": "ORB"
                    }

            # PHISHING CHECK (URL Mismatch)
            # If not whitelisted but brand detected in URL, it's safe
            if brand_lower not in url_lower:
                return {
                    "score": 95,
                    "verdict": "Phishing",
                    "reason": f"Visuals mimic '{detected_brand}' but URL is mismatched",
                    "method": "ORB"
                }
            else:
                return {
                    "score": 0,
                    "verdict": "Safe",
                    "reason": f"Verified visual branding for {detected_brand}",
                    "method": "ORB"
                }

        return {"score": 0, "verdict": "Safe", "reason": "No dominant brand impersonation detected", "method": "ORB"}

    except (ValueError, cv2.error) as e:
        logger.error(f"Visual analysis error: {e}")
        return {"score": 0, "verdict": "Error", "reason": "Visual analysis failed"}