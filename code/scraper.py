import asyncio
import re
from pathlib import Path
from playwright.async_api import async_playwright
import httpx

BRANDS = [
    ("bv", "bottega veneta"),
    ("lv", "louis vuitton"),
]

SEARCH_URL = "https://nowfashion.com/?s={query}"
MAX_PAGES = 10        # pages de résultats de recherche
MAX_COLLECTIONS = 50  # collections max par marque


async def get_collection_urls(page, brand_query: str) -> list[str]:
    """Découvre toutes les URLs de collections pour une marque."""
    urls = []
    query = brand_query.replace(" ", "+")

    for page_num in range(1, MAX_PAGES + 1):
        if page_num == 1:
            url = SEARCH_URL.format(query=query)
        else:
            url = f"https://nowfashion.com/page/{page_num}/?s={query}"

        print(f"   Recherche page {page_num} : {url}")
        response = await page.goto(url, wait_until="networkidle")

        if response.status == 404:
            print(f"   → Plus de pages à l'index {page_num}")
            break

        # Récupère tous les liens d'articles
        links = await page.query_selector_all("a[href*='nowfashion.com']")
        page_urls = []
        for link in links:
            href = await link.get_attribute("href") or ""
            # Filtre : URLs de collections (pas les pages de catégorie, admin, etc.)
            if (
                "nowfashion.com/" in href
                and href not in urls
                and href not in page_urls
                and not any(x in href for x in [
                    "/category/", "/tag/", "/page/", "/?", "/wp-",
                    "/about", "/contact", "#", "/cart", "/shop"
                ])
                and len(href.split("/")) >= 4  # au moins un slug
            ):
                page_urls.append(href)

        if not page_urls:
            print(f"   → Aucun lien trouvé, arrêt")
            break

        urls.extend(page_urls)
        print(f"   → {len(page_urls)} collections trouvées sur cette page")

        if len(urls) >= MAX_COLLECTIONS:
            break

        await asyncio.sleep(1)

    # Dédoublonnage
    urls = list(dict.fromkeys(urls))
    print(f"   Total découvert : {len(urls)} collections")
    return urls[:MAX_COLLECTIONS]


async def scrape_collection(page, brand: str, collection_url: str) -> int:
    """Scrape toutes les images d'une collection."""
    print(f"\n   → {collection_url}")

    try:
        response = await page.goto(collection_url, wait_until="networkidle", timeout=30000)
        if response.status != 200:
            print(f"     Statut {response.status}, skip")
            return 0
    except Exception as e:
        print(f"     Erreur navigation : {e}")
        return 0

    # Scroll pour charger le lazy loading
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await page.wait_for_timeout(2000)
    await page.evaluate("window.scrollTo(0, 0)")
    await page.wait_for_timeout(1000)

    # Récupère toutes les images depuis media.nowfashion.com
    imgs = await page.query_selector_all("img[src*='media.nowfashion.com']")

    img_urls = set()
    for img in imgs:
        src = await img.get_attribute("src") or ""
        # Filtre : seulement les images de looks (pas logos, icônes)
        if src and ".jpg" in src.lower() and "wp-content/uploads" in src:
            img_urls.add(src)

    if not img_urls:
        print(f"     Aucune image trouvée")
        return 0

    # Nom du dossier à partir du slug de l'URL
    slug = collection_url.rstrip("/").split("/")[-1]
    out_dir = Path(f"data/{brand}/{slug}")
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"     {len(img_urls)} images → {out_dir}")

    downloaded = 0
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        for i, img_url in enumerate(sorted(img_urls)):
            filename = out_dir / f"look_{i:03d}.jpg"
            if filename.exists():
                downloaded += 1
                continue
            try:
                r = await client.get(img_url)
                if r.status_code == 200:
                    filename.write_bytes(r.content)
                    downloaded += 1
                else:
                    print(f"     Erreur HTTP {r.status_code} pour {img_url}")
            except Exception as e:
                print(f"     Erreur téléchargement look {i} : {e}")

    print(f"     ✓ {downloaded}/{len(img_urls)} images téléchargées")
    return downloaded


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36"
        )

        grand_total = 0

        for brand, query in BRANDS:
            print(f"\n{'='*50}")
            print(f" {brand.upper()} — {query}")
            print(f"{'='*50}")

            # Étape 1 : découverte des collections
            collection_urls = await get_collection_urls(page, query)

            if not collection_urls:
                print(f"   Aucune collection trouvée pour {brand}")
                continue

            # Étape 2 : scraping de chaque collection
            brand_total = 0
            for i, url in enumerate(collection_urls, 1):
                print(f"\n [{i}/{len(collection_urls)}]", end="")
                count = await scrape_collection(page, brand, url)
                brand_total += count
                await asyncio.sleep(1.5)  # politesse

            print(f"\n{'─'*50}")
            print(f" ✓ {brand.upper()} terminé : {brand_total} images au total")
            grand_total += brand_total

        await browser.close()

    print(f"\n{'='*50}")
    print(f" TOTAL GLOBAL : {grand_total} images")
    print(f"{'='*50}")


if __name__ == "__main__":
    asyncio.run(main())