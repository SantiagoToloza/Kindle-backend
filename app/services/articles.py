from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.services.scraper import scraper_service


class ArticleService:

    async def get_all(self, db: AsyncSession, unread_only: bool = False) -> list[Article]:
        query = select(Article).order_by(Article.created_at.desc())
        if unread_only:
            query = query.where(Article.is_read == False)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_id(self, db: AsyncSession, article_id: int) -> Article | None:
        result = await db.execute(select(Article).where(Article.id == article_id))
        return result.scalar_one_or_none()

    async def get_by_url(self, db: AsyncSession, url: str) -> Article | None:
        result = await db.execute(select(Article).where(Article.url == url))
        return result.scalar_one_or_none()

    async def create_from_url(self, db: AsyncSession, url: str) -> Article:
        # Si ya existe, devolvemos el existente
        existing = await self.get_by_url(db, url)
        if existing:
            return existing

        data = await scraper_service.fetch_article(url)
        article = Article(url=url, **data)
        db.add(article)
        await db.commit()
        await db.refresh(article)
        return article

    async def mark_as_read(self, db: AsyncSession, article_id: int) -> Article | None:
        from datetime import datetime

        article = await self.get_by_id(db, article_id)
        if not article:
            return None
        article.is_read = True
        article.read_at = datetime.utcnow()
        await db.commit()
        await db.refresh(article)
        return article

    async def delete(self, db: AsyncSession, article_id: int) -> bool:
        article = await self.get_by_id(db, article_id)
        if not article:
            return False
        await db.delete(article)
        await db.commit()
        return True


article_service = ArticleService()
