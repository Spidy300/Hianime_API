"""
HiAnime.to Scraper API
======================
FastAPI REST API for accessing HiAnime scraper functionality

Run with: uvicorn api:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List
from pydantic import BaseModel
from dataclasses import asdict

from hianime_scraper import HiAnimeScraper, SearchResult, AnimeInfo, Episode

# Initialize FastAPI app
app = FastAPI(
    title="HiAnime Scraper API",
    description="REST API for scraping anime data from HiAnime.to",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize scraper (singleton)
scraper = HiAnimeScraper(rate_limit=True)


# =============================================================================
# RESPONSE MODELS
# =============================================================================

class AnimeSearchResponse(BaseModel):
    success: bool
    count: int
    page: int
    data: List[dict]


class EpisodeListResponse(BaseModel):
    success: bool
    count: int
    data: List[dict]


class AnimeDetailResponse(BaseModel):
    success: bool
    data: Optional[dict]


class ErrorResponse(BaseModel):
    success: bool = False
    error: str


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def serialize_results(results: List[SearchResult]) -> List[dict]:
    """Convert SearchResult objects to dictionaries"""
    return [asdict(r) for r in results]


def serialize_details(details: AnimeInfo) -> dict:
    """Convert AnimeInfo object to dictionary"""
    return asdict(details) if details else None


# =============================================================================
# API ROUTES
# =============================================================================

@app.get("/", tags=["Root"])
async def root():
    """API Health Check"""
    return {
        "status": "online",
        "api": "HiAnime Scraper API",
        "version": "1.0.0",
        "total_endpoints": 16,
        "endpoints": {
            "search": "/api/search?keyword=naruto",
            "filter": "/api/filter?type=tv&status=airing",
            "popular": "/api/popular",
            "top_airing": "/api/top-airing",
            "recently_updated": "/api/recently-updated",
            "completed": "/api/completed",
            "subbed": "/api/subbed",
            "dubbed": "/api/dubbed",
            "genre": "/api/genre/{genre}",
            "type": "/api/type/{type}",
            "az_list": "/api/az/{letter}",
            "producer": "/api/producer/{producer_slug}",
            "anime_details": "/api/anime/{slug}",
            "episodes": "/api/episodes/{slug}",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


# -----------------------------------------------------------------------------
# SEARCH
# -----------------------------------------------------------------------------

@app.get("/api/search", response_model=AnimeSearchResponse, tags=["Search"])
async def search_anime(
    keyword: str = Query(..., description="Search keyword", min_length=1),
    page: int = Query(1, ge=1, description="Page number")
):
    """
    Search for anime by keyword
    
    - **keyword**: Search term (required)
    - **page**: Page number (default: 1)
    """
    try:
        results = scraper.search(keyword, page=page)
        return {
            "success": True,
            "count": len(results),
            "page": page,
            "data": serialize_results(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------------------------------------------------
# BROWSE ENDPOINTS
# -----------------------------------------------------------------------------

@app.get("/api/popular", response_model=AnimeSearchResponse, tags=["Browse"])
async def get_popular(
    page: int = Query(1, ge=1, description="Page number")
):
    """Get most popular anime"""
    try:
        results = scraper.get_most_popular(page=page)
        return {
            "success": True,
            "count": len(results),
            "page": page,
            "data": serialize_results(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/top-airing", response_model=AnimeSearchResponse, tags=["Browse"])
async def get_top_airing(
    page: int = Query(1, ge=1, description="Page number")
):
    """Get currently airing anime"""
    try:
        results = scraper.get_top_airing(page=page)
        return {
            "success": True,
            "count": len(results),
            "page": page,
            "data": serialize_results(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/recently-updated", response_model=AnimeSearchResponse, tags=["Browse"])
async def get_recently_updated(
    page: int = Query(1, ge=1, description="Page number")
):
    """Get recently updated anime"""
    try:
        results = scraper.get_recently_updated(page=page)
        return {
            "success": True,
            "count": len(results),
            "page": page,
            "data": serialize_results(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/completed", response_model=AnimeSearchResponse, tags=["Browse"])
async def get_completed(
    page: int = Query(1, ge=1, description="Page number")
):
    """Get completed anime"""
    try:
        results = scraper.get_completed(page=page)
        return {
            "success": True,
            "count": len(results),
            "page": page,
            "data": serialize_results(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------------------------------------------------
# GENRE & TYPE
# -----------------------------------------------------------------------------

@app.get("/api/genre/{genre}", response_model=AnimeSearchResponse, tags=["Genre & Type"])
async def get_by_genre(
    genre: str,
    page: int = Query(1, ge=1, description="Page number")
):
    """
    Get anime by genre
    
    Available genres: action, adventure, cars, comedy, dementia, demons, drama,
    ecchi, fantasy, game, harem, historical, horror, isekai, josei, kids, magic,
    martial-arts, mecha, military, music, mystery, parody, police, psychological,
    romance, samurai, school, sci-fi, seinen, shoujo, shoujo-ai, shounen,
    shounen-ai, slice-of-life, space, sports, super-power, supernatural,
    thriller, vampire
    """
    try:
        results = scraper.get_by_genre(genre, page=page)
        return {
            "success": True,
            "count": len(results),
            "page": page,
            "data": serialize_results(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/type/{type_name}", response_model=AnimeSearchResponse, tags=["Genre & Type"])
async def get_by_type(
    type_name: str,
    page: int = Query(1, ge=1, description="Page number")
):
    """
    Get anime by type
    
    Available types: movie, tv, ova, ona, special, music
    """
    try:
        results = scraper.get_by_type(type_name, page=page)
        return {
            "success": True,
            "count": len(results),
            "page": page,
            "data": serialize_results(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------------------------------------------------
# ADVANCED FILTER
# -----------------------------------------------------------------------------

@app.get("/api/filter", response_model=AnimeSearchResponse, tags=["Filter"])
async def advanced_filter(
    type: Optional[str] = Query(None, description="Type: movie, tv, ova, ona, special, music"),
    status: Optional[str] = Query(None, description="Status: finished, airing, upcoming"),
    rated: Optional[str] = Query(None, description="Rating: g, pg, pg-13, r, r+, rx"),
    score: Optional[int] = Query(None, ge=1, le=10, description="Minimum score (1-10)"),
    season: Optional[str] = Query(None, description="Season: spring, summer, fall, winter"),
    language: Optional[str] = Query(None, description="Language: sub, dub"),
    genres: Optional[str] = Query(None, description="Comma-separated genres"),
    sort: Optional[str] = Query("default", description="Sort: default, recently_added, recently_updated, score, name_az, released_date, most_watched"),
    page: int = Query(1, ge=1, description="Page number")
):
    """
    Advanced filter for anime
    
    Filter by multiple criteria simultaneously
    """
    try:
        genre_list = genres.split(",") if genres else None
        
        results = scraper.advanced_filter(
            type=type,
            status=status,
            rated=rated,
            score=score,
            season=season,
            language=language,
            genres=genre_list,
            sort=sort,
            page=page
        )
        return {
            "success": True,
            "count": len(results),
            "page": page,
            "data": serialize_results(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------------------------------------------------
# ANIME DETAILS
# -----------------------------------------------------------------------------

@app.get("/api/anime/{slug}", response_model=AnimeDetailResponse, tags=["Details"])
async def get_anime_details(slug: str):
    """
    Get detailed information about an anime
    
    - **slug**: Anime slug (e.g., "naruto-677", "one-piece-100")
    """
    try:
        details = scraper.get_anime_details(slug)
        if not details:
            raise HTTPException(status_code=404, detail="Anime not found")
        
        return {
            "success": True,
            "data": serialize_details(details)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------------------------------------------------
# A-Z LIST
# -----------------------------------------------------------------------------

@app.get("/api/az/{letter}", response_model=AnimeSearchResponse, tags=["A-Z List"])
async def get_az_list(
    letter: str,
    page: int = Query(1, ge=1, description="Page number")
):
    """
    Get anime alphabetically by first letter
    
    - **letter**: Single letter A-Z or "other" for non-alphabetic
    """
    try:
        results = scraper.get_az_list(letter.upper(), page=page)
        return {
            "success": True,
            "count": len(results),
            "page": page,
            "data": serialize_results(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------------------------------------------------
# SUBBED / DUBBED
# -----------------------------------------------------------------------------

@app.get("/api/subbed", response_model=AnimeSearchResponse, tags=["Browse"])
async def get_subbed_anime(
    page: int = Query(1, ge=1, description="Page number")
):
    """Get anime with subtitles"""
    try:
        results = scraper.get_subbed_anime(page=page)
        return {
            "success": True,
            "count": len(results),
            "page": page,
            "data": serialize_results(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dubbed", response_model=AnimeSearchResponse, tags=["Browse"])
async def get_dubbed_anime(
    page: int = Query(1, ge=1, description="Page number")
):
    """Get dubbed anime"""
    try:
        results = scraper.get_dubbed_anime(page=page)
        return {
            "success": True,
            "count": len(results),
            "page": page,
            "data": serialize_results(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------------------------------------------------
# PRODUCER / STUDIO
# -----------------------------------------------------------------------------

@app.get("/api/producer/{producer_slug}", response_model=AnimeSearchResponse, tags=["Producer"])
async def get_by_producer(
    producer_slug: str,
    page: int = Query(1, ge=1, description="Page number")
):
    """
    Get anime by producer/studio
    
    - **producer_slug**: Producer slug (e.g., "studio-pierrot", "mappa", "toei-animation")
    """
    try:
        results = scraper.get_by_producer(producer_slug, page=page)
        return {
            "success": True,
            "count": len(results),
            "page": page,
            "data": serialize_results(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------------------------------------------------
# EPISODE LIST
# -----------------------------------------------------------------------------

@app.get("/api/episodes/{slug}", response_model=EpisodeListResponse, tags=["Episodes"])
async def get_episodes(slug: str):
    """
    Get full episode list for an anime (via AJAX API)
    
    - **slug**: Anime slug with ID (e.g., "naruto-677", "one-piece-100")
    
    Returns all episodes with:
    - Episode number, title (English & Japanese)
    - Direct episode URL with episode ID
    - Filler status (when available)
    """
    try:
        episodes = scraper.get_episodes(slug)
        return {
            "success": True,
            "count": len(episodes),
            "data": [asdict(ep) for ep in episodes]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": str(exc)}
    )


# =============================================================================
# RUN SERVER
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
