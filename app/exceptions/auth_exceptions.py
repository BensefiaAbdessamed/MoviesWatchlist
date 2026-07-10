from fastapi.requests import Request
from fastapi.responses import JSONResponse

class NotAuthenticatedError(Exception):
    pass

async def not_authenticated_handler(request: Request, exc: NotAuthenticatedError):
    return JSONResponse(
        status_code=404,
        content={
            "content": "YOU ARE NOT AUTHENTICATED TO DO THIS ACTION"
        }
    )