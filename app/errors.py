from urllib.parse import urlencode, urlsplit

from fastapi import Request, Response
from fastapi.responses import JSONResponse, RedirectResponse


class NotAuthenticated(Exception):
    pass

class CSRFError(Exception):
    pass

def not_authenticated_user(request: Request, exc: NotAuthenticated) -> Response:
    """
    Handle Response for anonymous requests
        Request | Response
        Normal HTML | 303 to /login?next=...
        HTMX (HX-Request: true) | 401 with HX-Redirect: /login?next=...
        /api/* | 401 JSON {"detail": "Not authenticated"}
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
    return Response(status_code=403, content="La requête n'a pas pu être vérifiée. Rechargez la page et réessayez.")