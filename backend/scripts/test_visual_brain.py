import sys
import os
import cv2
import base64
import random

# --- CRITICAL FIX: Add parent folder to Python Path ---
# This allows the script in 'scripts/' to import from 'app/'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# NOW we can import successfully
from app.image_analyzer import analyze_screenshot, load_references

# --- CONFIGURATION ---
# Pointing to your local brands folder
# We use '..' to go up one level from scripts to backend
brands_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "brands")
TEST_IMAGES_DIR = brands_path

def test_visuals():
    print(f"\n--- 👁️ VISUAL BRAIN TEST ---")
    print(f"Target Folder: {TEST_IMAGES_DIR}")
    
    # 1. Force reload of references
    print("Loading reference logos...")
    try:
        load_references()
    except Exception as e:
        print(f"Error loading references: {e}")
    
    # 2. Check if folder exists
    if not os.path.exists(TEST_IMAGES_DIR):
        print(f"\n[ERROR] Folder not found: {TEST_IMAGES_DIR}")
        return

    # 3. Get all images in that folder
    images = [f for f in os.listdir(TEST_IMAGES_DIR) if f.endswith(('.png', '.jpg', '.jpeg'))]
    if not images:
        print("[ERROR] Directory exists but is empty.")
        return
    
    print(f"Found {len(images)} images. Testing them now...\n")

    # 4. Test the images
    for img_name in images:
        img_path = os.path.join(TEST_IMAGES_DIR, img_name)
        print(f"Scanning: {img_name}...")
        
        try:
            # Encode as Base64 (Simulating the Browser Extension)
            with open(img_path, "rb") as img_file:
                b64_str = base64.b64encode(img_file.read()).decode('utf-8')
            
            # Run Analysis with Fake URL
            fake_url = "http://suspicious-login-attempt.com"
            result = analyze_screenshot(b64_str, fake_url)
            
            print(f"    Score:   {result['score']}")
            print(f"    Verdict: {result['verdict']}")
            print(f"    Reason:  {result['reason']}")
            
            if result['score'] > 90:
                print("    ✅ SUCCESS: Visual Impersonation Detected!")
            else:
                print("    ⚠️ MISS: AI did not match this specific image.")

        except Exception as e:
            print(f"    Error processing image: {e}")
        
        print("-" * 40)

if __name__ == "__main__":
    test_visuals()