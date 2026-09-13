"""
Streamlit UI for the Multi-Agent Research Pipeline — "DeepScout".

Run locally:
    streamlit run app.py

Deploy on Streamlit Community Cloud:
    - Push this repo to GitHub (make sure .env is in .gitignore!)
    - On share.streamlit.io, point to this file as the main app
    - Add your secrets (API keys) under App settings -> Secrets, using the
      same variable names you use in your .env file
"""

import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain

APP_NAME = "DeepScout"
APP_TAGLINE = (
    "Enter a topic and let a team of agents search the web, read the best "
    "sources, write a report, and critique it — end to end."
)

# --------------------------------------------------------------------------
# Setup
# --------------------------------------------------------------------------

load_dotenv()

# Let Streamlit Cloud "Secrets" populate env vars too.
# Accessing st.secrets raises if no secrets.toml exists at all (e.g. local dev
# without one), so this is wrapped in a try/except rather than a hasattr check.
try:
    for key, value in st.secrets.items():
        os.environ.setdefault(key, str(value))
except Exception:
    pass

st.set_page_config(
    page_title=f"{APP_NAME} — Multi-Agent Research Assistant",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------
# Styling
# --------------------------------------------------------------------------

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

        :root {
            --ds-accent-1: #6366f1;
            --ds-accent-2: #06b6d4;
        }

        .main > div { padding-top: 1.2rem; }
        footer { visibility: hidden; }
        #MainMenu { visibility: hidden; }

        /* ---- Hero ---- */
        .ds-hero {
            display: flex;
            align-items: center;
            gap: 0.9rem;
            margin-bottom: 0.2rem;
        }
        .ds-hero-icon {
            font-size: 2.6rem;
            line-height: 1;
        }
        .ds-hero-title {
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            font-size: 2.6rem;
            line-height: 1.1;
            background: linear-gradient(90deg, var(--ds-accent-1), var(--ds-accent-2));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 0;
        }
        .ds-hero-badge {
            display: inline-block;
            margin-top: 0.35rem;
            padding: 0.2rem 0.7rem;
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: var(--ds-accent-1);
            background: rgba(99, 102, 241, 0.12);
            border-radius: 999px;
        }
        .ds-tagline {
            font-size: 1.02rem;
            color: rgba(140, 140, 150, 0.95);
            margin-top: 0.5rem;
            margin-bottom: 1.3rem;
        }

        /* ---- Pipeline stepper ---- */
        .ds-stepper {
            display: flex;
            gap: 0.6rem;
            margin-bottom: 1.6rem;
            flex-wrap: wrap;
        }
        .ds-step {
            flex: 1;
            min-width: 150px;
            padding: 0.7rem 0.9rem;
            border-radius: 12px;
            background: rgba(120, 120, 120, 0.06);
            border: 1px solid rgba(120, 120, 120, 0.14);
        }
        .ds-step-num {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 22px; height: 22px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--ds-accent-1), var(--ds-accent-2));
            color: white;
            font-size: 0.72rem;
            font-weight: 700;
            margin-right: 0.4rem;
        }
        .ds-step-title { font-weight: 600; font-size: 0.92rem; }
        .ds-step-desc { font-size: 0.78rem; color: rgba(140,140,150,0.9); margin-top: 0.15rem; margin-left: 30px; }

        /* ---- Input row ---- */
        .stTextInput input {
            font-size: 1.05rem;
            border-radius: 10px !important;
        }
        div[data-testid="stFormSubmitButton"] button {
            background: linear-gradient(90deg, var(--ds-accent-1), var(--ds-accent-2));
            color: white;
            border: none;
            font-weight: 600;
            border-radius: 10px;
            height: 2.9rem;
        }
        div[data-testid="stFormSubmitButton"] button:hover {
            opacity: 0.92;
        }

        /* ---- Report card ---- */
        .report-card {
            background: rgba(120, 120, 120, 0.05);
            border: 1px solid rgba(120, 120, 120, 0.16);
            border-left: 4px solid var(--ds-accent-1);
            border-radius: 12px;
            padding: 1.5rem 1.7rem;
            line-height: 1.65;
        }
        .feedback-card {
            background: rgba(120, 120, 120, 0.05);
            border: 1px solid rgba(120, 120, 120, 0.16);
            border-left: 4px solid var(--ds-accent-2);
            border-radius: 12px;
            padding: 1.5rem 1.7rem;
            line-height: 1.65;
        }

        /* ---- Tabs ---- */
        .stTabs [data-baseweb="tab-list"] { gap: 4px; }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            font-weight: 500;
        }

        /* ---- Sidebar ---- */
        section[data-testid="stSidebar"] .ds-hero-title { font-size: 1.5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# Session state
# --------------------------------------------------------------------------

defaults = {
    "history": [],       # list of past runs
    "current": None,      # currently displayed run (dict)
    "running": False,
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------

with st.sidebar:
    st.markdown(
        f'<div class="ds-hero"><span class="ds-hero-icon">🧭</span>'
        f'<span class="ds-hero-title">{APP_NAME}</span></div>',
        unsafe_allow_html=True,
    )
    st.caption("Four agents. One report. Zero manual digging.")

    st.divider()
    st.markdown("##### How it works")
    st.markdown(
        "- **Search Agent** finds recent, reliable sources\n"
        "- **Reader Agent** picks the best URLs and scrapes them\n"
        "- **Writer** drafts a structured report\n"
        "- **Critic** reviews the report and gives feedback"
    )

    st.divider()
    st.markdown("##### Past topics")
    if st.session_state.history:
        for i, run in enumerate(reversed(st.session_state.history)):
            label = f"{run['topic'][:32]}{'…' if len(run['topic']) > 32 else ''}"
            if st.button(label, key=f"hist_{i}", use_container_width=True):
                st.session_state.current = run
    else:
        st.caption("No runs yet — your history will show up here.")

    st.divider()
    st.caption(f"Session started {datetime.now().strftime('%b %d, %Y')}")

# --------------------------------------------------------------------------
# Hero header
# --------------------------------------------------------------------------

st.markdown(
    f"""
    <div class="ds-hero">
        <span class="ds-hero-icon">🧭</span>
        <div>
            <div class="ds-hero-title">{APP_NAME}</div>
            <span class="ds-hero-badge">Multi-Agent Research Assistant</span>
        </div>
    </div>
    <div class="ds-tagline">{APP_TAGLINE}</div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="ds-stepper">
        <div class="ds-step">
            <div><span class="ds-step-num">1</span><span class="ds-step-title">Search</span></div>
            <div class="ds-step-desc">Finds recent, reliable sources</div>
        </div>
        <div class="ds-step">
            <div><span class="ds-step-num">2</span><span class="ds-step-title">Read</span></div>
            <div class="ds-step-desc">Scrapes the most relevant pages</div>
        </div>
        <div class="ds-step">
            <div><span class="ds-step-num">3</span><span class="ds-step-title">Write</span></div>
            <div class="ds-step-desc">Drafts a structured report</div>
        </div>
        <div class="ds-step">
            <div><span class="ds-step-num">4</span><span class="ds-step-title">Critique</span></div>
            <div class="ds-step-desc">Reviews it and flags gaps</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.form("research_form", clear_on_submit=False):
    col1, col2 = st.columns([5, 1])
    with col1:
        topic = st.text_input(
            "Research topic",
            placeholder="e.g. The impact of small modular reactors on grid decarbonization",
            label_visibility="collapsed",
        )
    with col2:
        submitted = st.form_submit_button(
            "🚀 Run research", use_container_width=True, disabled=st.session_state.running
        )

# --------------------------------------------------------------------------
# Pipeline execution (run inline so we can show live progress per stage)
# --------------------------------------------------------------------------

def run_pipeline_with_progress(topic: str) -> dict:
    state = {"topic": topic}

    with st.status("Running research pipeline…", expanded=True) as status:
        # 1. Search
        status.write("🔍 Searching for recent, reliable sources…")
        search_agent = build_search_agent()
        search_results = search_agent.invoke(
            {"messages": [("user", f"search for recent and reliable information on the topic: {topic}")]}
        )
        state["search_results"] = search_results["messages"][-1].content
        status.write("✅ Search complete.")

        # 2. Read
        status.write("📖 Reading and scraping the most relevant pages…")
        reader_agent = build_reader_agent()
        reader_results = reader_agent.invoke(
            {
                "messages": [
                    (
                        "user",
                        f"based on the results about {topic}, pick the most relevant urls and "
                        f"scrape them for detailed information "
                        f"search results : {state['search_results'][:800]}",
                    )
                ]
            }
        )
        state["scraped_content"] = reader_results["messages"][-1].content
        status.write("✅ Reading complete.")

        # 3. Write
        status.write("✍️ Drafting the report…")
        research_combined = (
            f"Search Results : {state['search_results']}\n\n"
            f"Scraped Content : {state['scraped_content']}"
        )
        state["report"] = writer_chain.invoke({"topic": topic, "research": research_combined})
        status.write("✅ Draft complete.")

        # 4. Critique
        status.write("🧐 Critiquing the report…")
        state["feedback"] = critic_chain.invoke({"report": state["report"]})
        status.write("✅ Critique complete.")

        status.update(label="Pipeline finished", state="complete", expanded=False)

    state["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    return state


def as_text(value) -> str:
    """Best-effort conversion of chain/agent output to plain text."""
    if isinstance(value, str):
        return value
    if hasattr(value, "content"):
        return value.content
    return str(value)


if submitted:
    if not topic or not topic.strip():
        st.warning("Please enter a topic before running the pipeline.")
    else:
        st.session_state.running = True
        try:
            result = run_pipeline_with_progress(topic.strip())
            st.session_state.history.append(result)
            st.session_state.current = result
        except Exception as e:
            st.error(f"The pipeline hit an error: {e}")
        finally:
            st.session_state.running = False

# --------------------------------------------------------------------------
# Results
# --------------------------------------------------------------------------

run = st.session_state.current

if run:
    report_text = as_text(run["report"])
    feedback_text = as_text(run["feedback"])

    st.divider()
    st.markdown(f"### Results — *{run['topic']}*")
    st.caption(f"Generated {run.get('timestamp', '')}")

    m1, m2, m3 = st.columns(3)
    m1.metric("Report length", f"{len(report_text.split())} words")
    m2.metric("Sources scraped", f"{len(run['scraped_content']):,} chars")
    m3.metric("Critique length", f"{len(feedback_text.split())} words")

    st.write("")

    tab_report, tab_feedback, tab_search, tab_scraped = st.tabs(
        ["📄 Report", "🧐 Critic Feedback", "🔍 Search Results", "📖 Scraped Content"]
    )

    with tab_report:
        st.markdown(f'<div class="report-card">{report_text}</div>', unsafe_allow_html=True)
        st.download_button(
            "⬇️ Download report (.md)",
            data=report_text,
            file_name=f"report_{run['topic'][:30].replace(' ', '_')}.md",
            mime="text/markdown",
        )

    with tab_feedback:
        st.markdown(f'<div class="feedback-card">{feedback_text}</div>', unsafe_allow_html=True)

    with tab_search:
        st.text_area("Raw search results", run["search_results"], height=400, label_visibility="collapsed")

    with tab_scraped:
        st.text_area("Raw scraped content", run["scraped_content"], height=400, label_visibility="collapsed")
else:
    st.info("Enter a topic above and click **Run research** to get started.")