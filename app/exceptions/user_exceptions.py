from fastapi.requests import Request
from fastapi.responses import JSONResponse

class UserNotFoundError(Exception):
    def __init__(self, user_id: int):
        self.user_id = user_id

async def user_not_found_handler(request: Request, exc: UserNotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "content": f"USER ID:`{exc.user_id} NOT FOUND!"
        }
    )

class AlreadyExists(Exception):
    def __init__(self, message: str):
        self.message = message

async def already_exists_handler(request: Request, exc: AlreadyExists):
    return JSONResponse(
        status_code=409,
        content={
            "content":  f"{exc.message} ALREADY EXISTS"
        }
    )





    