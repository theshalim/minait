import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers import admin, auth, orders, pages, webhooks
from app.security import refresh_session_middleware
from app.templating import base_ctx, templates

STATIC_DIR = Path(__file__).parent / "static"
logger = logging.getLogger("minait")

app = FastAPI(title=settings.SITE_NAME)

# Keeps logged-in users logged in past the ~1h Supabase access-token lifetime.
app.middleware("http")(refresh_session_middleware)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(orders.router)
app.include_router(admin.router)
app.include_router(webhooks.router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Auth dependencies raise 303 + Location to bounce anonymous users to /login.
    if exc.status_code == 303 and exc.headers and "Location" in exc.headers:
        return RedirectResponse(exc.headers["Location"], status_code=303)
    if exc.status_code == 404:
        return templates.TemplateResponse(
            "404.html", base_ctx(request), status_code=404
        )
    if exc.status_code == 403:
        return templates.TemplateResponse(
            "403.html", base_ctx(request), status_code=403
        )
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code, headers=exc.headers)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Last-resort net: an unexpected bug should show a normal-looking error
    # page (and get logged, visible in Vercel's Runtime Logs) instead of a
    # bare, unstyled "Internal Server Error".
    logger.error("Unhandled exception on %s %s", request.method, request.url.path, exc_info=exc)
    return templates.TemplateResponse("500.html", base_ctx(request), status_code=500)
