from bs4 import BeautifulSoup


def clean_html(html: str) -> str:
    """
    Limpia el HTML de readability para renderizar en la Kindle:
    - Remueve img, iframe, video, audio, script
    - Remueve atributos style y class inline
    """
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.find_all(["img", "iframe", "video", "audio", "script", "figure"]):
        tag.decompose()

    for tag in soup.find_all(True):
        tag.attrs.pop("style", None)
        tag.attrs.pop("class", None)
        tag.attrs.pop("id", None)

    return str(soup)
