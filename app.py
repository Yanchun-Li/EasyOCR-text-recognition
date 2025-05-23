import os
import sys
import logging
import traceback
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
from werkzeug.utils import secure_filename
from model_loader import CustomModelLoader
import easyocr

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # 改为DEBUG级别以获取更多信息
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Check GPU availability
device = 'cuda' if torch.cuda.is_available() else 'cpu'
logger.info(f"Using device: {device}")

# Initialize EasyOCR
try:
    logger.info("Initializing EasyOCR...")
    easyocr_reader = easyocr.Reader(['en'], gpu=(device=='cuda'))
    logger.info("EasyOCR initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize EasyOCR: {str(e)}")
    logger.error(traceback.format_exc())
    raise

# Initialize local model
try:
    logger.info("Initializing local model...")
    model_loader = CustomModelLoader()
    logger.info("Local model initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize local model: {str(e)}")
    logger.error(traceback.format_exc())
    raise

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'status': 'ok',
        'message': 'OCR API is running',
        'endpoints': {
            '/ocr': 'POST - Upload an image for OCR processing'
        }
    })

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_numpy_types(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_types(item) for item in obj)
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    else:
        return obj

@app.route('/ocr', methods=['POST'])
def ocr():
    try:
        logger.info("Received OCR request")
        if 'file' not in request.files:
            logger.error("No file part in request")
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        logger.info(f"Received file: {file.filename}")
        
        if file.filename == '':
            logger.error("No selected file")
            return jsonify({'error': 'No selected file'}), 400
        
        # Get OCR engine type from request
        ocr_engine = request.form.get('engine', 'local')  # Default to local model
        logger.info(f"Using OCR engine: {ocr_engine}")
        
        if file and allowed_file(file.filename):
            try:
                # Save file temporarily
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                logger.info(f"File saved to: {filepath}")
                
                # Process image based on selected OCR engine
                if ocr_engine == 'easyocr':
                    # Use EasyOCR
                    logger.info("Starting OCR processing with EasyOCR...")
                    results = easyocr_reader.readtext(filepath)
                    logger.info(f"OCR completed, found {len(results)} text regions")
                    
                    # Format results
                    formatted_results = []
                    for detection in results:
                        bbox, text, confidence = detection
                        formatted_results.append({
                            'text': text,
                            'confidence': round(float(confidence) * 100, 2),
                            'bbox': convert_numpy_types(bbox)
                        })
                else:
                    # Use local model
                    logger.info("Starting OCR processing with local model...")
                    results = model_loader.predict(filepath)
                    logger.info("OCR completed with local model")
                    
                    # Format results to match EasyOCR format
                    formatted_results = []
                    for item in results:
                        formatted_results.append({
                            'text': item['text'],
                            'confidence': item['confidence'],
                            'bbox': None  # Local model doesn't provide bounding boxes
                        })
                
                # Clean up
                os.remove(filepath)
                logger.info("Temporary file removed")
                
                return jsonify({
                    'success': True,
                    'result': formatted_results,
                    'engine': ocr_engine
                })
                
            except Exception as e:
                logger.error(f"Error processing image: {str(e)}")
                logger.error(traceback.format_exc())
                return jsonify({'error': f'Error processing image: {str(e)}'}), 500
        else:
            logger.error(f"Invalid file type: {file.filename}")
            return jsonify({'error': 'Invalid file type'}), 400
            
    except Exception as e:
        logger.error(f"Unexpected error in OCR endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True) 