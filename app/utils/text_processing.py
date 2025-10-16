import requests
from bs4 import BeautifulSoup

def fetch_url(url, timeout=10):
    """Fetch raw HTML from a URL."""
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.text

def extract_main_text(html):
    """Extract main textual content from HTML."""
    soup = BeautifulSoup(html, "html.parser")

    # Remove scripts, styles, and irrelevant tags
    for tag in soup(["script", "style", "header", "footer", "nav"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)

def chunk_text(text, chunk_size=400, overlap=50):
    """Split text into chunks with some overlap (token-based or approx by words)."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap  # overlap words
    return chunks
