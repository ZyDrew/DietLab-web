import logging
from urllib.parse import urlencode, urlsplit

from fastapi import Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.templating import templates


logger = logging.getLogger("dietlab.errors")

DEFAULT_403 = "Vous n'avez pas accès à cette ressource."
DEFAULT_404 = "La page demandée est introuvable."
DEFAULT_CSRF = "La requête n'a pas pu être vérifiée. Rechargez la page et réessayez."
MAX_MESSAGE_LENGTH = 200

FALLBACK_500 = (
    "<!doctype html><html lang=\"fr\"><head><meta charset=\"utf-8\">"
    "<title>DietLab - Erreur interne</title></head><body>"
    "<h1>Erreur interne</h1><p>Une erreur est survenue. "
    "<a href=\"/\">Retour à l'accueil</a></p></body></html>"
)


class NotAuthenticated(Exception):
    pass


class CSRFError(Exception):
    pass


def _message(detail, default: str) -> str:
    if isinstance(detail, str):
        detail = detail.strip()
        if detail and detail not in ("Not Found", "Forbidden"):
            return detail[:MAX_MESSAGE_LENGTH]
    return default


def _error_url(status: int, message: str | None = None) -> str:
    url = f"/error/{status}"
    if message:
        url += "?" + urlencode({"message": message})
    return url


def _render_error(request: Request, status: int, message: str | None = None) -> Response:
    context = {"message": message} if message else {}
    return templates.TemplateResponse(
        request=request,
        name=f"errors/{status}.html",
        context=context,
        status_code=status,
    )


def _htmx_error_redirect(status: int, message: str | None = None) -> Response:
    return Response(
        status_code=status,
        headers={"HX-Redirect": _error_url(status, message)},
    )


def not_authenticated_user(request: Request, exc: NotAuthenticated) -> Response:
    """
    Handle anonymous requests:
        normal HTML: 303 to /login?next=...
        HTMX: 401 with HX-Redirect to /login?next=...
        /api: 401 JSON
    """
    if request.url.path.startswith("/api"):
        response = JSONResponse({"detail": "Not authenticated"}, status_code=401)
        response.delete_cookie("dietlab_session", path="/")
        return response

    current = request.headers.get("HX-Current-URL")
    if current:
        parts = urlsplit(current)
        next_url = parts.path
        if parts.query:
            next_url += "?" + parts.query
    else:
        next_url = request.url.path
        if request.url.query:
            next_url += "?" + request.url.query

    login_url = "/login?" + urlencode({"next": next_url or "/"})

    if request.headers.get("HX-Request") == "true":
        response = Response(status_code=401, headers={"HX-Redirect": login_url})
    else:
        response = RedirectResponse(url=login_url, status_code=303)

    response.delete_cookie("dietlab_session", path="/")
    return response


def invalid_csrf_token(request: Request, exc: CSRFError) -> Response:
    logger.warning("CSRF validation failed on %s %s", request.method, request.url.path)
    if request.headers.get("HX-Request") == "true":
        return _htmx_error_redirect(403, DEFAULT_CSRF)
    return _render_error(request, 403, DEFAULT_CSRF)


def http_exception(request: Request, exc: StarletteHTTPException) -> Response:
    status = exc.status_code

    if status in (403, 404):
        default = DEFAULT_403 if status == 403 else DEFAULT_404
        message = _message(exc.detail, default)

        if status == 403:
            logger.warning("HTTP 403 on %s %s", request.method, request.url.path)
        else:
            logger.info("HTTP 404 on %s %s", request.method, request.url.path)

        if request.url.path.startswith("/api"):
            return JSONResponse({"detail": exc.detail}, status_code=status, headers=exc.headers)

        if request.headers.get("HX-Request") == "true":
            return _htmx_error_redirect(status, message)

        return _render_error(request, status, message)

    return JSONResponse({"detail": exc.detail}, status_code=status, headers=exc.headers)


def internal_error(request: Request, exc: Exception) -> Response:
    logger.error(
        "Unhandled error on %s %s (%s)",
        request.method,
        request.url.path,
        type(exc).__name__,
    )

    if request.url.path.startswith("/api"):
        return JSONResponse({"detail": "Internal server error"}, status_code=500)

    if request.url.path.startswith("/error/500"):
        return HTMLResponse(FALLBACK_500, status_code=500)

    if request.headers.get("HX-Request") == "true":
        return _htmx_error_redirect(500)

    return _render_error(request, 500)
