import google.generativeai as genai
import json
import os


try:
    print("Configuring the genai models before we go for LLM Searches")
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    models_present = genai.list_models()
    # for model in models_present:
    #     print(model)
    # models/gemini-1.5-flash-latest

    print('Genai is properly configured')
except KeyError:
    raise ValueError(
            "GOOGLE API KEY not found")

print("\n\n===== Run 2: Tool Use via LLM (simulated web search) =====")
# A dictionary to map tool names to their functions

def actual_web_search(query: str) -> str:
    print(f"\n--- TOOL CALL: Performing web search for: '{query}' ---")
    try:
        print("CALL API HERE")
    except Exception as e:
        return f"Error during web search: {e}"

TOOLS = {
    "web_search": actual_web_search,
}
def get_llm_response(conversation_history):
    """
     Calling an Actual Google LLM API using Model gemini-1.5-flash-latest
     """
    print(conversation_history)
    model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
    system_instruction = (
        "You are an AI agent. "
        "Your goal is to answer the user's question. "
        "If you need to use a tool to get information, respond with a JSON object "
        "like this: `{\"tool_name\": \"<tool_name>\", \"tool_args\": {\"<arg_name>\": \"<arg_value>\"}}`. "
        "Available tools: web_search(query: str) - Use this for general knowledge queries or to get current information. "
        "Otherwise, respond directly with the answer."
        "Only use the tools you have been provided with."
        "Make sure the JSON is valid and complete."
    )
    full_prompt = f"{system_instruction}\n\nUser's request: {conversation_history}"
    print(f"\n--- LLM Prompting ---")
    print(f"Prompt sent to LLM:\n{full_prompt}\n")
    try:
        response = model.generate_content("What is the weather in Tampa, Florida?")
        llm_output = response.text
        print(f"LLM Raw Output: {llm_output}")
        return "SUCCESS"
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return "An error occurred while communicating with the AI. Please try again."


def run_agent(user_query):
    print(f"User Query: {user_query}")
    print('Agent will retry 3 times')
    conversation_history = [
        {"role": "user", "content": user_query}
    ]
    max_iterations = 3
    for i in range(max_iterations):
        llm_output = get_llm_response(conversation_history[-1]['content'])
        try:
            tool_call = json.loads(llm_output)
            tool_name = tool_call.get("tool_name")
            tool_args = tool_call.get("tool_args", {})
            if tool_name and tool_name in TOOLS:
                print(f"\n--- AGENT ACTION: Calling tool '{tool_name}' with args {tool_args} ---")
                tool_function = TOOLS[tool_name]
                tool_result = tool_function(**tool_args)
                print(f"Tool Result: {tool_result}")
            else:
                # If it tried to be a tool but was invalid, or didn't provide a valid tool.
                print(
                    "\n--- AGENT ACTION: LLM provided an invalid tool call or unexpected JSON. Answering directly based on last LLM output. ---")
                print(f"Final Agent Response: {llm_output}")
                return  # Exit as the agent tried to do something else or is done
        except json.JSONDecodeError:
            # If the LLM output is not a JSON (meaning it's a direct answer)
            print("\n--- AGENT ACTION: LLM provided a direct answer. ---")
            print(f"Final Agent Response: {llm_output}")
            return  # Exit, as the agent has produced a final answer
        except Exception as e:
            print(f"\n--- AGENT ERROR: {e}. Answering directly based on last LLM output. ---")
            print(f"Final Agent Response: {llm_output}")
            return

run_agent("What is the current weather in Loughman, Florida?")