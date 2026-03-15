from datetime import datetime

from fastapi import APIRouter, Cookie, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.services.articles import article_service
from app.services.kindle_cleaner import clean_html

router = APIRouter(prefix="/kindle", tags=["kindle"])
templates = Jinja2Templates(directory="app/templates")

_AUTH_COOKIE = "kindle_auth"
_AUTH_VALUE = "ok"


def _datetimeformat(value: datetime) -> str:
    months = ["ene", "feb", "mar", "abr", "may", "jun",
              "jul", "ago", "sep", "oct", "nov", "dic"]
    return f"{value.day} {months[value.month - 1]} {value.year}"


def _urlhost(value: str) -> str:
    try:
        from urllib.parse import urlparse
        return urlparse(value).netloc.replace("www.", "")
    except Exception:
        return value


templates.env.filters["datetimeformat"] = _datetimeformat
templates.env.filters["urlhost"] = _urlhost


def _is_authenticated(request: Request) -> bool:
    return request.cookies.get(_AUTH_COOKIE) == _AUTH_VALUE


def _login_redirect(next_url: str) -> RedirectResponse:
    return RedirectResponse(url=f"/kindle/login?next={next_url}", status_code=302)


# --- Login ---

@router.get("/login", response_class=HTMLResponse)
async def kindle_login_page(request: Request, next: str = "/kindle/"):
    return templates.TemplateResponse(
        "kindle/login.html",
        {"request": request, "next": next, "error": None},
    )


@router.post("/login")
async def kindle_login(
    request: Request,
    pin: str = Form(...),
    next: str = Form("/kindle/"),
):
    if pin == settings.KINDLE_PIN:
        response = RedirectResponse(url=next, status_code=303)
        response.set_cookie(
            _AUTH_COOKIE,
            _AUTH_VALUE,
            max_age=30 * 24 * 3600,  # 30 días
            httponly=True,
            samesite="lax",
        )
        return response
    return templates.TemplateResponse(
        "kindle/login.html",
        {"request": request, "next": next, "error": "Código incorrecto"},
        status_code=401,
    )


# --- Vistas protegidas ---

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def kindle_list(request: Request, db: AsyncSession = Depends(get_db)):
    if not _is_authenticated(request):
        return _login_redirect("/kindle/")
    articles = await article_service.get_all(db, unread_only=False)
    unread = [a for a in articles if not a.is_read]
    return templates.TemplateResponse(
        "kindle/list.html",
        {"request": request, "articles": unread, "total": len(articles)},
    )


@router.get("/{article_id}", response_class=HTMLResponse)
async def kindle_read(
    request: Request, article_id: int, db: AsyncSession = Depends(get_db)
):
    if not _is_authenticated(request):
        return _login_redirect(f"/kindle/{article_id}")
    article = await article_service.get_by_id(db, article_id)
    if not article:
        return HTMLResponse("<p>Artículo no encontrado.</p>", status_code=404)
    content = clean_html(article.content_html)
    return templates.TemplateResponse(
        "kindle/read.html",
        {"request": request, "article": article, "content_html": content},
    )


@router.post("/{article_id}/read")
async def kindle_mark_read(
    request: Request, article_id: int, db: AsyncSession = Depends(get_db)
):
    if not _is_authenticated(request):
        return _login_redirect(f"/kindle/{article_id}")
    await article_service.mark_as_read(db, article_id)
    return RedirectResponse(url="/kindle/", status_code=303)
