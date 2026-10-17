import os
import requests
from bs4 import BeautifulSoup
from ..state import AgentState

# Fetch backend URL and agent secret from environment
BACKEND_API_URL = os.environ.get("BACKEND_API_URL")
AGENT_SECRET_KEY = os.environ.get("AGENT_SECRET_KEY")

def web_crawler(state: AgentState) -> AgentState:
    print("--- WEB CRAWLER: Scraping and filtering web page content ---")
    target_url = state.get("url")
    if not BACKEND_API_URL:
        raise RuntimeError("BACKEND_API_URL environment variable is missing.")
    if not AGENT_SECRET_KEY:
        raise RuntimeError("AGENT_SECRET_KEY environment variable is missing.")
    
    extracted_content = ""
    discovered_urls = []
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(target_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # --- Extract all valid links from the page ---
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('http://') or href.startswith('https://'):
                    discovered_urls.append(href)
            
            # Deduplicate discovered URLs
            unique_discovered_urls = list(set(discovered_urls))
            
            # Send discovered URLs to the backend with the internal agent secret header
            crawler_headers = {"X-Agent-Secret": AGENT_SECRET_KEY}

            for d_url in unique_discovered_urls:
                try:
                    res = requests.post(
                        f"{BACKEND_API_URL}/api/urls/get-id",
                        json={"url": d_url},
                        headers=crawler_headers,
                        timeout=40,
                    )
                    res.raise_for_status()
                    print(f"Synced discovered URL with backend: {d_url}")
                except Exception as backend_err:
                    raise RuntimeError(
                        f"Could not sync discovered URL {d_url} to backend."
                    ) from backend_err
            
            # Remove common non-content elements to reduce noise
            for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                element.decompose()
                
            # Extract text from semantic content tags or paragraphs
            text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'article', 'section'])
            
            if text_elements:
                extracted_content = "\n".join([elem.get_text(strip=True) for elem in text_elements if elem.get_text(strip=True)])
            else:
                extracted_content = soup.get_text(separator='\n', strip=True)
                
            print("Successfully crawled and extracted web content.")
        else:
            extracted_content = f"Failed to retrieve web page. Status code: {response.status_code}"
            
    except RuntimeError:
        raise
    except Exception as e:
        print(f"Error during web crawling: {e}")
        extracted_content = "Error processing web content extraction."
        
    return {
        "content": extracted_content
    }