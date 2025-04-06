# OCR Text Recognition

A modern web application for Optical Character Recognition (OCR) that combines the power of EasyOCR with a beautiful React frontend. This application allows users to extract text from images with confidence level visualization and choose between different OCR engines.


## Features

- **Modern UI/UX**
  - Clean and intuitive interface
  - Drag & drop image upload
  - Real-time image preview
  - Responsive design for all devices
  - OCR engine selection (Local Model or EasyOCR)

- **Text Recognition**
  - High-accuracy text extraction
  - Confidence level visualization
  - Color-coded results
  - Maintains text layout and structure
  - Multiple OCR engine support

- **Performance**
  - GPU acceleration support
  - Fast processing
  - Efficient memory usage

## Tech Stack

### Frontend
- **React.js** - Modern UI framework
- **Material-UI** - Component library
- **Axios** - HTTP client

### Backend
- **Flask** - Python web framework
- **EasyOCR** - OCR engine
- **PyTorch** - Deep learning framework
- **Custom OCR Model** - Local trained model

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Yanchun-Li/EasyOCR-text-recognition.git
cd EasyOCR-text-recognition
```

2. **Set up Python environment**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

3. **Set up React frontend**
```bash
cd ocr-frontend
npm install
```

### Running the Application

1. **Start the backend server**
```bash
# From the root directory
python app.py
```

2. **Start the frontend development server**
```bash
# From the ocr-frontend directory
cd ocr-frontend
npm start
```

3. **Access the application**
Open your browser and visit `http://localhost:3000`

## Usage Guide

1. **Select OCR Engine**
   - Choose between "Local Model" or "EasyOCR"
   - Local Model: Uses a custom-trained model
   - EasyOCR: Uses the pre-trained EasyOCR model

2. **Upload an Image**
   - Drag and drop an image onto the upload area
   - Or click to select a file from your computer

3. **View Results**
   - See the original image preview
   - View recognized text with confidence levels
   - Check which OCR engine was used
   - Check the confidence indicator:
     - Green: High confidence (100%)
     - Yellow: Medium confidence (50%)
     - Red: Low confidence (0%)

## Project Structure

```
ocr-text-recognition/
├── app.py                 # Flask backend
├── requirements.txt       # Python dependencies
├── model_loader.py        # Custom model loader
├── custom_example.py      # Custom model definition
├── uploads/              # Temporary upload directory
└── ocr-frontend/         # React frontend
    ├── src/
    │   ├── components/   # React components
    │   ├── App.js        # Main application
    │   └── index.js      # Entry point
    └── package.json      # Node dependencies
```

## API Documentation

### POST /ocr
Process an image and extract text.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: 
  - `file` (image file)
  - `engine` (optional, default: "local") - "local" or "easyocr"

**Response:**
```json
{
  "success": true,
  "result": [
    {
      "text": "recognized text",
      "confidence": 95.5,
      "bbox": [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
    }
  ],
  "engine": "local"
}
```

## Author

**Yanchun Li**
- GitHub: [@Yanchun-Li](https://github.com/Yanchun-Li) 