from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.dependencies.auth import get_current_user
from app.dependencies.csrf import require_csrf
from app.routes.patients import patients_router
from app.routes.recipes import recipes_router
from app.routes.foods import foods_router
from app.routes.comorbidities import comorbidities_router
from app.routes.meal_plan import meal_plan_router
from app.routes.views import views_router
from app.routes.auth import auth_router
from app.routes.errors import errors_router
from app.errors import (
    CSRFError,
    NotAuthenticated,
    http_exception,
    internal_error,
    invalid_csrf_token,
    not_authenticated_user,
)

app = FastAPI()
app.add_exception_handler(NotAuthenticated, not_authenticated_user)
app.add_exception_handler(CSRFError, invalid_csrf_token)
app.add_exception_handler(StarletteHTTPException, http_exception)
app.add_exception_handler(Exception, internal_error)

#Use to include the router for all HTML views
app.include_router(views_router, dependencies=[Depends(require_csrf)])
app.include_router(auth_router)
app.include_router(errors_router)

#Use to include all the routes from the routers declaration - For API and tests only
app.include_router(patients_router, prefix="/api", dependencies=[Depends(get_current_user)])
app.include_router(recipes_router, prefix="/api", dependencies=[Depends(get_current_user)])
app.include_router(foods_router, prefix="/api", dependencies=[Depends(get_current_user)])
app.include_router(comorbidities_router, prefix="/api", dependencies=[Depends(get_current_user)])
app.include_router(meal_plan_router, prefix="/api", dependencies=[Depends(get_current_user)])

#Use to include all static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")
