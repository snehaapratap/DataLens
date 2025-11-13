import os
from langchain.agents import initialize_agent, Tool
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from app.services.vision import extract_image_caption
from app.services.llm import analyze_csv

def generate_report_with_agent(csv_path, image_path):
    csv_summary = analyze_csv(csv_path)
    vision_summary = extract_image_caption(image_path)

    llm = ChatGroq(
        model="llama-3.1-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.3
    )

    tools = [
        Tool(
            name="CSV Insight",
            func=lambda _: csv_summary,
            description="Provides insights from tabular CSV data"
        ),
        Tool(
            name="Vision Insight",
            func=lambda _: vision_summary,
            description="Provides insights from the uploaded image"
        ),
    ]

    agent = initialize_agent(tools, llm, agent_type="zero-shot-react-description", verbose=True)

    result = agent.run(
        "Combine all insights into a structured JSON report "
        "with fields: summary, key_metrics, trends, and recommendations."
    )
    return result