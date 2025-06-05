import json
import os
import requests
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain import hub
from langchain_community.utilities import SerpAPIWrapper
from langchain_core.messages import SystemMessage, HumanMessage
try:
    google_api_key = os.environ["GOOGLE_API_KEY"]
    # print(google_api_key)
except KeyError:
    raise ValueError(
        "GOOGLE_API_KEY environment variable not set. "
        "Please set it before running the script. "
        "Get your API key from https://aistudio.google.com/"
    )
try:
    serpapi_api_key = os.environ["SERPAPI_API_KEY"]
    # print(serpapi_api_key)
except KeyError:
    raise ValueError(
        "SERPAPI_API_KEY environment variable not set. "
        "Please set it before running the script. "
        "Get your API key from https://serpapi.com/"
    )
# print('Initializing the LLM Modules')
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7)
# print('Initialize the search wrapper')
# print('Performing a search query using SerpAPI')
query = "is it going rain tonight in my location?"  # Example search query


def search_query(query, serpapi_api_key):
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": serpapi_api_key,
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()  # Return the search results as JSON
    else:
        raise ValueError(f"Failed to fetch from SerpAPI. Status code: {response.status_code}")


search_results = search_query(query, serpapi_api_key)


if isinstance(search_results, dict):
    print(json.dumps(search_results, indent=4))
else:
    print("search_results is not a dictionary!")


# print(f"Search Results: {search_results}")
results_text = " ".join(
    [result.get("snippet", "") for result in search_results.get("organic_results", [])[:3]])
print(f"results_text : {results_text}")
