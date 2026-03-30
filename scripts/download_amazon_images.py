#!/usr/bin/env python3
"""
Search Amazon for a query, find likely matching products, and download their images.

This is meant to run locally on your laptop with only the Python standard library.
It works best for simple product lookups like:

    python scripts/download_amazon_images.py "sabertooth 2x32"
    python scripts/download_amazon_images.py "12v 250w wiper motor" --limit 2 --images-per-product 2

Amazon changes markup often, so this is best-effort scraping for your own local use.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def fetch_text(url: str, timeout: int = 20) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def fetch_bytes(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Referer": "https://www.amazon.com/",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def normalize_product_url(url: str, market: str) -> str:
    if url.startswith("//"):
        url = "https:" + url
    elif url.startswith("/"):
        url = f"https://www.amazon.{market}{url}"
    parsed = urllib.parse.urlsplit(url)
    path = parsed.path
    match = re.search(r"/(dp|gp/product)/([A-Z0-9]{10})", path)
    if match:
        return f"https://www.amazon.{market}/{match.group(1)}/{match.group(2)}"
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, path, "", ""))


def extract_search_results(search_html: str, market: str) -> List[str]:
    patterns = [
        r'href="(/(?:[^"]*?/)?dp/[A-Z0-9]{10}[^"]*)"',
        r'href="(/gp/product/[A-Z0-9]{10}[^"]*)"',
    ]
    urls: List[str] = []
    seen = set()
    for pattern in patterns:
        for raw in re.findall(pattern, search_html):
            url = normalize_product_url(html.unescape(raw), market)
            if url not in seen:
                seen.add(url)
                urls.append(url)
    return urls


def extract_title(product_html: str) -> str:
    match = re.search(
        r'<span id="productTitle"[^>]*>\s*(.*?)\s*</span>',
        product_html,
        flags=re.S,
    )
    if not match:
        return ""
    return re.sub(r"\s+", " ", html.unescape(match.group(1))).strip()


def canonicalize_amazon_image(url: str) -> str:
    url = url.replace("\\u0026", "&").replace("\\/", "/")
    return re.sub(r"\._[^/]+_\.", ".", url)


def extract_image_urls(product_html: str) -> List[str]:
    found: List[str] = []
    seen = set()

    # First try the structured image entries Amazon often ships in page JSON.
    for match in re.findall(r'"(?:hiRes|large|mainUrl)"\s*:\s*"(https:[^"]+)"', product_html):
        url = canonicalize_amazon_image(match)
        if "m.media-amazon.com/images/I/" in url and url not in seen:
            seen.add(url)
            found.append(url)

    # Fallback: grab all Amazon media URLs and clean them up.
    for match in re.findall(r'https:\\/\\/m\.media-amazon\.com\\/images\\/I\\/[^"]+?\.(?:jpg|jpeg|png)', product_html):
        url = canonicalize_amazon_image(match)
        if url not in seen:
            seen.add(url)
            found.append(url)

    return found


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def score_product(query: str, title: str) -> int:
    q = set(tokenize(query))
    t = set(tokenize(title))
    return len(q & t)


def slugify(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower())
    text = text.strip("-")
    return text or "amazon-product"


def search_amazon(query: str, market: str) -> List[str]:
    search_url = f"https://www.amazon.{market}/s?k={urllib.parse.quote_plus(query)}"
    html_text = fetch_text(search_url)
    results = extract_search_results(html_text, market)
    if not results:
        raise RuntimeError("No Amazon product links were found. Amazon may have changed markup or blocked the request.")
    return results


def contains_required_terms(title: str, required_terms: Sequence[str]) -> bool:
    title_l = title.lower()
    return all(term.lower() in title_l for term in required_terms)


def choose_products(query: str, market: str, limit: int, delay: float, required_terms: Sequence[str]) -> List[Tuple[str, str, List[str]]]:
    candidates = search_amazon(query, market)
    scored: List[Tuple[int, str, str, List[str]]] = []

    for url in candidates[: max(limit * 3, 6)]:
        time.sleep(delay)
        try:
            product_html = fetch_text(url)
        except Exception:
            continue
        title = extract_title(product_html)
        image_urls = extract_image_urls(product_html)
        if required_terms and not contains_required_terms(title, required_terms):
            continue
        if not title or not image_urls:
            continue
        scored.append((score_product(query, title), title, url, image_urls))

    scored.sort(key=lambda item: (-item[0], item[1]))
    return [(title, url, image_urls) for _, title, url, image_urls in scored[:limit]]


def save_images(query: str, products: Sequence[Tuple[str, str, Sequence[str]]], outdir: Path, images_per_product: int, delay: float) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    manifest = []

    for idx, (title, url, image_urls) in enumerate(products, start=1):
        product_slug = slugify(title)[:80]
        print(f"\n[{idx}] {title}")
        print(f"    {url}")
        downloaded_files = []

        for img_idx, image_url in enumerate(image_urls[:images_per_product], start=1):
            ext = os.path.splitext(urllib.parse.urlsplit(image_url).path)[1] or ".jpg"
            filename = outdir / f"{idx:02d}-{product_slug}-{img_idx:02d}{ext}"
            time.sleep(delay)
            try:
                filename.write_bytes(fetch_bytes(image_url))
                downloaded_files.append(str(filename))
                print(f"    downloaded -> {filename}")
            except Exception as exc:
                print(f"    failed to download {image_url}: {exc}", file=sys.stderr)

        manifest.append(
            {
                "query": query,
                "title": title,
                "product_url": url,
                "downloaded_files": downloaded_files,
            }
        )

    (outdir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Search Amazon and download product images.")
    parser.add_argument("query", help="Search phrase, e.g. 'sabertooth 2x32'")
    parser.add_argument("--market", default="com", help="Amazon market suffix, e.g. com, co.uk, ca")
    parser.add_argument("--limit", type=int, default=3, help="How many products to keep")
    parser.add_argument("--images-per-product", type=int, default=1, help="How many images to download per product")
    parser.add_argument("--outdir", default="output/amazon-images", help="Output folder")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests in seconds")
    parser.add_argument("--must-contain", default="", help="Comma-separated terms that must appear in the product title")
    return parser.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    try:
        required_terms = [term.strip() for term in args.must_contain.split(",") if term.strip()]
        products = choose_products(args.query, args.market, args.limit, args.delay, required_terms)
        if not products:
            print("No product pages with downloadable images were found.", file=sys.stderr)
            return 1
        save_images(
            query=args.query,
            products=products,
            outdir=Path(args.outdir),
            images_per_product=args.images_per_product,
            delay=args.delay,
        )
        print(f"\nSaved results to {Path(args.outdir).resolve()}")
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
