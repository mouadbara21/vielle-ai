import logging
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

class WebCrawler:
    def __init__(self, timeout=10):
        self.timeout = timeout
        self.client = httpx.Client(timeout=self.timeout, follow_redirects=True)
        self.headers = {
            "User-Agent": "VeilleAI-Bot/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
        }

    def crawl(self, start_url: str, max_pages: int = 10) -> list[dict]:
        """Crawl starting from a URL and return a list of page dicts with 'url' and 'html'."""
        visited = set()
        queue = [start_url]
        pages = []
        base_domain = urlparse(start_url).netloc

        while queue and len(pages) < max_pages:
            url = queue.pop(0)
            if url in visited:
                continue

            try:
                logger.info(f"Crawling URL: {url}")
                response = self.client.get(url, headers=self.headers)
                visited.add(url)

                if response.status_code == 200 and "text/html" in response.headers.get("Content-Type", ""):
                    html_content = response.text
                    pages.append({"url": url, "html": html_content})

                    # Extract more links if we need more pages
                    if len(pages) < max_pages:
                        soup = BeautifulSoup(html_content, "html.parser")
                        for link in soup.find_all("a", href=True):
                            next_url = urljoin(url, link["href"])
                            if urlparse(next_url).netloc == base_domain and next_url not in visited:
                                queue.append(next_url)
            except Exception as e:
                logger.error(f"Error crawling {url}: {e}")
                visited.add(url)

        return pages

    def close(self):
        self.client.close()
