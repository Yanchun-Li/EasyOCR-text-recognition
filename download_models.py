import urllib.request
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def download_models():
    MODEL_DIR = './models'
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    # EasyOCR model file URLs (updated)
    model_urls = {
        'craft_st.pth': 'https://huggingface.co/spaces/JaidedAI/EasyOCR/resolve/main/craft_st.pth',
        'english_g2.pth': 'https://huggingface.co/spaces/JaidedAI/EasyOCR/resolve/main/english_g2.pth'
    }
    
    for filename, url in model_urls.items():
        filepath = os.path.join(MODEL_DIR, filename)
        if not os.path.exists(filepath):
            logging.info(f"Downloading {filename}...")
            try:
                urllib.request.urlretrieve(url, filepath)
                logging.info(f"Successfully downloaded {filename}")
            except Exception as e:
                logging.error(f"Error downloading {filename}: {str(e)}")
        else:
            logging.info(f"{filename} already exists, skipping download")

if __name__ == "__main__":
    download_models() 