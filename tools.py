# Modern import path (LangChain 0.2+)

from langchain_core.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os

from dotenv import load_dotenv
load_dotenv()
tavily = TavilyClient(api_key = os.getenv("TAVILY-API-KEY"))

@tool
def web_search( query : str) -> str:
    """ 
    search the web for recent and reliable information on a given topic and return title, url and snippets.
    """
    results =   tavily.search( query = query, max_results=5)
    out = []

    for r in results['results']:
        out.append(
           f"Title: {r['title']}\n"
           f"URL: {r['url']}\n"
              f"Snippet: {r.get('snippet', r.get('content', ''))}\n"
        )

    return "\n".join(out)


@tool
def web_scraper(url : str) -> str:
    """ 
    scrape the web page at the given URL and return the clean text content for deep reading.
    """
    try:
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(["script", "style", "nav", "header", "footer"]):
            tag.decompose()  # Remove these tags
        return soup.get_text(separator=" ", strip=True)[:1000]  # Return first 1000 characters
    except Exception as e:
        return f"Error scraping the URL: {str(e)}"


