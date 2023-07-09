import streamlit as st
from streamlit_chat import message

from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory

from langchain.agents import Tool
from langchain.tools import DuckDuckGoSearchRun
from langchain.agents import AgentType
from langchain.agents import initialize_agent, load_tools
from langchain.callbacks import StreamlitCallbackHandler

# from langchain import Wikipedia
# from langchain.agents.react.base import DocstoreExplorer

from dotenv import load_dotenv

# load .env
# OPENAIのAPIKEYを.envに記載
load_dotenv()

# Search
search = DuckDuckGoSearchRun()

def current_search(search_term):
    results = search.run(search_term, time=None, safesearch='Off', region='jp-jp')
    return results

# docstore = DocstoreExplorer(Wikipedia())
tools = [
    Tool(
        name = "Current Search",
        func=current_search,
        description="useful for when you need to answer questions about current events or the current state of the world"
    ),
    # Tool(
    #     name="Lookup",
    #     func=docstore.lookup,
    #     description="useful for when you need to ask with lookup",
    # ),
]
# 

# ChatGPT-3.5のモデルのインスタンスの作成
llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
# llm = ChatOpenAI(temperature=0)

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

def get_session_state(memory):
    if "state" not in st.session_state: 
        st.session_state.state = {"memory": memory} 
    return st.session_state.state

state = get_session_state(memory)

st.write(state['memory'].load_memory_variables({}))

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    memory=state['memory'],
    handle_parsing_errors=True,
    )

# Main
st.title("Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input():
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        st_callback = StreamlitCallbackHandler(st.container())
        # response = agent.run(prompt, callbacks=[st_callback])
        response = agent.run(prompt)
        st.write(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

