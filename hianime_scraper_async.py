"""
HiAnime.to Async Web Scraper - High-Performance Implementation
==============================================================
An asynchronous scraper for high-volume data extraction from HiAnime.to

Author: Senior Web Scraping Engineer
Version: 1.0.0
Date: December 2024

Features:
- Async HTTP requests with aiohttp
- Concurrent page scraping
- Semaphore-based rate limiting
- Connection pooling
"""

import asyncio
import aiohttp
import random
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# Import shared models and utilities from main scraper
from hianime_scraper import (
    AnimeInfo, 
    SearchResult, 
    ScraperConfig, 
    ParserUtils
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AsyncHiAnimeScraper:
    """Async implementation of HiAnime scraper for high-performance scraping"""
    
    def __init__(
        self,
        max_concurrent: int = 5,
        delay: float = 1.0,
        proxies: Optional[List[str]] = None
    ):
        """
        Initialize async scraper
        
        Args:
            max_concurrent: Maximum concurrent requests
            delay: Delay between batches (seconds)
            proxies: List of proxy URLs
        """
        self.base_url = ScraperConfig.BASE_URL
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.delay = delay
        self.proxies = proxies or []
        self.proxy_index = 0
        
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with random user agent"""
        return {
            "User-Agent": random.choice(ScraperConfig.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
        }
    
    def _get_proxy(self) -> Optional[str]:
        """Get next proxy from rotation"""
        if not self.proxies:
            return None
        proxy = self.proxies[self.proxy_index]
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    async def _fetch(
        self, 
        session: aiohttp.ClientSession, 
        url: str,
        params: Optional[Dict] = None
    ) -> str:
        """Fetch URL with rate limiting"""
        async with self.semaphore:
            proxy = self._get_proxy()
            
            try:
                async with session.get(
                    url,
                    params=params,
                    headers=self._get_headers(),
                    proxy=proxy,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response.raise_for_status()
                    return await response.text()
                    
            except Exception as e:
                logger.error(f"Failed to fetch {url}: {e}")
                return ""
            
            finally:
                # Apply delay
                await asyncio.sleep(self.delay)
    
    async def _get_soup(
        self, 
        session: aiohttp.ClientSession, 
        url: str,
        params: Optional[Dict] = None
    ) -> BeautifulSoup:
        """Get BeautifulSoup object from URL"""
        html = await self._fetch(session, url, params)
        return BeautifulSoup(html, 'html.parser') if html else BeautifulSoup("", 'html.parser')
    
    def _parse_anime_list(self, soup: BeautifulSoup) -> List[SearchResult]:
        """Parse anime list from page (same as sync version)"""
        results = []
        anime_items = soup.select('.flw-item')
        
        for item in anime_items:
            try:
                title_elem = item.select_one('.film-name a')
                if not title_elem:
                    continue
                
                title = ParserUtils.clean_text(title_elem.text)
                href = title_elem.get('href', '')
                anime_url = urljoin(self.base_url, href)
                anime_id = ParserUtils.extract_anime_id(href)
                
                img_elem = item.select_one('.film-poster img')
                thumbnail = img_elem.get('data-src') or img_elem.get('src') if img_elem else None
                
                type_elem = item.select_one('.fdi-item')
                anime_type = ParserUtils.clean_text(type_elem.text) if type_elem else None
                
                duration_elem = item.select_one('.fdi-duration')
                duration = ParserUtils.clean_text(duration_elem.text) if duration_elem else None
                
                sub_elem = item.select_one('.tick-sub')
                dub_elem = item.select_one('.tick-dub')
                
                results.append(SearchResult(
                    title=title,
                    url=anime_url,
                    id=anime_id,
                    thumbnail=thumbnail,
                    type=anime_type,
                    duration=duration,
                    episodes_sub=ParserUtils.parse_episode_count(sub_elem.text if sub_elem else ""),
                    episodes_dub=ParserUtils.parse_episode_count(dub_elem.text if dub_elem else "")
                ))
                
            except Exception as e:
                logger.warning(f"Failed to parse anime item: {e}")
                continue
        
        return results
    
    # =========================================================================
    # ASYNC SEARCH METHODS
    # =========================================================================
    
    async def search(
        self,
        keyword: str,
        page: int = 1
    ) -> List[SearchResult]:
        """Search for anime by keyword"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/search"
            soup = await self._get_soup(session, url, {"keyword": keyword, "page": page})
            return self._parse_anime_list(soup)
    
    async def search_multiple_pages(
        self,
        keyword: str,
        pages: List[int]
    ) -> List[SearchResult]:
        """Search multiple pages concurrently"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for page in pages:
                url = f"{self.base_url}/search"
                task = self._get_soup(session, url, {"keyword": keyword, "page": page})
                tasks.append(task)
            
            soups = await asyncio.gather(*tasks)
            
            all_results = []
            for soup in soups:
                all_results.extend(self._parse_anime_list(soup))
            
            return all_results
    
    # =========================================================================
    # ASYNC BROWSE METHODS
    # =========================================================================
    
    async def get_most_popular(self, page: int = 1) -> List[SearchResult]:
        """Get most popular anime"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/most-popular"
            soup = await self._get_soup(session, url, {"page": page})
            return self._parse_anime_list(soup)
    
    async def get_top_airing(self, page: int = 1) -> List[SearchResult]:
        """Get top airing anime"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/top-airing"
            soup = await self._get_soup(session, url, {"page": page})
            return self._parse_anime_list(soup)
    
    async def get_by_genre(self, genre: str, page: int = 1) -> List[SearchResult]:
        """Get anime by genre"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/genre/{genre}"
            soup = await self._get_soup(session, url, {"page": page})
            return self._parse_anime_list(soup)
    
    # =========================================================================
    # BULK ASYNC OPERATIONS
    # =========================================================================
    
    async def scrape_genre_multiple_pages(
        self,
        genre: str,
        pages: List[int]
    ) -> List[SearchResult]:
        """Scrape multiple pages of a genre concurrently"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for page in pages:
                url = f"{self.base_url}/genre/{genre}"
                task = self._get_soup(session, url, {"page": page})
                tasks.append(task)
            
            soups = await asyncio.gather(*tasks)
            
            all_results = []
            for soup in soups:
                all_results.extend(self._parse_anime_list(soup))
            
            return all_results
    
    async def scrape_multiple_genres(
        self,
        genres: List[str],
        page: int = 1
    ) -> Dict[str, List[SearchResult]]:
        """Scrape first page of multiple genres concurrently"""
        async with aiohttp.ClientSession() as session:
            tasks = {}
            for genre in genres:
                url = f"{self.base_url}/genre/{genre}"
                tasks[genre] = self._get_soup(session, url, {"page": page})
            
            results = {}
            soups = await asyncio.gather(*tasks.values())
            
            for genre, soup in zip(tasks.keys(), soups):
                results[genre] = self._parse_anime_list(soup)
            
            return results
    
    async def get_anime_details_batch(
        self,
        anime_slugs: List[str]
    ) -> List[Optional[AnimeInfo]]:
        """Get details for multiple anime concurrently"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for slug in anime_slugs:
                url = f"{self.base_url}/{slug}"
                tasks.append(self._fetch_anime_details(session, url))
            
            return await asyncio.gather(*tasks)
    
    async def _fetch_anime_details(
        self,
        session: aiohttp.ClientSession,
        url: str
    ) -> Optional[AnimeInfo]:
        """Fetch and parse single anime details"""
        soup = await self._get_soup(session, url)
        
        if not soup.select_one('.film-name'):
            return None
        
        try:
            title_elem = soup.select_one('.film-name')
            title = ParserUtils.clean_text(title_elem.text) if title_elem else ""
            
            synopsis_elem = soup.select_one('.film-description .text')
            synopsis = ParserUtils.clean_text(synopsis_elem.text) if synopsis_elem else ""
            
            extracted_id = ParserUtils.extract_anime_id(url)
            slug = ParserUtils.extract_slug(url)
            
            # Parse additional info
            info_items = soup.select('.anisc-info .item')
            genres = []
            studios = []
            
            for item in info_items:
                label = item.select_one('.item-head')
                if label and "genres" in label.text.lower():
                    genre_links = item.select('a')
                    genres = [ParserUtils.clean_text(g.text) for g in genre_links]
                elif label and "studios" in label.text.lower():
                    studio_links = item.select('a')
                    studios = [ParserUtils.clean_text(s.text) for s in studio_links]
            
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
                episodes_sub=ParserUtils.parse_episode_count(sub_elem.text if sub_elem else ""),
                episodes_dub=ParserUtils.parse_episode_count(dub_elem.text if dub_elem else "")
            )
            
        except Exception as e:
            logger.error(f"Failed to parse details for {url}: {e}")
            return None


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

async def main():
    """Example async usage"""
    
    # Initialize async scraper
    scraper = AsyncHiAnimeScraper(
        max_concurrent=3,  # Max 3 concurrent requests
        delay=1.5          # 1.5 second delay between requests
    )
    
    print("=== Async Search ===")
    results = await scraper.search("naruto")
    for r in results[:5]:
        print(f"- {r.title}")
    
    print("\n=== Search Multiple Pages Concurrently ===")
    all_results = await scraper.search_multiple_pages("demon", pages=[1, 2, 3])
    print(f"Total results from 3 pages: {len(all_results)}")
    
    print("\n=== Scrape Multiple Genres ===")
    genre_results = await scraper.scrape_multiple_genres(
        ["action", "romance", "comedy"],
        page=1
    )
    for genre, anime_list in genre_results.items():
        print(f"{genre}: {len(anime_list)} anime")
    
    print("\n=== Batch Details Fetch ===")
    slugs = ["naruto-677", "one-piece-100", "bleach-806"]
    details = await scraper.get_anime_details_batch(slugs)
    for d in details:
        if d:
            print(f"- {d.title}: {d.episodes_sub} episodes")


if __name__ == "__main__":
    asyncio.run(main())
