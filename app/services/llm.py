from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import pandas as pd
import os
from dotenv import load_dotenv


load_dotenv()
if not os.getenv("GROQ_API_KEY"):
    raise EnvironmentError("GROQ_API_KEY environment variable is not set. Please configure it in the .env file.")

llm = ChatGroq(
    model="llama-3.1-8b-instant",  
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3
)

def analyze_csv(csv_path: str):
    df = pd.read_csv(csv_path)
    summary = df.describe(include="all").to_string()

    prompt = PromptTemplate.from_template("""
    You are a business analyst. Analyze the following data summary and provide:
    1. Key metrics
    2. Trends
    3. High-level recommendations
    Data summary:
    {summary}
    """)

    response = llm.invoke(prompt.format(summary=summary))
    return response.content
