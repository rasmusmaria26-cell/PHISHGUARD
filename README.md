# 🛡️ PhishGuard

**AI-Powered Phishing Detection Browser Extension**

PhishGuard is an advanced browser extension that protects users from phishing attacks using multi-layered AI detection. Unlike traditional blacklist-based solutions, PhishGuard analyzes websites in real-time using heuristic analysis, NLP content scanning, and computer vision to detect both known and zero-day phishing threats.

![Version](https://img.shields.io/badge/version-1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8+-blue)

---

## 🚀 Key Features

### 🔍 **Triple-Layer Detection System**

1. **Heuristic URL Analysis**
   - Analyzes 15+ technical indicators (suspicious subdomains, SSL certificates, URL patterns)
   - Detects homograph attacks and typosquatting
   - Checks domain age and reputation

2. **NLP Content Scanning**
   - Machine learning model trained on phishing patterns
   - Detects urgency tactics ("Verify Account Now!", "Suspended Account")
   - Analyzes page text for suspicious language patterns

3. **YOLO Visual Detection** ⭐ NEW
   - Computer vision-based logo detection
   - Identifies brand impersonation attempts
   - Detects fake login pages for popular services (Google, Netflix, PayPal, etc.)

### ⚡ **Real-Time Protection**

- **Instant Blocking**: Automatically overlays warning screens on dangerous sites
- **Trust Score**: Transparent 0-100 scoring system for every page
- **Visual Indicators**: Color-coded threat levels (Safe/Suspicious/Dangerous)
- **One-Click Override**: Advanced users can bypass warnings if needed

### 📊 **Comprehensive Analysis**

- Detailed breakdown of detection factors
- Visual similarity analysis for brand impersonation
- Heuristic scoring with explanations
- Content analysis results

---

## 🛠️ Tech Stack

### **Frontend (Browser Extension)**
- JavaScript (ES6+)
- HTML5 & CSS3
- Chrome Extension Manifest V3

### **Backend (Detection Engine)**
- **Python 3.8+**
- **FastAPI** - High-performance API framework
- **Scikit-learn** - Content analysis ML models
- **Ultralytics YOLO** - Visual detection
- **OpenCV** - Image processing
- **Pandas & NumPy** - Data processing

### **Machine Learning Models**
- TF-IDF Vectorizer for text analysis
- Logistic Regression for content classification
- YOLOv8 for logo detection
- Custom heuristic scoring algorithm

---

## 📦 Installation

### **Prerequisites**
- Python 3.8 or higher
- Chrome/Edge browser (Manifest V3 compatible)
- pip package manager

### **Backend Setup**

1. **Clone the repository**
   ```bash
   git clone https://github.com/rasmusmaria26-cell/PHISHGUARD.git
   cd PHISHGUARD
   ```

2. **Set up Python virtual environment**
   ```bash
   cd backend
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start the backend server**
   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

   The API will be available at `http://127.0.0.1:8000`

### **Browser Extension Setup**

1. **Open Chrome/Edge**
2. Navigate to `chrome://extensions/` (or `edge://extensions/`)
3. Enable **Developer mode** (toggle in top-right)
4. Click **Load unpacked**
5. Select the `extension` folder from this repository
6. PhishGuard icon should appear in your browser toolbar ✅

---

## 🎯 Usage

### **Automatic Protection**
- PhishGuard automatically scans every page you visit
- Warning screens appear instantly on detected phishing sites
- No configuration needed for basic protection

### **Manual Scanning**
1. Click the PhishGuard icon in your browser toolbar
2. Click **"Scan Current Page"**
3. View detailed analysis results:
   - Overall trust score
   - Heuristic analysis breakdown
   - Content analysis results
   - Visual detection findings

### **Understanding Threat Levels**

| Score | Level | Color | Action |
|-------|-------|-------|--------|
| 80-100 | ✅ Safe | Green | Page appears legitimate |
| 50-79 | ⚠️ Suspicious | Yellow | Exercise caution |
| 0-49 | 🚫 Dangerous | Red | Blocked automatically |

---

## 🧪 Testing

### **Test Pages**
The project includes test pages to verify detection capabilities:

```bash
# Open test pages in your browser
backend/test_google.html      # Fake Google login
backend/test_netflix.html     # Fake Netflix page
backend/test_dashboard.html   # Visual trap examples
backend/visual_trap.html      # Brand impersonation tests
```

See [TEST_PAGES_README.md](backend/TEST_PAGES_README.md) for detailed testing instructions.

### **YOLO Model Training**
To train the visual detection model with your own logo dataset:

```bash
cd backend
python scripts/train_yolo.py
```

See [YOLO_QUICKSTART.md](backend/YOLO_QUICKSTART.md) for training instructions.

---

## 📁 Project Structure

```
PHISHGUARD/
├── extension/              # Browser extension
│   ├── manifest.json      # Extension configuration
│   ├── popup.html         # Extension popup UI
│   ├── popup.js           # Popup logic
│   ├── content.js         # Page content analyzer
│   ├── background.js      # Background service worker
│   └── warning.html       # Phishing warning overlay
│
├── backend/               # Detection engine
│   ├── app/
│   │   ├── main.py           # FastAPI application
│   │   ├── heuristic.py      # URL heuristic analysis
│   │   ├── content_analyzer.py  # NLP content scanning
│   │   ├── yolo_detector.py  # Visual detection
│   │   └── image_analyzer.py # Image processing
│   │
│   ├── models/            # Trained ML models
│   │   └── content_model.joblib
│   │
│   ├── data/              # Training data & brand assets
│   │   ├── brands/        # Reference brand logos
│   │   └── logos/         # YOLO training dataset
│   │
│   ├── scripts/           # Utility scripts
│   │   ├── train_yolo.py
│   │   └── collect_logos.py
│   │
│   └── requirements.txt   # Python dependencies
│
└── docs/                  # Documentation
```

---

## 🔬 How It Works

### **Detection Pipeline**

```
User visits webpage
       ↓
Content script extracts:
  • URL
  • Page text
  • Screenshots
       ↓
Sends to backend API
       ↓
Parallel Analysis:
  ├─ Heuristic (URL patterns)
  ├─ Content (NLP)
  └─ Visual (YOLO)
       ↓
Weighted scoring algorithm
       ↓
Return threat level + details
       ↓
Display results / Block page
```

### **Heuristic Analysis**
Checks for:
- IP addresses in URLs
- Suspicious TLDs (.tk, .ml, .ga)
- Excessive subdomains
- URL length anomalies
- HTTPS presence
- Homograph attacks

### **Content Analysis**
- TF-IDF vectorization of page text
- Trained on 5,000+ phishing/legitimate samples
- Detects urgency keywords, fake forms, suspicious links

### **Visual Detection**
- YOLOv8-based logo detection
- Trained on brand logos (Google, Netflix, PayPal, etc.)
- Compares detected logos with page domain
- Flags brand impersonation attempts

---

## 📊 Performance

- **Detection Accuracy**: ~94% on test dataset
- **False Positive Rate**: <3%
- **Average Scan Time**: <500ms
- **Supported Brands**: 5+ (expandable)

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Add more brand logos** to the YOLO training dataset
2. **Improve heuristic rules** for better detection
3. **Report false positives/negatives** via Issues
4. **Submit test cases** for edge cases

### **Development Workflow**
```bash
# Create a feature branch
git checkout -b feature/your-feature

# Make changes and test
# ...

# Commit and push
git commit -m "Add: your feature description"
git push origin feature/your-feature

# Create a Pull Request
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

PhishGuard is a security tool designed to assist users in identifying potential phishing threats. While it provides strong protection, no system is 100% foolproof. Always exercise caution when:
- Entering sensitive information online
- Clicking links from unknown sources
- Downloading files from untrusted websites

**Use at your own risk.** The developers are not responsible for any damages resulting from the use of this software.

---

## 🙏 Acknowledgments

- **UCI Machine Learning Repository** - Phishing dataset
- **Ultralytics** - YOLOv8 framework
- **FastAPI** - Modern Python web framework
- **Chrome Extension Documentation** - Development resources

---

## 📧 Contact

For questions, suggestions, or bug reports:
- **GitHub Issues**: [Create an issue](https://github.com/rasmusmaria26-cell/PHISHGUARD/issues)
- **Repository**: [PHISHGUARD](https://github.com/rasmusmaria26-cell/PHISHGUARD)

---

**Stay Safe Online! 🛡️**