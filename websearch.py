import json

# --- 1. Define Tools the Agent Can Use ---
# In a real scenario, these would be actual functions or API calls.

def web_search(query: str) -> str:
    """
    Simulates a web search. In a real scenario, this would call a search engine API.
    """
    print(f"\n--- TOOL CALL: Performing web search for: '{query}' ---")
    # Simulate a search result based on common queries
    if "current weather in Loughman, Florida" in query.lower():
        return "The current weather in Loughman, Florida is partly cloudy with a temperature of 85°F (29°C) and high humidity."
    elif "population of New York City" in query.lower():
        return "The estimated population of New York City in 2023 was around 8.3 million people."
    elif "capital of France" in query.lower():
        return "The capital of France is Paris."
    else:
        return f"Simulated search result for '{query}': Information about this specific query is not readily available in this simulation."

# A dictionary to map tool names to their functions
TOOLS = {
    "web_search": web_search,
}

# --- 2. The Agent's "Brain" (Simulated LLM) ---
# In a real agent, this would be an API call to a powerful LLM.
# The LLM would be prompted to either give a direct answer or output a JSON
# structure indicating a tool to use.

def get_llm_response(prompt: str) -> str:
    """
    Simulates an LLM's response.
    In a real application, this would be an API call (e.g., OpenAI, Google Gemini).
    The prompt would guide the LLM to either answer directly or suggest a tool.
    """
    print(f"\n--- LLM Prompting ---")
    print(f"Prompt sent to LLM:\n{prompt}\n")

    # Simulate LLM's decision making based on the prompt
    if "current weather" in prompt.lower() and "Loughman, Florida" in prompt.lower():
        # LLM decides to use the web_search tool
        return json.dumps({
            "tool_name": "web_search",
            "tool_args": {"query": "current weather in Loughman, Florida"}
        })
    elif "population of New York City" in prompt.lower():
        # LLM decides to use the web_search tool
        return json.dumps({
            "tool_name": "web_search",
            "tool_args": {"query": "population of New York City"}
        })
    elif "capital of France" in prompt.lower():
        # LLM decides to use the web_search tool
        return json.dumps({
            "tool_name": "web_search",
            "tool_args": {"query": "capital of France"}
        })
    elif "hello" in prompt.lower() or "how are you" in prompt.lower():
        # LLM decides to answer directly
        return "Hello! I am a helpful AI agent. How can I assist you today?"
    else:
        # Default direct answer
        return "I can try to answer your question or use a tool if necessary. What would you like to know?"

# --- 3. The Agent Executive Loop ---
# This is where the agent observes, plans, acts, and reflects.

def run_agent(user_query: str):
    print(f"User Query: {user_query}")
    conversation_history = [
        {"role": "user", "content": user_query}
    ]

    max_iterations = 3 # Prevent infinite loops
    for i in range(max_iterations):
        # 1. Plan/Reason (LLM Call)
        # We instruct the LLM on how to respond (either direct or tool use).
        system_instruction = (
            "You are an AI agent. "
            "Your goal is to answer the user's question. "
            "If you need to use a tool to get information, respond with a JSON object "
            "like this: `{\"tool_name\": \"<tool_name>\", \"tool_args\": {\"<arg_name>\": \"<arg_value>\"}}`. "
            "Otherwise, respond directly with the answer."
        )
        prompt_to_llm = f"{system_instruction}\n\nUser's request: {conversation_history[-1]['content']}"

        llm_output = get_llm_response(prompt_to_llm)
        print(f"LLM Raw Output: {llm_output}")

        try:
            # Attempt to parse as a tool call
            tool_call = json.loads(llm_output)
            tool_name = tool_call.get("tool_name")
            tool_args = tool_call.get("tool_args", {})

            if tool_name and tool_name in TOOLS:
                print(f"\n--- AGENT ACTION: Calling tool '{tool_name}' with args {tool_args} ---")
                tool_function = TOOLS[tool_name]
                tool_result = tool_function(**tool_args)

                print(f"Tool Result: {tool_result}")
                # Add tool output to history for the next LLM turn (reflection)
                conversation_history.append({
                    "role": "tool_output",
                    "content": f"Tool '{tool_name}' result: {tool_result}"
                })
                # Now, re-prompt the LLM with the tool output to formulate the final answer
                conversation_history.append({
                    "role": "user",
                    "content": f"Based on the tool output: '{tool_result}', what is the answer to the original question: '{user_query}'?"
                })
            else:
                # If it tried to be a tool but was invalid, or didn't provide a valid tool.
                print("\n--- AGENT ACTION: LLM provided an invalid tool call or unexpected JSON. Answering directly based on last LLM output. ---")
                print(f"Final Agent Response: {llm_output}")
                return # Exit as the agent tried to do something else

        except json.JSONDecodeError:
            # If the LLM output is not a JSON (meaning it's a direct answer)
            print("\n--- AGENT ACTION: LLM provided a direct answer. ---")
            print(f"Final Agent Response: {llm_output}")
            return # Exit, as the agent has produced a final answer
        except Exception as e:
            print(f"\n--- AGENT ERROR: {e}. Answering directly based on last LLM output. ---")
            print(f"Final Agent Response: {llm_output}")
            return

    print("\n--- AGENT WARNING: Max iterations reached without a final answer. ---")
    # Fallback: if max iterations reached, try to output the last LLM response as the answer
    print(f"Final Agent Response (Fallback): {conversation_history[-1]['content']}")


# --- Sample Runs ---
print("\n===== Run 1: Direct Answer =====")
run_agent("Hello, how are you today?")

print("\n\n===== Run 2: Tool Use (Weather) =====")
run_agent("What is the current weather in Loughman, Florida?")

print("\n\n===== Run 3: Tool Use (Population) =====")
run_agent("What is the population of New York City?")

print("\n\n===== Run 4: Tool Use (Capital of France) =====")
run_agent("What is the capital of France?")

print("\n\n===== Run 5: Unknown Query (Default Direct Answer) =====")
run_agent("Tell me a story about a dragon.")