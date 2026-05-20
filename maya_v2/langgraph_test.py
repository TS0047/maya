import json 
from typing import TypedDict

from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage,SystemMessage
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph,START,END


from AppOpener import give_appnames,open


class chat_state(TypedDict):
    messages : list

@tool
def get_news():
    """ returns a str list of recent news headlines in the world"""
    print("news tool called")
    return ["the ayatholla is dead", "the sun is said to burst in 10 days","stock prices go very low due to the appocalypse","crime rate increases due to the 10 day dooms day limit"]

@tool
def get_my_apps():
    """
    returns all the available apps on the desktop as a dictionary 
    """
    apps = list(give_appnames())
    print("get_my_apps called")
    return apps

@tool
def open_app(app_name:str):
    """
    opens the apps based on their names

    Args:
        app_name : the app that needs to be opened as a string 
    """
    print("open_app called")
    try:
        open(app_name)
        return f"opened {app_name} succesfully"
    except Exception as e:
        return f"exeption : {e} found while opening the app {app_name}"

tools = [get_news, get_my_apps, open_app]
tool_descriptions = "\n".join(f"- {t.name}: {t.description}" for t in tools)

llm = init_chat_model("qwen2.5:7b",model_provider="ollama")
llm = llm.bind_tools([get_news,get_my_apps,open_app])

raw_llm = init_chat_model("qwen2.5-coder:7b",model_provider="ollama")
raw_llm.bind_tools([get_news,get_my_apps,open_app])

def expand_prompt(state):
    system_prompt = (
    "You are a task planning agent for a desktop AI assistant.\n"
    "You have access to ONLY these tools:\n"
    f"{tool_descriptions}\n"
    "Your job: convert a vague user request into a clear, numbered step-by-step execution plan.\n"
    "Rules:\n"
    "1. Use ONLY the tools listed above. Never invent tools.\n"
    "2. Reference tools by exact name.\n"
    "3. If a step depends on a previous step's output, state that explicitly.\n"
    "4. Never answer the request yourself — only plan the steps.\n"
    "Output: a numbered list of steps, nothing else."
    )
    
    serialized_messages = []
    for m in state['messages']:
        if hasattr(m, 'dict'):
            serialized_messages.append(m.model_dump())
        elif isinstance(m, dict):
            serialized_messages.append(m)
        else:
            serialized_messages.append({'content': str(m)})
    
    response = {'contexts': serialized_messages, 'iterations': [], 'system instructions': system_prompt}
    for i in range(0, 2):
        lol = raw_llm.invoke(json.dumps(response)).content
        response['iterations'] = response['iterations'] + [lol]
        print(f"{i}th thinking .", end=" ")
        print(lol)
        print("-"*50)
    return response['iterations'][-1]


SYSTEM = SystemMessage(content=(
    "You are Maya, a desktop AI assistant.\n"
    "You have ONLY these tools: get_news, get_my_apps, open_app.\n"
    "IMPORTANT: Never write code or pseudocode. Only call tools directly.\n"
    "Never explain what you will do — just call the tool.\n"
    "Complete the task autonomously without asking the user anything."
))

def llm_node(state):
    response = llm.invoke(state['messages'])
    return {'messages' : state['messages'] + [response]}

def router(state):
    last_message = state['messages'][-1]
    return 'tools' if getattr(last_message,'tool_calls',None) else 'end'



tool_node = ToolNode([get_news,get_my_apps,open_app])

builder = StateGraph(chat_state)

builder.add_node('llm',llm_node)
builder.add_node('tools',tool_node)
builder.add_edge(START,'llm')
builder.add_edge('tools','llm')
builder.add_conditional_edges('llm', router,{'tools':'tools' , 'end' : END})

graph = builder.compile()



if __name__ == '__main__':
    state = {'messages' : []}

    while True:
        user_message = input('> ')
        
        if user_message.lower() == 'quit':
            break
    
        state['messages'].append({'role' : 'user', 'content' : user_message})

        expanded_prompt = expand_prompt(state)
        state['messages'][-1] = {'role' : 'user', 'content' : expanded_prompt}

        state = graph.invoke(state)

        print("maya : " + state['messages'][-1].content)
