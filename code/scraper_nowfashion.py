import asyncio
import re
from pathlib import Path
from playwright.async_api import async_playwright
import httpx

BRANDS = [
    ("bv", "bottega-veneta"),
    ("lv", "louis-vuitton"),
]

MAX_SEARCH_PAGES = 10
MAX_COLLECTIONS = 50


async def get_collection_urls(page, brand_slug: str) -> list[str]:
    """Découvre toutes les URLs de collections pour une marque.
    Filtre strict : URL doit contenir le slug de la marque ET une année (20XX).
    """
    urls = []
    query = brand_slug.replace("-", "+")

    for page_num in range(1, MAX_SEARCH_PAGES + 1):
        if page_num == 1:
            search_url = f"https://nowfashion.com/?s={query}"
        else:
            search_url = f"https://nowfashion.com/page/{page_num}/?s={query}"

        print(f"   Recherche page {page_num} : {search_url}")

        try:
            response = await page.goto(search_url, wait_until="networkidle", timeout=20000)
            if response.status == 404:
                print(f"   → Plus de pages de résultats")
                break
        except Exception as e:
            print(f"   → Erreur : {e}")
            break

        links = await page.query_selector_all("a[href]")
        new_found = 0
        for link in links:
            href = (await link.get_attribute("href") or "").strip().rstrip("/")
            # Filtre strict : slug marque + année 4 chiffres dans l'URL
            if (
                brand_slug in href
                and re.search(r"20\d{2}", href)
                and "nowfashion.com/" in href
                and href not in urls
            ):
                urls.append(href)
                new_found += 1

        print(f"   → {new_found} nouvelles collections (total : {len(urls)})")

        if new_found == 0:
            print(f"   → Aucune nouvelle collection, arrêt de la recherche")
            break

        if len(urls) >= MAX_COLLECTIONS:
            break

        await asyncio.sleep(1)

    urls = list(dict.fromkeys(urls))
    print(f"\n   {len(urls)} collections valides trouvées pour {brand_slug}")
    return urls[:MAX_COLLECTIONS]


async def scrape_collection(page, brand: str, collection_url: str) -> int:
    """Scrape toutes les images d'une collection."""
    print(f"\n   → {collection_url}")

    try:
        response = await page.goto(
            collection_url, wait_until="networkidle", timeout=30000
        )
        if response.status != 200:
            print(f"     Statut {response.status}, skip")
            return 0
    except Exception as e:
        print(f"     Erreur navigation : {e}")
        return 0

    # Scroll pour déclencher le lazy loading
    for _ in range(3):
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(1500)
    await page.evaluate("window.scrollTo(0, 0)")
    await page.wait_for_timeout(500)

    # Extrait les URLs d'images de looks
    imgs = await page.query_selector_all("img[src*='media.nowfashion.com']")

    img_urls = set()
    for img in imgs:
        src = (await img.get_attribute("src") or "").strip()
        if (
            src
            and "wp-content/uploads" in src
            and src.lower().endswith(".jpg")
        ):
            img_urls.add(src)

    if not img_urls:
        print(f"     Aucune image trouvée")
        return 0

    # Nom du dossier = slug de l'URL
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
                    print(f"     HTTP {r.status_code} pour image {i}")
            except Exception as e:
                print(f"     Erreur image {i} : {e}")

    print(f"     ✓ {downloaded}/{len(img_urls)} images téléchargées")
    return downloaded


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )

        grand_total = 0

        for brand, brand_slug in BRANDS:
            print(f"\n{'='*50}")
            print(f" {brand.upper()} — {brand_slug}")
            print(f"{'='*50}")

            # Étape 1 : découverte des collections
            collection_urls = await get_collection_urls(page, brand_slug)

            if not collection_urls:
                print(f"   Aucune collection trouvée pour {brand_slug}")
                continue

            # Étape 2 : scraping de chaque collection
            brand_total = 0
            for i, url in enumerate(collection_urls, 1):
                print(f"\n [{i}/{len(collection_urls)}]", end="")
                count = await scrape_collection(page, brand, url)
                brand_total += count
                await asyncio.sleep(1.5)

            print(f"\n{'─'*50}")
            print(f" ✓ {brand.upper()} terminé : {brand_total} images au total")
            grand_total += brand_total

        await browser.close()

    print(f"\n{'='*50}")
    print(f" TOTAL GLOBAL : {grand_total} images")
    print(f"{'='*50}")


if __name__ == "__main__":
    asyncio.run(main())
