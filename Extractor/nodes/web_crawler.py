import requests
from bs4 import BeautifulSoup
from state import AgentState

# Configure your backend API base URL (update as needed for deployment)
BACKEND_API_URL = "https://your-backend-api.com"

def web_crawler(state: AgentState) -> AgentState:
    print("--- WEB CRAWLER: Scraping and filtering web page content ---")
    target_url = state.get("url")
    
    extracted_content = ""
    discovered_urls = []
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(target_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # --- NEW FEATURE: Extract all valid links from the page ---
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('http://') or href.startswith('https://'):
                    discovered_urls.append(href)
            
            # Deduplicate discovered URLs
            unique_discovered_urls = list(set(discovered_urls))
            
            # Send discovered URLs to the backend to check/add them to the database
            for d_url in unique_discovered_urls:
                try:
                    # Calls backend API endpoint to look up or register the URL record ID
                    res = requests.post(
                        f"{BACKEND_API_URL}/api/urls/get-id",
                        json={"url": d_url},
                        timeout=3
                    )
                    if res.status_code in [200, 201]:
                        print(f"Synced discovered URL with backend: {d_url}")
                except Exception as backend_err:
                    print(f"Warning: Could not sync URL {d_url} to backend: {backend_err}")
            
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