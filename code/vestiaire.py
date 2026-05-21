import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

OUT_DIR = Path("figures")
OUT_DIR.mkdir(exist_ok=True)

BRANDS = {
    "bv": "bottega+veneta",
    "lv": "louis+vuitton",
}

MAX_PAGES = 15


def parse_jsonld(html: str, brand: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script", {"type": "application/ld+json"})
    if not script:
        return []
    try:
        data = json.loads(script.string)
    except Exception:
        return []
    items = []
    for entry in data.get("itemListElement", []):
        product = entry.get("item", {})
        offer = product.get("offers", {})
        price = offer.get("price")
        if not price:
            continue
        original_price = None
        price_spec = offer.get("priceSpecification", {})
        if price_spec:
            original_price = price_spec.get("price")
        items.append({
            "brand": brand,
            "name": product.get("name", ""),
            "color": product.get("color", ""),
            "price_eur": float(price),
            "original_price_eur": float(original_price) if original_price else None,
            "url": product.get("url", ""),
            "product_id": product.get("productID", ""),
        })
    return items


async def scrape_brand(page, brand: str, query: str) -> list[dict]:
    all_items = []
    seen_ids = set()

    for p in range(1, MAX_PAGES + 1):
        url = f"https://fr.vestiairecollective.com/search/?q={query}&page={p}"
        print(f"  Page {p}/{MAX_PAGES}", end="\r")
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)
            html = await page.content()
            items = parse_jsonld(html, brand)
            if not items:
                print(f"\n  Aucun item page {p}, arrêt")
                break
            new = [i for i in items if i["product_id"] not in seen_ids]
            if not new:
                print(f"\n  Plus de nouveaux items, arrêt")
                break
            for i in new:
                seen_ids.add(i["product_id"])
            all_items.extend(new)
            await asyncio.sleep(1.5)
        except Exception as e:
            print(f"\n  Erreur : {e}")
            break

    print(f"\n  ✓ {brand.upper()} : {len(all_items)} items")
    if all_items:
        prices = [i["price_eur"] for i in all_items]
        print(f"  Prix min: {min(prices)}€ | max: {max(prices)}€ | médiane: {sorted(prices)[len(prices)//2]}€")
    return all_items


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        )
        all_results = {}
        for brand, query in BRANDS.items():
            print(f"\n{'='*50}\n {brand.upper()}\n{'='*50}")
            items = await scrape_brand(page, brand, query)
            all_results[brand] = items
            await asyncio.sleep(3)
        await browser.close()

    out = OUT_DIR / "vestiaire.json"
    with open(out, "w") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Sauvegardé → {out}")
    for brand, items in all_results.items():
        print(f"  {brand.upper()} : {len(items)} items")

asyncio.run(main())