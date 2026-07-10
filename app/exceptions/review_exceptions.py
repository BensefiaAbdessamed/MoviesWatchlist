from fastapi.requests import Request
from fastapi.responses import JSONResponse

class ReviewNotFoundError(Exception):
    def __init__(self, 
        movie_id: int
    ):
        self.movie_id = movie_id
        

async def review_not_found_handler(request: Request, exc: ReviewNotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "content": f"REVIEW FOR MOVIE ID:{exc.movie_id} NOT FOUND!"
        }
    )


class ReviewAlreadyExists(Exception):
    def __init__(self, 
        movie_id: int
    ):
        self.movie_id = movie_id
        
async def review_already_exists_handler(request: Request, exc: ReviewAlreadyExists):
    return JSONResponse(
        status_code=409,
        content={
            "content": f"REVIEW FOR MOVIE ID:{exc.movie_id} ALREADY EXISTS!"
        }
    )