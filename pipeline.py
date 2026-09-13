from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain

def run_research_pipeline(topic: str) -> dict:
    state = {}

    #1. Search Agent
    search_agent = build_search_agent()
    search_results = search_agent.invoke({
        "messages": [("user", f"search for recent and reliable information on the topic: {topic}")]
    })
    state['search_results'] = search_results['messages'][-1].content
    print("search_results:", state['search_results'])

    #2. Reader Agent

    reader_agent = build_reader_agent()
    reader_results = reader_agent.invoke({
        "messages": [
            ("user", f"based on the results about {topic}, pick the most relevant urls and scrape them for detailed information"
             f" search results : {state['search_results'][:800]}")
        ]
    })
    state['scraped_content'] = reader_results['messages'][-1].content
    print("scraped_content:", state['scraped_content'])



    #3. Writer Chain

    research_combined = (
        f"Search Results : {state['search_results']}\n\n"
        f"Scraped Content : {state['scraped_content']}"
    )
    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })
    print("final report:", state["report"])

    #4. Critic Chain
    state["feedback"] = critic_chain.invoke({
        "report": state["report"]
    })

    print("critic report:", state["feedback"])

    return state


if __name__ == "__main__":
    topic = input("Enter the research topic: ")
    run_research_pipeline(topic)