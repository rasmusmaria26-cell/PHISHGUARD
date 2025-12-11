import sys
import os
import logging

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

# Configure logging
logging.basicConfig(level=logging.INFO)

print("Attempting to import image_analyzer...")
try:
    from app.image_analyzer import analyze_screenshot, BRAND_WHITELIST, REFERENCE_LOGOS
    print("✅ SUCCESS: image_analyzer imported successfully")
except Exception as e:
    print(f"❌ FAILED: Import failed with error: {e}")
    sys.exit(1)

print(f"Loaded {len(BRAND_WHITELIST)} items in whitelist")
print(f"Loaded {len(REFERENCE_LOGOS)} reference logos")

# Test with empty input
try:
    result = analyze_screenshot("", "https://google.com")
    print(f"Empty input test result: {result}")
except Exception as e:
    print(f"❌ FAILED: Analysis crashed: {e}")
