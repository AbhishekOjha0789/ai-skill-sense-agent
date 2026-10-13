# nodes/image_crawler.py
import requests
from io import BytesIO
from PIL import Image
import pytesseract
from state import AgentState

def image_crawler(state: AgentState) -> AgentState:
    print("--- IMAGE CRAWLER: Extracting text from image (OCR) ---")
    target_url = state.get("url")
    
    extracted_text = ""
    try:
        # 1. Download the image from the URL
        response = requests.get(target_url, timeout=10)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            
            # 2. Use Tesseract OCR to extract text directly from the image
            extracted_text = pytesseract.image_to_string(image)
            print("Successfully extracted text via OCR.")
        else:
            extracted_text = "Failed to download image for OCR."
            
    except Exception as e:
        print(f"Error during image OCR extraction: {e}")
        extracted_text = "Error extracting text from image."
        
    return {
        "content": extracted_text.strip()
    }