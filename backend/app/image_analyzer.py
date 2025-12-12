import cv2
import numpy as np
import base64
import os
import logging
import glob

logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BRANDS_DIR = os.path.join(BASE_DIR, "../data/brands")

# Constants
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MIN_INLIERS = 5
MARGIN_MULTIPLIER = 1.5

# Initialize Global Variables
BRAND_WHITELIST = {
    "paypal": ["paypal.com", "paypal.me"],
    "google": ["google.com", "accounts.google.com"],
    "microsoft": ["microsoft.com", "live.com", "office.com"],
    "netflix": ["netflix.com"],
    "facebook": ["facebook.com", "fb.com"],
    "apple": ["apple.com", "icloud.com"],
    "amazon": ["amazon.com", "amazon.co.uk", "amazon.de"],
    "instagram": ["instagram.com"],
    "linkedin": ["linkedin.com"],
    "twitter": ["twitter.com", "x.com"],
    "whatsapp": ["whatsapp.com"],
    "telegram": ["telegram.org", "t.me"]
}

REFERENCE_LOGOS = {}

def load_reference_logos():
    """Load reference logos for ORB matching"""
    global REFERENCE_LOGOS
    if not os.path.exists(BRANDS_DIR):
        logger.warning(f"Brands directory not found: {BRANDS_DIR}")
        return

    # Load all images in the brands directory
    # Look for both PNG and JPG files
    image_files = glob.glob(os.path.join(BRANDS_DIR, "*.png")) + glob.glob(os.path.join(BRANDS_DIR, "*.jpg"))
    
    for img_path in image_files:
        filename = os.path.basename(img_path)
        # Fix: correctly strip extension and any suffix like _logo
        brand_name = filename.split('.')[0].split('_')[0].lower()
        
        try:
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                REFERENCE_LOGOS[brand_name] = img
                # Update whitelist if brand not known (default to name.com)
                if brand_name not in BRAND_WHITELIST:
                    BRAND_WHITELIST[brand_name] = [f"{brand_name}.com"]
            else:
                logger.warning(f"Could not read logo: {filename}")
        except Exception as e:
            logger.error(f"Error loading logo {filename}: {e}")

    logger.info(f"Loaded {len(REFERENCE_LOGOS)} reference logos for ORB detection")

# Initialize YOLO and ORB
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

# Initialize ORB
orb = cv2.ORB_create()

# Load logos on module import
load_reference_logos()

def analyze_screenshot(base64_string: str, url: str, page_text: str = "") -> dict:
    try:
        # 1. Validate and Decode Image
        if not base64_string:
             return {"score": 0, "verdict": "Error", "reason": "Empty image string"}

        if "," in base64_string:
            base64_string = base64_string.split(",")[1]
        

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
                    
                    # SAFETY VALVE: Trust Government & Education Domains
                    # These TLDs are highly regulated and unlikely to host "Visual Clones" of commercial brands.
                    trusted_tlds = ['.gov', '.edu', '.mil', '.ac.in', '.gov.in', '.nic.in']
                    if any(tld in url_lower for tld in trusted_tlds):
                        logger.info(f"Trusted TLD detected ({url}). Ignoring visual match for {brand}.")
                        return {
                            "score": 0,
                            "verdict": "Safe",
                            "reason": f"Trusted domain ({url_lower.split('.')[-1]}) verified.",
                            "method": "YOLO (Trusted TLD)"
                        }

                    # PHISHING: Brand detected but URL doesn't match
                    if brand_lower not in url_lower:
                        # Intent Analysis: Check for PHISHING-SPECIFIC threats (not just "Sign In")
                        # We avoid common header terms like "Sign In", "Login", "Account" as they appear on Wikia/YouTube headers.
                        sensitive_keywords = [
                            'verify your', 'verify account', 'confirm password', 'update payment', 
                            'billing information', 'security alert', 'unusual activity', 
                            'account suspended', 'unlock account', 'confirm identity', 
                            'enter password', 'enter credit', 'card number', 'expiration date'
                        ]
                        
                        # Check text content for intent
                        has_intent = any(k in page_text.lower() for k in sensitive_keywords)
                        
                        if has_intent:
                            return {
                                "score": 95,
                                "verdict": "Phishing",
                                "reason": "Suspicious visual branding + Phishing threats detected",
                                "method": "YOLO"
                            }
                        else:
                            # Strict Logic: If logo is found and URL is mismatch, treat as Phishing (95)
                            # We trust the whitelist mechanism to protect legitimate sites.
                            return {
                                "score": 95,
                                "verdict": "Phishing",
                                "reason": f"Visuals mimic '{brand}' but URL is mismatched",
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
                    # Log potentially interesting matches
                    if inliers > 2:
                        logger.info(f"debug: Brand {brand} -> {inliers} inliers")
                    
                    # Threshold check using lowered threshold
                    if inliers > MIN_INLIERS: 
                        brand_scores[brand] = inliers

        # 4. Pick Winner (Winner Takes All Logic)
        detected_brand = None
        highest_score = 0
        
        if brand_scores:
            logger.info(f"Brand scores candidates: {brand_scores}")
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
            
            # Extract domain from URL for whitelist checking
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()  # Get only the domain part
            brand_lower = detected_brand.lower()

            # Check whitelist using dictionary
            if brand_lower in BRAND_WHITELIST:
                legitimate_domains = BRAND_WHITELIST[brand_lower]
                # Check if the actual domain matches any whitelisted domain
                if any(legit_domain in domain for legit_domain in legitimate_domains):
                    return {
                        "score": 0,
                        "verdict": "Safe",
                        "reason": f"Verified visual branding for {detected_brand}",
                        "method": "ORB"
                    }

            # PHISHING CHECK (URL Mismatch)
            # If brand detected but domain doesn't match whitelist -> PHISHING
            return {
                "score": 95,
                "verdict": "Phishing",
                "reason": f"Visuals mimic '{detected_brand}' but URL is mismatched",
                "method": "ORB"
            }

        return {"score": 0, "verdict": "Safe", "reason": "No dominant brand impersonation detected", "method": "ORB"}

    except (ValueError, cv2.error) as e:
        logger.error(f"Visual analysis error: {e}")
        return {"score": 0, "verdict": "Error", "reason": "Visual analysis failed"}