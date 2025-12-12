"""
Synthetic Dataset Generator for Phishing Logo Detection
-------------------------------------------------------
This script takes single clean logo files and generates a large, 
realistic training dataset for YOLOv8 by simulating:
- Various background colors/patterns
- Random branding positions (headers)
- Scale/Rotation variances
- Noise and blur
"""

import cv2
import numpy as np
import os
import random
import glob
from pathlib import Path
import shutil
import yaml

# CONFIG
RAW_BRANDS_DIR = "../data/brands"
OUTPUT_DIR = "../data/logo_dataset"
IMAGES_PER_BRAND = 50  # Generate 50 synthetic examples per logo
IMAGE_SIZE = 640

def init_workspace():
    if os.path.exists(OUTPUT_DIR):
        print(f"Cleaning existing dataset at {OUTPUT_DIR}...")
        shutil.rmtree(OUTPUT_DIR)
    
    # Create YOLO structure
    for split in ['train', 'val']:
        os.makedirs(f"{OUTPUT_DIR}/images/{split}", exist_ok=True)
        os.makedirs(f"{OUTPUT_DIR}/labels/{split}", exist_ok=True)

def get_random_background():
    """Create a synthetic website header background"""
    bg = np.zeros((IMAGE_SIZE, IMAGE_SIZE, 3), dtype=np.uint8)
    
    # 1. Solid Color (Light or Dark)
    if random.random() > 0.5:
        # Light theme
        color = random.randint(240, 255)
    else:
        # Dark theme
        color = random.randint(20, 50)
    bg[:] = color
    
    # 2. Add header bar simulation
    header_height = random.randint(60, 150)
    header_color = np.random.randint(0, 255, 3).tolist()
    cv2.rectangle(bg, (0, 0), (IMAGE_SIZE, header_height), header_color, -1)
    
    return bg, header_height

def augment_logo(logo):
    """Apply random augmentations to the logo"""
    # 1. Random Scale
    scale = random.uniform(0.5, 1.2)
    h, w = logo.shape[:2]
    new_h, new_w = int(h * scale), int(w * scale)
    logo = cv2.resize(logo, (new_w, new_h))
    
    # 2. Random Rotation (slight)
    angle = random.uniform(-10, 10)
    M = cv2.getRotationMatrix2D((new_w//2, new_h//2), angle, 1)
    logo = cv2.warpAffine(logo, M, (new_w, new_h), borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0,0))
    
    return logo

def overlay_transparent(background, overlay, x, y):
    """Paste transparent PNG onto background"""
    h, w = overlay.shape[:2]
    
    if x + w > background.shape[1] or y + h > background.shape[0]:
        return background, None # Skip if OOB
        
    alpha = overlay[:, :, 3] / 255.0
    for c in range(0, 3):
        background[y:y+h, x:x+w, c] = (alpha * overlay[:, :, c] +
                                       (1.0 - alpha) * background[y:y+h, x:x+w, c])
    return background, (x, y, w, h)

def generate():
    init_workspace()
    
    # Find all brand images
    brand_files = glob.glob(os.path.join(RAW_BRANDS_DIR, "*.*"))
    brand_files = [f for f in brand_files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    brands_map = {} # name -> id
    
    print(f"Found {len(brand_files)} brand logos.")
    
    for idx, brand_path in enumerate(brand_files):
        filename = os.path.basename(brand_path)
        # Normalize brand name (remove _logo, etc)
        brand_name = filename.split('.')[0].split('_')[0].lower()
        
        if brand_name in brands_map:
            class_id = brands_map[brand_name]
        else:
            class_id = len(brands_map)
            brands_map[brand_name] = class_id
            
        print(f"Processing {brand_name} (ID: {class_id})...")
        
        # Load Logo (preserve alpha)
        logo = cv2.imread(brand_path, cv2.IMREAD_UNCHANGED)
        if logo is None:
            print(f"Skipping {brand_name} (load failed)")
            continue
            
        # Ensure alpha channel
        if logo.shape[2] == 3:
            logo = cv2.cvtColor(logo, cv2.COLOR_BGR2BGRA)

        # Generate Samples
        for i in range(IMAGES_PER_BRAND):
            bg, header_h = get_random_background()
            
            # Augment
            aug_logo = augment_logo(logo)
            
            # Place in header area (typical for phishing)
            h, w = aug_logo.shape[:2]
            
            # Constraints
            if w >= IMAGE_SIZE or h >= header_h:
                aug_logo = cv2.resize(aug_logo, (min(w, 100), min(h, 50)))
                w, h = aug_logo.shape[:2]

            valid_x = IMAGE_SIZE - w
            valid_y = header_h - h
            
            # Ensure we have enough space for the random placement (min x=10, min y=5)
            if valid_x < 10 or valid_y < 5: 
                # Try to shrink logo further to fit
                scale_factor = 0.8
                aug_logo = cv2.resize(aug_logo, (0,0), fx=scale_factor, fy=scale_factor)
                w, h = aug_logo.shape[:2]
                valid_x = IMAGE_SIZE - w
                valid_y = header_h - h
                
                if valid_x < 10 or valid_y < 5: continue
            
            x = random.randint(10, valid_x)
            y = random.randint(5, valid_y)
            
            final_img, bbox = overlay_transparent(bg, aug_logo, x, y)
            
            if bbox is None: continue
            
            # Split Train/Val
            split = 'train' if random.random() < 0.8 else 'val'
            
            # Save Image
            img_filename = f"{brand_name}_{i}.jpg"
            img_path = f"{OUTPUT_DIR}/images/{split}/{img_filename}"
            cv2.imwrite(img_path, final_img)
            
            # Save Label (YOLO Format: class x_center y_center width height) normalized 0-1
            label_path = f"{OUTPUT_DIR}/labels/{split}/{img_filename.replace('.jpg', '.txt')}"
            
            bx, by, bw, bh = bbox
            cx = (bx + bw/2) / IMAGE_SIZE
            cy = (by + bh/2) / IMAGE_SIZE
            nw = bw / IMAGE_SIZE
            nh = bh / IMAGE_SIZE
            
            with open(label_path, 'w') as f:
                f.write(f"{class_id} {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}")
                
    # Generate data.yaml
    yaml_data = {
        'path': os.path.abspath(OUTPUT_DIR),
        'train': 'images/train',
        'val': 'images/val',
        'nc': len(brands_map),
        'names': list(brands_map.keys())
    }
    
    with open(f"{OUTPUT_DIR}/data.yaml", 'w') as f:
        yaml.dump(yaml_data, f)
        
    print("\nDataset Generation Complete! 🚀")
    print(f"Classes: {len(brands_map)}")
    print(f"Location: {OUTPUT_DIR}")

if __name__ == "__main__":
    generate()
