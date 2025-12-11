"""
Logo Download Script - Automated logo collection for 50 brands
This script downloads logos from Clearbit Logo API (free, no auth required)
"""

import requests
from pathlib import Path
import time

# 50 High-Risk Brands
BRANDS = {
    # Financial (15)
    'paypal': 'paypal.com',
    'chase': 'chase.com',
    'bankofamerica': 'bankofamerica.com',
    'wellsfargo': 'wellsfargo.com',
    'citibank': 'online.citibank.com',
    'americanexpress': 'americanexpress.com',
    'capitalone': 'capitalone.com',
    'hsbc': 'hsbc.com',
    'barclays': 'barclays.com',
    'venmo': 'venmo.com',
    'cashapp': 'cash.app',
    'zelle': 'zellepay.com',
    'stripe': 'stripe.com',
    'square': 'squareup.com',
    'coinbase': 'coinbase.com',
    
    # Tech Giants (15)
    'google': 'google.com',
    'microsoft': 'microsoft.com',
    'apple': 'apple.com',
    'facebook': 'facebook.com',
    'amazon': 'amazon.com',
    'twitter': 'twitter.com',
    'linkedin': 'linkedin.com',
    'instagram': 'instagram.com',
    'whatsapp': 'whatsapp.com',
    'telegram': 'telegram.org',
    'adobe': 'adobe.com',
    'dropbox': 'dropbox.com',
    'zoom': 'zoom.us',
    'slack': 'slack.com',
    'github': 'github.com',
    
    # Streaming (10)
    'netflix': 'netflix.com',
    'spotify': 'spotify.com',
    'disney': 'disneyplus.com',
    'hulu': 'hulu.com',
    'hbomax': 'hbomax.com',
    'youtube': 'youtube.com',
    'twitch': 'twitch.tv',
    'primevideo': 'primevideo.com',
    'appletv': 'tv.apple.com',
    'paramount': 'paramountplus.com',
    
    # E-commerce (10)
    'ebay': 'ebay.com',
    'alibaba': 'alibaba.com',
    'etsy': 'etsy.com',
    'walmart': 'walmart.com',
    'target': 'target.com',
    'bestbuy': 'bestbuy.com',
    'homedepot': 'homedepot.com',
    'ikea': 'ikea.com',
    'costco': 'costco.com',
    'fedex': 'fedex.com',
}

def download_logo(brand_name, domain, output_dir):
    """Download logo from Clearbit API"""
    url = f"https://logo.clearbit.com/{domain}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            output_path = output_dir / f"{brand_name}_logo.png"
            output_path.write_bytes(response.content)
            print(f"✅ Downloaded: {brand_name}")
            return True
        else:
            print(f"❌ Failed: {brand_name} (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Error downloading {brand_name}: {e}")
        return False

def main():
    # Create output directory
    output_dir = Path("data/logo_dataset/images/raw")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📥 Downloading {len(BRANDS)} brand logos...\n")
    
    success_count = 0
    for brand_name, domain in BRANDS.items():
        if download_logo(brand_name, domain, output_dir):
            success_count += 1
        time.sleep(0.5)  # Be nice to the API
    
    print(f"\n✅ Downloaded {success_count}/{len(BRANDS)} logos")
    print(f"📁 Saved to: {output_dir.absolute()}")
    print("\n🎯 Next Steps:")
    print("1. Review the downloaded logos")
    print("2. Upload to Roboflow for annotation")
    print("3. Or use the annotation script to manually annotate")

if __name__ == "__main__":
    main()
