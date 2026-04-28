import logging
import feedparser
from datetime import datetime
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)

class RSSCollector:
    def __init__(self, timeout=10):
        self.timeout = timeout
        # Using a custom user-agent could be helpful, but feedparser handles most
        self.user_agent = "VeilleAI-Bot/1.0"

    def collect(self, feed_url: str, max_items: int = 20) -> list[dict]:
        """Fetch an RSS feed and return a list of page dicts mimicking crawler output."""
        logger.info(f"Collecting RSS feed: {feed_url}")
        try:
            # feedparser can take URL directly
            feed = feedparser.parse(feed_url, agent=self.user_agent)
            
            if feed.bozo and feed.bozo_exception:
                logger.warning(f"Feed parser bozo exception on {feed_url}: {feed.bozo_exception}")
                # Sometimes it parses valid entries despite the bozo exception
                
            pages = []
            for entry in feed.entries[:max_items]:
                url = entry.get("link", "")
                title = entry.get("title", "")
                
                # Content can be in 'content' or 'summary'
                content = ""
                if "content" in entry and len(entry.content) > 0:
                    content = entry.content[0].value
                elif "summary" in entry:
                    content = entry.summary
                elif "description" in entry:
                    content = entry.description
                    
                # We also embed title into html so that ArticleScraper or downstream
                # can process it if they want raw html. But if we return already 
                # extracted content, we might bypass ArticleScraper.
                # To be compatible with crawl_tasks.py logic which expects `html` 
                # and later uses ArticleScraper:
                
                html_content = f"<html><head><title>{title}</title></head><body>{content}</body></html>"
                
                if url and content:
                    pages.append({
                        "url": url,
                        "title": title,
                        "html": html_content,
                    })

            return pages
        except Exception as e:
            logger.error(f"Error collecting RSS feed {feed_url}: {e}")
            return []
