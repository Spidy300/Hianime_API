# HiAnime.to - Comprehensive Endpoint & API Documentation

## 📋 Overview

**Website:** https://hianime.to  
**Domain CDN:** cdn.noitatnemucod.net  
**Analysis Date:** December 18, 2025  
**robots.txt Status:** Permissive (Allow: /)  

---

## 🔐 Legal & Compliance Notes

- **robots.txt**: `Allow: /` - No restrictions on crawling
- **Sitemap**: Available at `https://hianime.to/sitemap.xml`
- **Terms of Service**: Available at `https://hianime.to/terms`
- **DMCA Policy**: Available at `https://hianime.to/dmca`
- **Content Notice**: "HiAnime does not store any files on our server, we only linked to the media which is hosted on 3rd party services"

---

## 🌐 Base URL Structure

```
Base URL: https://hianime.to
CDN (Images/Thumbnails): https://cdn.noitatnemucod.net
```

---

## 📚 Discovered Endpoints

### 1. Homepage & Main Navigation

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main landing page |
| `/home` | GET | Home page (alternate) |

---

### 2. Search Endpoints

#### Basic Search
```
GET /search?keyword={query}
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `keyword` | string | Yes | URL-encoded search term |

**Example:**
```
https://hianime.to/search?keyword=naruto
https://hianime.to/search?keyword=Chainsaw%20Man%20the%20Movie%3A%20Reze%20Arc
```

#### Advanced Filter Search
```
GET /filter
GET /filter?type={type}&status={status}&rated={rated}&score={score}&season={season}&language={language}&start_date={date}&end_date={date}&sort={sort}&genres={genres}&page={page}
```

**Filter Parameters:**
| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `type` | string | movie, tv, ova, ona, special, music | Anime type filter |
| `status` | string | finished, airing, upcoming | Airing status |
| `rated` | string | g, pg, pg-13, r, r+, rx | Age rating |
| `score` | int | 1-10 | Minimum MAL score |
| `season` | string | spring, summer, fall, winter | Season filter |
| `language` | string | sub, dub | Audio language |
| `start_date` | date | YYYY-MM-DD | Aired after date |
| `end_date` | date | YYYY-MM-DD | Aired before date |
| `sort` | string | default, recently_added, recently_updated, score, name_az, released_date, most_watched | Sort order |
| `genres` | string | action,adventure,... | Comma-separated genres |
| `page` | int | 1-n | Pagination |

**Available Genres:**
```
action, adventure, cars, comedy, dementia, demons, drama, ecchi, fantasy, 
game, harem, historical, horror, isekai, josei, kids, magic, marial-arts, 
mecha, military, music, mystery, parody, police, psychological, romance, 
samurai, school, sci-fi, seinen, shoujo, shoujo-ai, shounen, shounen-ai, 
slice-of-life, space, sports, super-power, supernatural, thriller, vampire
```

---

### 3. Browse Endpoints

#### By Category
| Endpoint | Description | Pagination |
|----------|-------------|------------|
| `/most-popular` | Most popular anime | `?page=1` (50 pages) |
| `/top-airing` | Currently airing popular | `?page=1` (11 pages) |
| `/recently-updated` | Recently updated episodes | `?page=1` (213 pages) |
| `/completed` | Completed anime | `?page=1` (208 pages) |
| `/subbed-anime` | Anime with subtitles | `?page=1` |
| `/dubbed-anime` | Dubbed anime | `?page=1` |

#### By Type
| Endpoint | Description |
|----------|-------------|
| `/movie` | Movies only |
| `/tv` | TV series |
| `/ova` | Original Video Animation |
| `/ona` | Original Net Animation |
| `/special` | Special episodes |

#### By Genre
```
GET /genre/{genre-slug}
```

**Format:** `/genre/{genre}?page={page}`

**Examples:**
```
https://hianime.to/genre/action
https://hianime.to/genre/action?page=2
https://hianime.to/genre/adventure
https://hianime.to/genre/romance
```

**Total Genre Pages Example:** Action has ~98 pages

#### A-Z List (Alphabetical Browse)
```
GET /az-list
GET /az-list/{letter}
GET /az-list/other  (# symbols)
GET /az-list/0-9
GET /az-list/A through Z
```

---

### 4. Anime Detail Pages

#### Anime Info Page
```
GET /{anime-slug}-{anime-id}
```

**URL Pattern:** `/{title-slug}-{numeric-id}`

**Examples:**
```
https://hianime.to/naruto-677
https://hianime.to/one-piece-100
https://hianime.to/demon-slayer-kimetsu-no-yaiba-47
https://hianime.to/solo-leveling-season-2-arise-from-the-shadow-19413
```

**Response Data Points:**
- Title (English/Japanese/Synonyms)
- Synopsis/Description
- Episode count (sub/dub)
- Type (TV/Movie/OVA/etc.)
- Duration
- Status
- Aired dates
- Premiered season
- MAL Score
- Genres (linked)
- Studios
- Producers
- Characters & Voice Actors
- Related Anime
- Recommendations
- Promotional Videos

---

### 5. Watch/Streaming Endpoints

#### Watch Page
```
GET /watch/{anime-slug}-{anime-id}
```

**Example:**
```
https://hianime.to/watch/naruto-677
```

**Features Available:**
- Episode list (Sub/Dub counts shown)
- Server selection
- Auto-play toggle
- Auto-next toggle
- Auto-skip intro toggle
- Light on/off mode
- Watch2gether integration

#### Episode-Specific (Inferred Pattern)
```
GET /watch/{anime-slug}-{anime-id}?ep={episode-number}
```

---

### 6. Community Endpoints

```
GET /community/board           - Community main board
GET /community/post/{slug}-{id} - Individual posts
GET /community/user/{user-id}   - User profiles
```

**Example:**
```
https://hianime.to/community/post/searching-for-my-friends-302069
https://hianime.to/community/user/10234613
```

---

### 7. Producer/Studio Pages

```
GET /producer/{producer-slug}
```

**Example:**
```
https://hianime.to/producer/studio-pierrot
https://hianime.to/producer/tv-tokyo
https://hianime.to/producer/aniplex
```

---

### 8. Character & People Pages

```
GET /character/{character-slug}-{id}
GET /people/{person-slug}-{id}
```

**Examples:**
```
https://hianime.to/character/naruto-uzumaki-9
https://hianime.to/character/sakura-haruno-291
https://hianime.to/people/junko-takeuchi-103
```

---

### 9. Special Features

```
GET /watch2gether                    - Watch together feature
GET /watch2gether/create/{anime-id}  - Create watch party
GET /random                          - Random anime redirect
GET /events                          - Events page
GET /news                            - News articles
GET /app-download                    - Mobile app download
```

---

### 10. Static/Info Pages

```
GET /terms     - Terms of Service
GET /dmca      - DMCA policy
GET /contact   - Contact page
```

---

## 📦 Sitemap Structure

**Main Sitemap Index:** `https://hianime.to/sitemap.xml`

| Sitemap File | Content |
|--------------|---------|
| `/sitemap-page.xml` | Static pages |
| `/sitemap-genre.xml` | Genre pages |
| `/sitemap-type.xml` | Type pages (movie, tv, ova, ona, special) |
| `/sitemap-movie-1.xml` through `/sitemap-movie-5.xml` | Movie listings |

---

## 🖼️ CDN/Asset URLs

### Image Patterns

**Thumbnails:**
```
https://cdn.noitatnemucod.net/thumbnail/300x400/100/{image-hash}.jpg
```

**Avatars:**
```
https://cdn.noitatnemucod.net/avatar/100x100/{series}/{filename}
```

**Examples:**
```
https://cdn.noitatnemucod.net/thumbnail/300x400/100/bcd84731a3eda4f4a306250769675065.jpg
https://cdn.noitatnemucod.net/avatar/100x100/attack_on_titan/aot_10.png
```

---

## 📊 Pagination Patterns

All list endpoints support pagination via query parameter:

```
?page={number}
```

**Observed Limits:**
| Endpoint | Max Pages |
|----------|-----------|
| `/most-popular` | ~50 |
| `/top-airing` | ~11 |
| `/recently-updated` | ~213 |
| `/completed` | ~208 |
| `/genre/action` | ~98 |
| `/filter` | ~236 |

---

## 🔄 Identified AJAX/API Patterns

Based on analysis, the site likely uses internal AJAX endpoints for:

1. **Episode List Loading** - Dynamic episode lists
2. **Server Selection** - Video source switching  
3. **Search Autocomplete** - Live search suggestions
4. **Top 10 Tabs** - Today/Week/Month switching
5. **Comments Loading** - Lazy-loaded comments

**Likely AJAX Endpoint Patterns (to be verified via network analysis):**
```
/ajax/episode/list?id={anime-id}
/ajax/episode/servers?episodeId={ep-id}
/ajax/search/suggest?keyword={query}
/ajax/home/widget/top10?type={day|week|month}
```

---

## 📝 Data Schema Examples

### Anime Card Data Structure
```json
{
  "id": "19932",
  "slug": "one-punch-man-season-3",
  "title": "One-Punch Man Season 3",
  "url": "/one-punch-man-season-3-19932",
  "thumbnail": "https://cdn.noitatnemucod.net/thumbnail/300x400/100/269a2fc7ec4b9c0592493ef192ad2a9d.jpg",
  "type": "TV",
  "duration": "24m",
  "rating": "18+",
  "episodes": {
    "sub": 10,
    "dub": 3
  }
}
```

### Search Result Pattern
```json
{
  "title": "Naruto",
  "url": "/naruto-677?ref=search",
  "type": "TV",
  "duration": "23m",
  "episodes": {
    "sub": 220,
    "dub": 220
  }
}
```

---

## ⚠️ Anti-Scraping Considerations

### Observed Protections:
1. **Cloudflare Protection** - Standard Cloudflare CDN
2. **JavaScript Rendering** - Some content requires JS execution
3. **Dynamic Content Loading** - AJAX-based episode/server data

### Recommended Bypass Strategies:
1. Use headless browser (Playwright/Puppeteer) for JS-rendered content
2. Implement request delays (2-5 seconds between requests)
3. Rotate User-Agents
4. Use residential proxies for high-volume scraping
5. Respect rate limits to avoid IP bans

---

## 🛠️ Implementation Notes

### Rate Limiting Recommendations:
- **Conservative:** 1 request per 3 seconds
- **Moderate:** 1 request per 1.5 seconds  
- **Aggressive:** 1 request per 0.5 seconds (risk of blocking)

### Required Headers:
```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
```

### Session Handling:
- Cookies may be required for authenticated features
- Some features require JavaScript execution
- Video streams are hosted on 3rd party servers

---

## 📁 Output Format Recommendations

For scraping results, recommend storing in:

1. **JSON** - For API responses and structured data
2. **CSV** - For anime lists and search results
3. **SQLite/PostgreSQL** - For persistent storage with relationships

---

## 🔗 External Integrations

The site integrates with:
- **MyAnimeList (MAL)** - Score data
- **YouTube** - Promotional videos
- **Discord** - Community server
- **Twitter** - Social sharing
- **Reddit** - Community subreddit (/r/HiAnimeZone)

---

*Documentation compiled through systematic endpoint discovery and web page analysis.*
