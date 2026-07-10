from fastapi.requests import Request
from fastapi.responses import JSONResponse

class WatchlistNotFoundError(Exception):
    def __init__(self, 
        user_id: int
    ):
        self.user_id = user_id
        

async def watchlist_not_found_handler(request: Request, exc: WatchlistNotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "content": f"{exc.user_id} WATCHLIST IS EMPTY"
        }
    )


class WatchlistAlreadyExists(Exception):
    def __init__(self, 
        movie_id: int
    ):
        self.movie_id = movie_id
        
async def watchlist_already_exists_handler(request: Request, exc: WatchlistAlreadyExists):
    return JSONResponse(
        status_code=409,
        content={
            "content": f"MOVIE ID: {exc.movie_id}, ALREADY EXISTS IN YOUR WATCHLIST!"
        }
    )