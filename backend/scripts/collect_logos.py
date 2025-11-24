"""
Logo Dataset Collection Script
Download and prepare brand logos for YOLO training
"""

import requests
import os
from PIL import Image
import io
import time

# Official logo URLs (high quality)
LOGO_SOURCES = {
    'paypal': [
        'https://www.paypalobjects.com/webstatic/mktg/logo/pp_cc_mark_111x69.jpg',
        'https://www.paypalobjects.com/digitalassets/c/website/logo/full-text/pp_fc_hl.svg',
    ],
    'google': [
        'https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png',
    ],
    'microsoft': [
        'https://img-prod-cms-rt-microsoft-com.akamaized.net/cms/api/am/imageFileData/RE1Mu3b',
    ],
    'netflix': [
        'https://assets.nflxext.com/us/ffe/siteui/common/icons/nficon2016.png',
    ],
    'amazon': [
        'https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg',
    ],
    'apple': [
        'https://www.apple.com/ac/structured-data/images/knowledge_graph_logo.png',
    ],
}

def download_image(url, save_path, timeout=10):
    """Download image from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # Open and save image
        img = Image.open(io.BytesIO(response.content))
        
        # Convert to RGB if needed
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        img.save(save_path, 'JPEG', quality=95)
        return True
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def collect_logos(output_dir='data/logos/images/train'):
    """Download brand logos"""
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("📥 Downloading Brand Logos")
    print("=" * 60)
    
    total_downloaded = 0
    
    for brand, urls in LOGO_SOURCES.items():
        print(f"\n🏷️  {brand.upper()}")
        brand_dir = os.path.join(output_dir, brand)
        os.makedirs(brand_dir, exist_ok=True)
        
        for idx, url in enumerate(urls, 1):
            filename = f"{brand}_{idx:03d}.jpg"
            filepath = os.path.join(brand_dir, filename)
            
            if os.path.exists(filepath):
                print(f"   ⏭️  Skipping {filename} (already exists)")
                continue
            
            print(f"   ⬇️  Downloading {filename}...")
            if download_image(url, filepath):
                print(f"   ✅ Saved to {filepath}")
                total_downloaded += 1
            
            time.sleep(0.5)  # Rate limiting
    
    print("\n" + "=" * 60)
    print(f"✅ Downloaded {total_downloaded} logos")
    print("=" * 60)
    
    print("\n📝 Next Steps:")
    print("1. Add more logo variations manually")
    print("2. Use data augmentation to create more samples")
    print("3. Annotate logos with bounding boxes using LabelImg or Roboflow")
    print("4. Run: python scripts/train_yolo.py")


if __name__ == "__main__":
    collect_logos()
