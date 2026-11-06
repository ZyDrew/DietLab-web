from fastapi import APIRouter, Request

from app.errors import DEFAULT_403, DEFAULT_404, MAX_MESSAGE_LENGTH
from app.templating import templates


errors_router = APIRouter()


def _message(request: Request, default: str) -> str:
    message = request.query_params.get("message")
    if message:
        return message[:MAX_MESSAGE_LENGTH]
    return default


@errors_router.get("/error/403")
def error_403(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="errors/403.html",
        context={"message": _message(request, DEFAULT_403)},
        status_code=403,
    )


@errors_router.get("/error/404")
def error_404(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="errors/404.html",
        context={"message": _message(request, DEFAULT_404)},
        status_code=404,
    )


@errors_router.get("/error/500")
def error_500(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="errors/500.html",
        status_code=500,
    )
