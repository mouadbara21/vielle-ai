import logging
from bs4 import BeautifulSoup
from readability import Document

logger = logging.getLogger(__name__)

class ArticleScraper:
    def extract(self, html_content: str, url: str = "") -> dict:
        """Extract main content and title using readability-lxml."""
        try:
            doc = Document(html_content)
            title = doc.short_title()
            
            # Use BeautifulSoup to clean the readability output (remove tags)
            summary_html = doc.summary()
            soup = BeautifulSoup(summary_html, "html.parser")
            
            # Remove scripts, styles
            for script in soup(["script", "style", "noscript", "header", "footer", "nav"]):
                script.decompose()

            text = soup.get_text(separator="\n", strip=True)

            return {
                "title": title,
                "content": text,
                "url": url
            }
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return None
