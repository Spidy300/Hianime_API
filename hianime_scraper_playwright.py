"""
HiAnime.to Playwright Scraper - Browser Automation Implementation
=================================================================
A Playwright-based scraper for handling JavaScript-rendered content

Author: Senior Web Scraping Engineer
Version: 1.0.0
Date: December 2024

Features:
- Full browser automation with Playwright
- JavaScript rendering support
- Dynamic content handling
- Stealth mode with fingerprint randomization
- Cookie and session management
"""

import asyncio
import random
import logging
import json
from typing import Optional, List, Dict, Any
from dataclasses import asdict
from pathlib import Path

try:
    from playwright.async_api import async_playwright, Browser, Page, BrowserContext
except ImportError:
    print("Please install playwright: pip install playwright")
    print("Then run: playwright install chromium")
    raise

from hianime_scraper import AnimeInfo, SearchResult, Episode, ScraperConfig, ParserUtils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StealthConfig:
    """Browser stealth configuration"""
    
    VIEWPORTS = [
        {"width": 1920, "height": 1080},
        {"width": 1366, "height": 768},
        {"width": 1536, "height": 864},
        {"width": 1440, "height": 900},
        {"width": 1280, "height": 720},
    ]
    
    LOCALES = ["en-US", "en-GB", "en-CA"]
    
    TIMEZONES = [
        "America/New_York",
        "America/Los_Angeles", 
        "America/Chicago",
        "Europe/London",
    ]


class PlaywrightHiAnimeScraper:
    """Playwright-based scraper for HiAnime.to"""
    
    def __init__(
        self,
        headless: bool = True,
        slow_mo: int = 100,
        proxy: Optional[str] = None,
        save_state: bool = False
    ):
        """
        Initialize Playwright scraper
        
        Args:
            headless: Run browser in headless mode
            slow_mo: Slow down operations by ms
            proxy: Proxy server URL
            save_state: Save browser state for reuse
        """
        self.base_url = ScraperConfig.BASE_URL
        self.headless = headless
        self.slow_mo = slow_mo
        self.proxy = proxy
        self.save_state = save_state
        self.state_path = Path("browser_state.json")
        
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
    
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def start(self):
        """Start browser"""
        self._playwright = await async_playwright().start()
        
        # Browser launch options
        launch_options = {
            "headless": self.headless,
            "slow_mo": self.slow_mo,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ]
        }
        
        if self.proxy:
            launch_options["proxy"] = {"server": self.proxy}
        
        self._browser = await self._playwright.chromium.launch(**launch_options)
        
        # Create stealth context
        viewport = random.choice(StealthConfig.VIEWPORTS)
        locale = random.choice(StealthConfig.LOCALES)
        timezone = random.choice(StealthConfig.TIMEZONES)
        
        context_options = {
            "viewport": viewport,
            "locale": locale,
            "timezone_id": timezone,
            "user_agent": random.choice(ScraperConfig.USER_AGENTS),
            "java_script_enabled": True,
        }
        
        # Load saved state if available
        if self.save_state and self.state_path.exists():
            context_options["storage_state"] = str(self.state_path)
        
        self._context = await self._browser.new_context(**context_options)
        
        # Add stealth scripts
        await self._context.add_init_script("""
            // Mask webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Mock plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Mock languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)
        
        self._page = await self._context.new_page()
        
        logger.info("Browser started successfully")
    
    async def close(self):
        """Close browser and save state"""
        if self.save_state and self._context:
            await self._context.storage_state(path=str(self.state_path))
            logger.info("Browser state saved")
        
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        
        logger.info("Browser closed")
    
    async def _navigate(self, url: str, wait_selector: str = ".flw-item"):
        """Navigate to URL and wait for content"""
        await self._page.goto(url, wait_until="domcontentloaded")
        
        try:
            await self._page.wait_for_selector(wait_selector, timeout=10000)
        except Exception:
            logger.warning(f"Selector {wait_selector} not found, continuing anyway")
        
        # Random delay to mimic human behavior
        await asyncio.sleep(random.uniform(1.0, 2.0))
    
    async def _get_page_content(self) -> str:
        """Get current page HTML content"""
        return await self._page.content()
    
    async def _parse_anime_list(self) -> List[SearchResult]:
        """Parse anime list from current page"""
        content = await self._get_page_content()
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        
        results = []
        anime_items = soup.select('.flw-item')
        
        for item in anime_items:
            try:
                title_elem = item.select_one('.film-name a')
                if not title_elem:
                    continue
                
                title = ParserUtils.clean_text(title_elem.text)
                href = title_elem.get('href', '')
                anime_url = f"{self.base_url}{href}" if href.startswith('/') else href
                anime_id = ParserUtils.extract_anime_id(href)
                
                img_elem = item.select_one('.film-poster img')
                thumbnail = img_elem.get('data-src') or img_elem.get('src') if img_elem else None
                
                type_elem = item.select_one('.fdi-item')
                anime_type = ParserUtils.clean_text(type_elem.text) if type_elem else None
                
                sub_elem = item.select_one('.tick-sub')
                dub_elem = item.select_one('.tick-dub')
                
                results.append(SearchResult(
                    title=title,
                    url=anime_url,
                    id=anime_id,
                    thumbnail=thumbnail,
                    type=anime_type,
                    episodes_sub=ParserUtils.parse_episode_count(sub_elem.text if sub_elem else ""),
                    episodes_dub=ParserUtils.parse_episode_count(dub_elem.text if dub_elem else "")
                ))
                
            except Exception as e:
                logger.warning(f"Failed to parse item: {e}")
                continue
        
        return results
    
    # =========================================================================
    # SEARCH METHODS
    # =========================================================================
    
    async def search(self, keyword: str, page: int = 1) -> List[SearchResult]:
        """Search for anime"""
        url = f"{self.base_url}/search?keyword={keyword}&page={page}"
        await self._navigate(url)
        return await self._parse_anime_list()
    
    async def advanced_filter(
        self,
        type_: Optional[str] = None,
        status: Optional[str] = None,
        rated: Optional[str] = None,
        score: Optional[str] = None,
        season: Optional[str] = None,
        language: Optional[str] = None,
        genres: Optional[List[str]] = None,
        sort: str = "default",
        page: int = 1
    ) -> List[SearchResult]:
        """Advanced filter search"""
        params = []
        
        if type_:
            params.append(f"type={type_}")
        if status:
            params.append(f"status={status}")
        if rated:
            params.append(f"rated={rated}")
        if score:
            params.append(f"score={score}")
        if season:
            params.append(f"season={season}")
        if language:
            params.append(f"language={language}")
        if genres:
            for genre in genres:
                params.append(f"genres={genre}")
        if sort:
            params.append(f"sort={sort}")
        
        params.append(f"page={page}")
        
        url = f"{self.base_url}/filter?{'&'.join(params)}"
        await self._navigate(url)
        return await self._parse_anime_list()
    
    # =========================================================================
    # BROWSE METHODS
    # =========================================================================
    
    async def get_most_popular(self, page: int = 1) -> List[SearchResult]:
        """Get most popular anime"""
        url = f"{self.base_url}/most-popular?page={page}"
        await self._navigate(url)
        return await self._parse_anime_list()
    
    async def get_top_airing(self, page: int = 1) -> List[SearchResult]:
        """Get top airing anime"""
        url = f"{self.base_url}/top-airing?page={page}"
        await self._navigate(url)
        return await self._parse_anime_list()
    
    async def get_by_genre(self, genre: str, page: int = 1) -> List[SearchResult]:
        """Get anime by genre"""
        url = f"{self.base_url}/genre/{genre}?page={page}"
        await self._navigate(url)
        return await self._parse_anime_list()
    
    async def get_by_type(self, type_: str, page: int = 1) -> List[SearchResult]:
        """Get anime by type (movie, tv, ova, etc.)"""
        url = f"{self.base_url}/{type_}?page={page}"
        await self._navigate(url)
        return await self._parse_anime_list()
    
    # =========================================================================
    # DETAIL METHODS
    # =========================================================================
    
    async def get_anime_details(self, slug: str) -> Optional[AnimeInfo]:
        """Get full anime details"""
        url = f"{self.base_url}/{slug}"
        await self._navigate(url, wait_selector=".film-name")
        
        content = await self._get_page_content()
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        
        try:
            title_elem = soup.select_one('.film-name')
            title = ParserUtils.clean_text(title_elem.text) if title_elem else ""
            
            synopsis_elem = soup.select_one('.film-description .text')
            synopsis = ParserUtils.clean_text(synopsis_elem.text) if synopsis_elem else ""
            
            extracted_id = ParserUtils.extract_anime_id(slug)
            
            # Parse info
            info_items = soup.select('.anisc-info .item')
            genres = []
            studios = []
            status = None
            anime_type = None
            
            for item in info_items:
                label = item.select_one('.item-head')
                if not label:
                    continue
                    
                label_text = label.text.lower()
                
                if "genres" in label_text:
                    genre_links = item.select('a')
                    genres = [ParserUtils.clean_text(g.text) for g in genre_links]
                elif "studios" in label_text:
                    studio_links = item.select('a')
                    studios = [ParserUtils.clean_text(s.text) for s in studio_links]
                elif "status" in label_text:
                    status = ParserUtils.clean_text(item.select_one('.name').text if item.select_one('.name') else "")
                elif "type" in label_text:
                    anime_type = ParserUtils.clean_text(item.select_one('.name').text if item.select_one('.name') else "")
            
            sub_elem = soup.select_one('.tick-sub')
            dub_elem = soup.select_one('.tick-dub')
            
            return AnimeInfo(
                id=extracted_id,
                slug=slug,
                title=title,
                url=url,
                synopsis=synopsis,
                genres=genres,
                studios=studios,
                status=status,
                type=anime_type,
                episodes_sub=ParserUtils.parse_episode_count(sub_elem.text if sub_elem else ""),
                episodes_dub=ParserUtils.parse_episode_count(dub_elem.text if dub_elem else "")
            )
            
        except Exception as e:
            logger.error(f"Failed to parse anime details: {e}")
            return None
    
    async def get_episode_list(self, slug: str) -> List[Episode]:
        """Get episode list for an anime (requires JavaScript)"""
        url = f"{self.base_url}/watch/{slug}"
        await self._navigate(url, wait_selector=".ss-list")
        
        # Wait for episode list to load
        await asyncio.sleep(1)
        
        content = await self._get_page_content()
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        
        episodes = []
        episode_items = soup.select('.ss-list a')
        
        for item in episode_items:
            try:
                ep_num_elem = item.get('data-number')
                ep_title = item.get('title', '')
                ep_href = item.get('href', '')
                
                episodes.append(Episode(
                    number=int(ep_num_elem) if ep_num_elem else 0,
                    title=ParserUtils.clean_text(ep_title),
                    url=f"{self.base_url}{ep_href}" if ep_href.startswith('/') else ep_href
                ))
                
            except Exception as e:
                logger.warning(f"Failed to parse episode: {e}")
                continue
        
        return episodes
    
    # =========================================================================
    # SCREENSHOT & DEBUG
    # =========================================================================
    
    async def screenshot(self, path: str = "screenshot.png"):
        """Take screenshot of current page"""
        await self._page.screenshot(path=path, full_page=True)
        logger.info(f"Screenshot saved to {path}")
    
    async def save_html(self, path: str = "page.html"):
        """Save current page HTML"""
        content = await self._get_page_content()
        Path(path).write_text(content)
        logger.info(f"HTML saved to {path}")


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

async def main():
    """Example Playwright usage"""
    
    print("=== Playwright HiAnime Scraper ===\n")
    
    async with PlaywrightHiAnimeScraper(
        headless=True,
        slow_mo=50,
        save_state=True
    ) as scraper:
        
        # Search example
        print("Searching for 'naruto'...")
        results = await scraper.search("naruto")
        print(f"Found {len(results)} results")
        for r in results[:3]:
            print(f"  - {r.title}")
        
        # Get details
        if results:
            print(f"\nGetting details for: {results[0].title}")
            slug = results[0].url.split('/')[-1]
            details = await scraper.get_anime_details(slug)
            if details:
                print(f"  Synopsis: {details.synopsis[:100]}...")
                print(f"  Genres: {', '.join(details.genres)}")
        
        # Get popular
        print("\nGetting most popular...")
        popular = await scraper.get_most_popular()
        print(f"Found {len(popular)} popular anime")
        
        # Take screenshot for debugging
        await scraper.screenshot("hianime_screenshot.png")


if __name__ == "__main__":
    asyncio.run(main())
