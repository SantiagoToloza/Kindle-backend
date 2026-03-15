import httpx
from bs4 import BeautifulSoup
from readability import Document


class ScraperService:
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; KindleReader/1.0; +https://github.com/you/kindle-reader)"
        )
    }

    async def fetch_article(self, url: str) -> dict:
        """
        Descarga la URL y extrae el contenido limpio con readability.
        Devuelve un dict con title, content_html, content_text, author, site_name.
        """
        async with httpx.AsyncClient(
            headers=self.HEADERS,
            follow_redirects=True,
            timeout=15.0,
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            html = response.text

        doc = Document(html)
        content_html = doc.summary(html_partial=True)
        title = doc.title()

        # Extraer texto plano del HTML limpio
        soup = BeautifulSoup(content_html, "lxml")
        content_text = soup.get_text(separator="\n", strip=True)

        # Intentar sacar author y site_name de meta tags
        raw_soup = BeautifulSoup(html, "lxml")
        author = self._get_meta(raw_soup, ["author", "article:author"])
        site_name = self._get_meta(raw_soup, ["og:site_name"])

        return {
            "title": title,
            "content_html": content_html,
            "content_text": content_text,
            "author": author,
            "site_name": site_name,
        }

    def _get_meta(self, soup: BeautifulSoup, names: list[str]) -> str | None:
        for name in names:
            tag = soup.find("meta", attrs={"name": name}) or soup.find(
                "meta", attrs={"property": name}
            )
            if tag and tag.get("content"):
                return tag["content"].strip()
        return None


scraper_service = ScraperService()
