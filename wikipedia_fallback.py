# wikipedia_fallback.py
import requests
from bs4 import BeautifulSoup

def get_wikipedia_plot(title):
    try:
        search_url = f"https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": title,
            "utf8": 1
        }

        search_res = requests.get(search_url, params=params).json()
        if not search_res["query"]["search"]:
            return None

        page_title = search_res["query"]["search"][0]["title"]

        page_url = f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
        page_html = requests.get(page_url).text
        soup = BeautifulSoup(page_html, "html.parser")

        # Find the "Plot" section
        plot_header = soup.find(id="Plot") or soup.find(id="Plot_summary")
        if not plot_header:
            return None

        plot_text = []
        for tag in plot_header.find_all_next():
            if tag.name == "h2":
                break
            if tag.name == "p":
                plot_text.append(tag.text)

        return "\n".join(plot_text).strip() if plot_text else None

    except Exception as e:
        print(f"❌ Wikipedia fetch failed for '{title}': {e}")
        return None
