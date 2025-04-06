# OCR Text Recognition

A web-based OCR (Optical Character Recognition) application that recognizes text from images with confidence level visualization.

## Features

- Upload images via drag & drop or click
- Real-time text recognition
- Confidence level visualization with color coding
- Maintains original text layout
- GPU acceleration support (if available)

## Technologies

- Backend:
  - Flask (Python web framework)
  - EasyOCR (OCR engine)
  - PyTorch (Deep learning framework)
  
- Frontend:
  - HTML5
  - CSS3
  - JavaScript (ES6+)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/ocr-text-recognition.git
cd ocr-text-recognition
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and visit `http://localhost:5000`

## Usage

1. Open the web interface
2. Upload an image by clicking the upload area or dragging and dropping
3. Wait for the processing to complete
4. View the recognized text with confidence levels indicated by colors:
   - Green: High confidence (100%)
   - Yellow: Medium confidence (50%)
   - Red: Low confidence (0%)

## Project Structure

```
ocr-text-recognition/
├── app.py              # Flask application
├── requirements.txt    # Python dependencies
├── templates/         
│   └── index.html     # Frontend template
└── uploads/           # Temporary folder for uploads
```

## License

MIT License 