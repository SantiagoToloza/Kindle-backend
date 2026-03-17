from datetime import datetime

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.articles import article_service
from app.services.kindle_cleaner import clean_html

router = APIRouter(prefix="/kindle", tags=["kindle"])
templates = Jinja2Templates(directory="app/templates")


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


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def kindle_list(request: Request, db: AsyncSession = Depends(get_db)):
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
    article_id: int, db: AsyncSession = Depends(get_db)
):
    await article_service.mark_as_read(db, article_id)
    return RedirectResponse(url="/kindle/", status_code=303)
