import json
import requests
from bs4 import BeautifulSoup
from collections import deque
from urllib.parse import urljoin, urlparse

BASE_URL = "https://www.angelone.in/support"

def is_web_url(url):
    scheme = urlparse(url).scheme
    return scheme in ("http", "https")

def discover_support_pages(start_url):
    seen = set()
    queue = deque([start_url])

    while queue:
        url = queue.popleft()
        if url in seen:
            continue
        seen.add(url)

        try:
            resp = requests.get(url)
            resp.raise_for_status()
        except Exception:
            continue  # skip unfetchable URLs

        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a", href=True):
            full = urljoin(start_url, a["href"])
            if (
                "support" in full.lower()
                and full not in seen
                and is_web_url(full)
            ):
                queue.append(full)

    return seen - {start_url}

def scrape_faq_page(url):
    try:
        resp = requests.get(url)
        resp.raise_for_status()
    except Exception:
        return []  # skip this page entirely on error

    soup = BeautifulSoup(resp.text, "html.parser")
    faqs = []
    for section in soup.find_all("div", class_="tab"):
        label = section.find("label", class_="tab-label")
        q_span = label.find("span") if label else None
        question = q_span.get_text(strip=True) if q_span else None

        content_div = section.find("div", class_="tab-content")
        answer = content_div.get_text(" ", strip=True) if content_div else None

        if question and answer:
            faqs.append({"question": question, "answer": answer})

    return faqs

def main():
    english_faqs = []
    hindi_faqs = []

    support_pages = discover_support_pages(BASE_URL)
    for page in support_pages:
        faqs = scrape_faq_page(page)
        if "hindi" in page.lower():
            hindi_faqs.extend(faqs)
        else:
            english_faqs.extend(faqs)

    # Write out to JSON files
    with open("english_faqs.json", "w", encoding="utf-8") as f_en:
        json.dump(english_faqs, f_en, ensure_ascii=False, indent=2)

    with open("hindi_faqs.json", "w", encoding="utf-8") as f_hi:
        json.dump(hindi_faqs, f_hi, ensure_ascii=False, indent=2)

    print(f"Saved {len(english_faqs)} English FAQs to english_faqs.json")
    print(f"Saved {len(hindi_faqs)} Hindi FAQs to hindi_faqs.json")

if __name__ == "__main__":
    main()