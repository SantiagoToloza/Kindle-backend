from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.article import ArticleCreate, ArticleDetail, ArticleOut
from app.services.articles import article_service

router = APIRouter(prefix="/api/articles", tags=["articles"])


@router.post("/", response_model=ArticleOut, status_code=201)
async def ingest_article(payload: ArticleCreate, db: AsyncSession = Depends(get_db)):
    """Recibe una URL, scrapea el contenido y lo guarda."""
    try:
        article = await article_service.create_from_url(db, str(payload.url))
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"No se pudo procesar la URL: {e}")
    return article


@router.get("/", response_model=list[ArticleOut])
async def list_articles(
    unread_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    """Lista todos los artículos (o solo los no leídos)."""
    return await article_service.get_all(db, unread_only=unread_only)


@router.get("/{article_id}", response_model=ArticleDetail)
async def get_article(article_id: int, db: AsyncSession = Depends(get_db)):
    """Devuelve el detalle completo con el HTML del artículo."""
    article = await article_service.get_by_id(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")
    return article


@router.patch("/{article_id}/read", response_model=ArticleOut)
async def mark_read(article_id: int, db: AsyncSession = Depends(get_db)):
    """Marca el artículo como leído."""
    article = await article_service.mark_as_read(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")
    return article


@router.delete("/{article_id}", status_code=204)
async def delete_article(article_id: int, db: AsyncSession = Depends(get_db)):
    """Elimina un artículo."""
    deleted = await article_service.delete(db, article_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")
