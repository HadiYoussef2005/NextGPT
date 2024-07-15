import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAIError
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent
from langchain import hub
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.agents import AgentExecutor

load_dotenv()

os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
message_history = ChatMessageHistory()
search = TavilySearchResults()
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0125", api_key=os.getenv("OPEN_AI_KEY"))
tools = [search]
prompt = hub.pull("hwchase17/openai-functions-agent")
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)
chat_history = []

app = FastAPI()

class InputData(BaseModel):
    input_data: str

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post("/chatbot_query/")
def process_input(input_data: InputData): 
    chat_history_str = "\n".join(chat_history)

    query = f"{chat_history_str} {input_data.input_data}"
    
    try:
        output = agent_executor.invoke(
            {"input": query}
        )
    except OpenAIError as e:
        if e.http_status == 400:
            return {"error": "You reached the maximum conversation limit, please clear the conversation."}
        else:
            raise e

    chat_history.append("\nUser: " + input_data.input_data)
    chat_history.append("\nChatbot: " + output['output'])

    return {"output": output['output']}

@app.post("/clear_conversation/")
def clear_conversation():
    global chat_history
    chat_history = []
