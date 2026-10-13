# nodes/web_crawler.py
import requests
from bs4 import BeautifulSoup
from state import AgentState

def web_crawler(state: AgentState) -> AgentState:
    print("--- WEB CRAWLER: Scraping and filtering web page content ---")
    target_url = state.get("url")
    
    extracted_content = ""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(target_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove common non-content elements to reduce noise
            for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                element.decompose()
                
            # Extract text from semantic content tags or paragraphs
            text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'article', 'section'])
            
            if text_elements:
                extracted_content = "\n".join([elem.get_text(strip=True) for elem in text_elements if elem.get_text(strip=True)])
            else:
                # Fallback to general body text if specific tags aren't found
                extracted_content = soup.get_text(separator='\n', strip=True)
                
            print("Successfully crawled and extracted web content.")
        else:
            extracted_content = f"Failed to retrieve web page. Status code: {response.status_code}"
            
    except Exception as e:
        print(f"Error during web crawling: {e}")
        extracted_content = "Error processing web content extraction."
        
    return {
        "content": extracted_content
    }