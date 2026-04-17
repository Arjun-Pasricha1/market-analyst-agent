from typing import Annotated, List, TypedDict, Union
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    #Stores entire conversation history
    #add_messages tells langgraph to append new messages to the list
    messages: Annotated[List[BaseMessage],add_messages]

    #Our custo monologue variables
    ticker : str
    company_info : dict
    market_news : List[str]
    technical_indicators: dict
    final_report : str
    