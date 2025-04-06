from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from PIL import Image
import numpy as np
import easyocr
import torch
import uuid
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Ensure upload folder exists
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Check GPU availability
gpu_available = torch.cuda.is_available()
logger.info(f"GPU available: {gpu_available}")
if gpu_available:
    logger.info(f"GPU device: {torch.cuda.get_device_name(0)}")

# Initialize EasyOCR
logger.info("Initializing EasyOCR...")
reader = easyocr.Reader(['en'], gpu=gpu_available)  # Use English model with GPU if available
logger.info("EasyOCR initialized successfully")

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super(NumpyEncoder, self).default(obj)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/ocr', methods=['POST'])
def ocr_endpoint():
    logger.info("Received OCR request")
    
    if 'image' not in request.files:
        logger.error("No image file in request")
        return jsonify({'error': 'No uploaded image'}), 400
    
    file = request.files['image']
    if file.filename == '':
        logger.error("No selected file")
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        # Generate unique filename to avoid conflicts
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = str(uuid.uuid4()) + file_extension
        filename = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        try:
            # Save uploaded file
            file.save(filename)
            logger.info(f"Saved file: {filename}")
            
            # Open image and convert to RGB
            image = Image.open(filename).convert('RGB')
            logger.info(f"Image opened successfully, size: {image.size}")
            
            # Perform OCR
            logger.info("Starting OCR processing...")
            result = reader.readtext(np.array(image))
            logger.info(f"OCR completed, found {len(result)} text regions")
            
            # Process results
            processed_results = []
            for detection in result:
                bbox, text, confidence = detection
                # Calculate text position (center of bounding box)
                y_center = (bbox[0][1] + bbox[2][1]) / 2
                # Get x position (left boundary)
                x_start = bbox[0][0]
                
                processed_results.append({
                    'text': str(text),
                    'confidence': float(confidence),
                    'position': {
                        'x': float(x_start),
                        'y': float(y_center)
                    }
                })
            
            # Sort and group text by vertical position
            y_threshold = 10  # Threshold for considering text on the same line
            processed_results.sort(key=lambda x: (x['position']['y'], x['position']['x']))
            
            # Group processing
            lines = []
            current_line = []
            last_y = None
            
            for item in processed_results:
                current_y = item['position']['y']
                if last_y is None or abs(current_y - last_y) <= y_threshold:
                    current_line.append(item)
                else:
                    if current_line:
                        # Sort current line by x position
                        current_line.sort(key=lambda x: x['position']['x'])
                        lines.append(current_line)
                    current_line = [item]
                last_y = current_y
            
            if current_line:
                current_line.sort(key=lambda x: x['position']['x'])
                lines.append(current_line)
            
            # Clean up temporary file
            try:
                os.remove(filename)
                logger.info("Temporary file cleaned up")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file: {str(e)}")
            
            # Return response
            response = {
                'lines': lines,
                'success': True
            }
            
            logger.info(f"Returning response with {len(lines)} lines")
            return app.response_class(
                response=json.dumps(response, cls=NumpyEncoder),
                status=200,
                mimetype='application/json'
            )
            
        except Exception as e:
            # Clean up temporary file on error
            try:
                os.remove(filename)
                logger.info("Temporary file cleaned up after error")
            except:
                pass
            error_msg = f"OCR processing error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return jsonify({
                'error': error_msg,
                'success': False
            }), 500

if __name__ == '__main__':
    app.run(debug=True) 