# HiAnime.to Web Scraper

A production-ready Python web scraper for extracting anime data from HiAnime.to. Includes **sync**, **async**, and **Playwright** implementations.

## ⚠️ Disclaimer

This scraper is provided for **educational purposes only**. Please:
- Respect the website's Terms of Service
- Implement appropriate rate limiting
- Do not overload the servers
- Do not use for commercial purposes without permission
- Be aware of legal implications in your jurisdiction

## 📁 Project Structure

```
sraping_mcp/
├── hianime_endpoints_documentation.md  # Complete endpoint reference
├── hianime_scraper.py                  # Sync scraper (requests + BeautifulSoup)
├── hianime_scraper_async.py            # Async scraper (aiohttp + asyncio)
├── hianime_scraper_playwright.py       # Browser automation (Playwright)
├── requirements.txt                    # Python dependencies
└── README.md                           # This file
```

## 🚀 Features

### Core Features
- **Search Functionality**: Keyword search with pagination
- **Advanced Filtering**: Filter by type, status, rating, genre, score, season
- **Category Browsing**: Most popular, top airing, recently updated, completed
- **Genre/Type Lists**: Browse by specific genres or anime types
- **Detailed Info Extraction**: Full anime details including synopsis, cast, related anime
- **Rate Limiting**: Built-in delays to respect server load
- **Proxy Support**: Rotate through proxies for anonymity
- **Export Options**: JSON and CSV export

### Implementation Options
| Implementation | File | Best For |
|----------------|------|----------|
| **Sync** | `hianime_scraper.py` | Simple scripts, sequential tasks |
| **Async** | `hianime_scraper_async.py` | High-volume, concurrent scraping |
| **Playwright** | `hianime_scraper_playwright.py` | JS-rendered content, stealth mode |

## 📦 Installation

```bash
# Clone or download the repository
cd sraping_mcp

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🔧 Quick Start

```python
from hianime_scraper import HiAnimeScraper

# Initialize the scraper
scraper = HiAnimeScraper(rate_limit=True)

# Search for anime
results = scraper.search("naruto")
for anime in results:
    print(f"{anime.title} - {anime.episodes_sub} episodes")

# Get anime details
details = scraper.get_anime_details("naruto-677")
print(f"Synopsis: {details.synopsis}")
```

## 📖 API Reference

### Initialize Scraper

```python
scraper = HiAnimeScraper(
    proxies=["http://proxy1:8080", "http://proxy2:8080"],  # Optional
    rate_limit=True  # Enable rate limiting (recommended)
)
```

### Search Methods

#### Basic Search
```python
results = scraper.search("one piece", page=1)
```

#### Advanced Filter
```python
results = scraper.advanced_filter(
    type="tv",           # movie, tv, ova, ona, special, music
    status="finished",   # finished, airing, upcoming
    rated="pg-13",       # g, pg, pg-13, r, r+, rx
    score=8,             # Minimum MAL score (1-10)
    season="fall",       # spring, summer, fall, winter
    language="sub",      # sub, dub
    genres=["action", "adventure"],
    sort="score",        # default, recently_added, score, name_az, etc.
    page=1
)
```

### Browse Methods

```python
# Get most popular anime
popular = scraper.get_most_popular(page=1)

# Get currently airing
airing = scraper.get_top_airing(page=1)

# Get recently updated
updated = scraper.get_recently_updated(page=1)

# Get completed anime
completed = scraper.get_completed(page=1)

# Get anime by genre
action = scraper.get_by_genre("action", page=1)

# Get anime by type
movies = scraper.get_by_type("movie", page=1)

# Alphabetical listing
anime_a = scraper.get_az_list("A", page=1)
```

### Detail Methods

```python
# Get full anime details
details = scraper.get_anime_details("naruto-677")

# Access detail attributes
print(details.title)
print(details.japanese_title)
print(details.synopsis)
print(details.episodes_sub)
print(details.mal_score)
print(details.genres)
print(details.studios)
```

### Bulk Operations

```python
# Scrape all pages (generator)
for anime in scraper.scrape_all_pages(
    scraper.get_most_popular,
    max_pages=5
):
    print(anime.title)

# Export to JSON
scraper.export_to_json(results, "output.json")

# Export to CSV
scraper.export_to_csv(results, "output.csv")
```

## 📊 Data Models

### SearchResult
```python
@dataclass
class SearchResult:
    title: str
    url: str
    id: str
    thumbnail: Optional[str]
    type: Optional[str]        # TV, Movie, OVA, etc.
    duration: Optional[str]    # e.g., "24m"
    episodes_sub: Optional[int]
    episodes_dub: Optional[int]
```

### AnimeInfo
```python
@dataclass
class AnimeInfo:
    id: str
    slug: str
    title: str
    url: str
    thumbnail: Optional[str]
    type: Optional[str]
    duration: Optional[str]
    rating: Optional[str]      # PG-13, 18+, etc.
    status: Optional[str]      # Airing, Finished
    episodes_sub: Optional[int]
    episodes_dub: Optional[int]
    mal_score: Optional[float]
    synopsis: Optional[str]
    japanese_title: Optional[str]
    synonyms: Optional[str]
    aired: Optional[str]
    premiered: Optional[str]
    genres: List[str]
    studios: List[str]
    producers: List[str]
```

## 🔗 Discovered Endpoints

See `hianime_endpoints_documentation.md` for complete endpoint documentation.

### Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `/search?keyword=X` | Search anime |
| `/filter?type=X&genre=X` | Advanced filter |
| `/most-popular` | Most popular anime |
| `/top-airing` | Currently airing |
| `/genre/{genre}` | Browse by genre |
| `/{anime-slug}-{id}` | Anime detail page |
| `/watch/{anime-slug}-{id}` | Watch page |

---

## 🌐 Async Scraper (High Performance)

Use `hianime_scraper_async.py` for concurrent scraping:

```python
import asyncio
from hianime_scraper_async import AsyncHiAnimeScraper

async def main():
    scraper = AsyncHiAnimeScraper(
        max_concurrent=3,  # Limit concurrent requests
        delay=1.5          # Delay between batches
    )
    
    # Search multiple pages concurrently
    results = await scraper.search_multiple_pages("demon", pages=[1, 2, 3])
    print(f"Found {len(results)} results")
    
    # Scrape multiple genres at once
    genres = await scraper.scrape_multiple_genres(["action", "romance"])
    
    # Batch fetch anime details
    details = await scraper.get_anime_details_batch([
        "naruto-677", "one-piece-100", "bleach-806"
    ])

asyncio.run(main())
```

---

## 🎭 Playwright Scraper (Browser Automation)

Use `hianime_scraper_playwright.py` for JavaScript-rendered content:

```bash
# First, install Playwright browsers
pip install playwright
playwright install chromium
```

```python
import asyncio
from hianime_scraper_playwright import PlaywrightHiAnimeScraper

async def main():
    async with PlaywrightHiAnimeScraper(
        headless=True,
        slow_mo=100,
        save_state=True  # Persist cookies/session
    ) as scraper:
        # Search with full browser
        results = await scraper.search("naruto")
        
        # Get episode list (requires JS)
        episodes = await scraper.get_episode_list("naruto-677")
        
        # Take debug screenshot
        await scraper.screenshot("debug.png")

asyncio.run(main())
```

---

## ⚙️ Configuration

Edit `ScraperConfig` class in `hianime_scraper.py`:

```python
class ScraperConfig:
    MIN_DELAY = 1.0      # Min seconds between requests
    MAX_DELAY = 3.0      # Max seconds between requests
    MAX_RETRIES = 3      # Retry attempts
    REQUEST_TIMEOUT = 30 # Timeout in seconds
```

## 🛡️ Rate Limiting Recommendations

| Use Case | Delay | Risk |
|----------|-------|------|
| Research | 3-5 sec | Low |
| Moderate | 1-2 sec | Medium |
| Aggressive | <1 sec | High (may get blocked) |

## 🔄 Proxy Configuration

```python
proxies = [
    "http://user:pass@proxy1.example.com:8080",
    "http://user:pass@proxy2.example.com:8080",
    "socks5://user:pass@proxy3.example.com:1080"
]

scraper = HiAnimeScraper(proxies=proxies)
```

## 🐛 Troubleshooting

### Connection Errors
- Check your internet connection
- Try increasing timeout in config
- Use proxy rotation

### Getting Blocked
- Increase delay between requests
- Rotate user agents (built-in)
- Use residential proxies
- Reduce concurrent requests

### Missing Data
- Some fields require JavaScript rendering
- Consider using Playwright for full content
- Check if element selectors have changed

## 📝 License

This project is for educational purposes. Use responsibly.

## 🤝 Contributing

Feel free to submit issues or pull requests for improvements.
