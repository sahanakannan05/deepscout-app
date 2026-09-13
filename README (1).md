# 🧭 DeepScout

**A multi-agent research assistant that searches the web, reads the best sources, drafts a report, and critiques its own work — end to end, with zero manual digging.**

🔗 **Live demo:** https://deepscout-app-lf7bkvhexzvkry76twjrrd.streamlit.app/

---

## What it does

Give DeepScout a topic, and four specialized agents work in sequence to produce a polished, fact-checked research report:

| Stage | Role |
|---|---|
| 🔍 **Search Agent** | Finds recent, reliable sources on the topic |
| 📖 **Reader Agent** | Picks the most relevant URLs and scrapes them for detail |
| ✍️ **Writer** | Synthesizes everything into a structured report |
| 🧐 **Critic** | Reviews the report and flags gaps, weak claims, or missing context |

The result: instead of manually opening 10 browser tabs and piecing together notes, you get a single, structured report — plus a critique of that report's own quality.

## Screenshots

<!--
  How to add these:
  1. Create a folder named "screenshots" in your project root.
  2. Take screenshots of the app (e.g. the home screen, a run in progress, the final report tabs).
  3. Save them into that folder, e.g. screenshots/home.png, screenshots/results.png
  4. Replace the paths below to match your filenames, then commit + push the images along with this README.
  GitHub renders these automatically once the images are in the repo.
-->

**Home screen**
![DeepScout home screen](screenshots/home.png)

**Pipeline running**
![Pipeline in progress](screenshots/running.png)

**Final report + critic feedback**
![Results view](screenshots/results.png)
![critique view](screenshots/critique.png)

## Tech stack

- **LLM:** Mistral
- **Agent orchestration:** LangGraph (for the search and reader agents) + LangChain (chains for the writer and critic steps)
- **Search:** Tavily API
- **Web scraping:** BeautifulSoup
- **UI:** Streamlit
- **Deployment:** Streamlit Community Cloud

## Architecture

```
User topic
    │
    ▼
┌─────────────────┐
│  Search Agent    │  (LangGraph agent, Tavily tool)
│  finds sources   │
└────────┬─────────┘
         ▼
┌─────────────────┐
│  Reader Agent    │  (LangGraph agent, BeautifulSoup tool)
│  scrapes details │
└────────┬─────────┘
         ▼
┌─────────────────┐
│  Writer Chain    │  (LangChain, Mistral)
│  drafts report   │
└────────┬─────────┘
         ▼
┌─────────────────┐
│  Critic Chain    │  (LangChain, Mistral)
│  reviews report  │
└────────┬─────────┘
         ▼
   Final report + feedback
```

Each agent is a self-contained LangGraph agent with its own tool access, so the search step can't accidentally hallucinate URLs (it has to call Tavily), and the reader step can't fabricate scraped content (it has to call BeautifulSoup on real pages).

## Features

- **Live progress tracking** — watch each agent work in real time instead of waiting on a spinner
- **Tabbed results** — final report, critic feedback, and raw intermediate outputs (search results, scraped content) all separately viewable
- **Run history** — revisit past topics from the session without re-running the pipeline
- **Downloadable reports** — export the final report as a Markdown file
- **Secrets-based config** — API keys are never hardcoded; loaded via `.env` locally or Streamlit Secrets in production

## Running it locally

```bash
git clone https://github.com/sahanakannan05/<deepscout-app>.git
cd <deepscout-app>
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Create a `.env` file in the project root with your API keys:

```
MISTRAL_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
```

Then run:

```bash
streamlit run app.py
```

## Project structure

```
.
├── app.py              # Streamlit UI
├── pipeline.py          # Orchestrates the 4-agent pipeline
├── agents.py            # LangGraph agent + LangChain chain definitions
├── tools.py              # Tavily search tool + BeautifulSoup scraping tool
├── requirements.txt
└── .gitignore
```

## Why I built this

While writing my Research paper on AURA, my own smart assistive cane project for visually impaired users, I found myself buried in a scattered mess of sensor research papers, obstacle-detection benchmarks, and assistive-tech literature — all of it spread across dozens of tabs with no single place to synthesize it. DeepScout grew out of that frustration: I wanted an agent pipeline that could search, read, and draft a structured summary the way I wished I'd had while writing my own paper. Building it also forced me to get hands-on with multi-agent orchestration (LangGraph) and tool-calling agents in a way my coursework hadn't — designing agents that have to actually call a search API or scrape a real page, rather than hallucinating sources, was the hardest and most useful part.

---

*Built by [Sahana Kannan](https://github.com/sahanakannan05)*
