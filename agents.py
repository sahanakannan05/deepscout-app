from langchain.agents import create_agent
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search , web_scraper
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatMistralAI(model = "open-mistral-nemo", temperature = 0, api_key = os.getenv("MISTRAL-API-KEY"))

 #1st agent

def build_search_agent():
    return create_agent(
        model = llm,
        tools = [web_search]
    )
 #2nd agent

def build_reader_agent() :
    return create_agent(
        model = llm,
        tools = [web_scraper]
    )
#writer chain

writer_prompt = ChatPromptTemplate.from_messages(
    [
    ("system", "You are a expert research writer. write clear, structured , insightful report"),
    ("human" , """ write a detailed report on the topic below.
    Topic : {topic}
    Research : {research}

    Structure the report as:
    Introduction
    Key Findings
    Analysis
    Conclusion
    Sources (list all url's used for research)

    Be detailed, factual and professional
    """)
    ]
)

writer_chain = writer_prompt | llm | StrOutputParser()

#critic chain

critic_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "you are a expert research critic. be honest and specific. you will review the report and provide feedback . "),
        ("human", """ review the report below and provide feedback.
        Report : {report}

        respond in this format:

        score : (0-10)
        Strengths :
        -
        -

        Areas for Improvement :
        - 
        - 
        one line summary of the report quality :
        """)
    ]
)

critic_chain = critic_prompt | llm | StrOutputParser() 
