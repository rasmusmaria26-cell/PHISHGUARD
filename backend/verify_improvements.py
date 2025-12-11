import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_whitelist():
    print("\n--- Testing Whitelist ---")
    payload = {
        "url": "https://www.google.com",
        "text": "Login to Google",
        "deceptive_links_count": 0
    }
    try:
        res = requests.post(f"{BASE_URL}/analyze", json=payload)
        data = res.json()
        print(f"URL: {payload['url']}")
        print(f"Score: {data['score']} (Expected: 0)")
        if data['score'] == 0:
            print("✅ Whitelist Test Passed")
        else:
            print("❌ Whitelist Test Failed")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_deceptive_links():
    print("\n--- Testing Deceptive Links ---")
    payload = {
        "url": "http://suspicious-site.com",
        "text": "Click here to update",
        "deceptive_links_count": 2
    }
    try:
        res = requests.post(f"{BASE_URL}/analyze", json=payload)
        data = res.json()
        print(f"Deceptive Links: {payload['deceptive_links_count']}")
        print(f"Content Score: {data['content_score']}")
        print(f"Final Score: {data['score']}")
        
        # Content score should be high due to penalty
        if data['content_score'] >= 40: # 2 * 20 = 40 penalty
            print("✅ Deceptive Link Penalty Applied")
        else:
            print("❌ Deceptive Link Penalty Failed")
            
        if "Detected 2 deceptive links" in str(data['reasons']):
             print("✅ Reason Added")
        else:
             print("❌ Reason Missing")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_whitelist()
    test_deceptive_links()
