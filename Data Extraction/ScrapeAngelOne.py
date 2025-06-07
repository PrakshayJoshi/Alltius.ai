from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import json

# --- setup driver ---
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# --- load support page ---
start_url = "https://www.angelone.in/support"
driver.get(start_url)
time.sleep(5)  # let the JS render

soup = BeautifulSoup(driver.page_source, "html.parser")

# --- find the Quick Links container (by its heading) ---
#    We look for the section titled “Quick Links (10)”
quick_section = soup.find("h6", string=lambda t: t and "Quick Links" in t)
if not quick_section:
    raise RuntimeError("Couldn't find the Quick Links header!")
container = quick_section.find_next_sibling("ul")  # assume the list is next

# --- collect all the 'Learn More' anchors under that container ---
# after loading start_url and soup = BeautifulSoup(…)
learn_more_anchors = soup.find_all(
    "a",
    string=lambda txt: txt and "Learn More" in txt
)

all_links = []
for a in learn_more_anchors:
    href = a.get("href")
    if not href or href.startswith("javascript"):
        continue
    # normalize to absolute
    if href.startswith("/"):
        href = "https://www.angelone.in" + href
    elif not href.startswith("http"):
        href = "https://www.angelone.in/" + href
    if href not in all_links:
        all_links.append(href)

print(f"Found {len(all_links)} article URLs")


# --- fetch each article’s content ---
support_data = []
for link in all_links:
    try:
        print("Visiting", link)
        driver.get(link)
        time.sleep(3)
        page = BeautifulSoup(driver.page_source, "html.parser")
        title = page.find("h1").get_text(strip=True) if page.find("h1") else page.title.string
        # collect the main body text (e.g. all <p> under the article)
        content = "\n".join(p.get_text(strip=True)
                            for p in page.select("article p") if p.get_text(strip=True))
        support_data.append({"url": link, "title": title, "content": content})
    except Exception as e:
        print(f"  → skipped {link}: {e}")

driver.quit()

# --- save to JSON ---
with open("angelone_support_articles.json", "w", encoding="utf-8") as f:
    json.dump(support_data, f, ensure_ascii=False, indent=2)

print("Done. Articles saved:", len(support_data))
