from fastapi.requests import Request
from fastapi.responses import JSONResponse

class MovieNotFoundError(Exception):
    def __init__(self, movie_id: int):
        self.movie_id = movie_id

async def movie_not_found_handler(request: Request, exc: MovieNotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "content": f"MOVIE WITH ID:{exc.movie_id} NOT FOUND!"
        }
    )

class MovieAlreadyExists(Exception):
    def __init__(self, movie_id: int):
        self.movie_id = movie_id

async def movie_already_exists_handler(request: Request, exc: MovieAlreadyExists):
    return JSONResponse(
        status_code=409,
        content={
            "content": f"MOVIE WITH ID:{exc.movie_id} ALREADY EXISTS!"
        }
    )
