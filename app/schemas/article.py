from datetime import datetime

from pydantic import BaseModel, HttpUrl


class ArticleCreate(BaseModel):
    url: HttpUrl


class ArticleOut(BaseModel):
    id: int
    url: str
    title: str
    author: str | None
    site_name: str | None
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ArticleDetail(ArticleOut):
    content_html: str
