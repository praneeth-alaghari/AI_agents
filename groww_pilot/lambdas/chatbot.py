import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from infra.openai_secrets import OPENAI_API_KEY

# Initialize the memory and ChatOpenAI model
memory = ConversationBufferMemory(return_messages=True)
llm = ChatOpenAI(model_name="gpt-4o-mini", openai_api_key=OPENAI_API_KEY)

# Initialize the conversation chain
conversation_chain = ConversationChain(llm=llm, memory=memory)

def chatbot_interface():
    
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # User input at the bottom
    user_input = st.text_input("You: ", key="user_input")

    if user_input:
        # Get the bot response from the conversation chain
        bot_response = conversation_chain.predict(input=user_input)

        # Update chat history
        st.session_state["chat_history"].append(("user", user_input))
        st.session_state["chat_history"].append(("bot", bot_response))

        # Explicitly clear the input after sending it
        # st.session_state["user_input"] = ""

    # Display chat messages after processing
    for role, msg in st.session_state["chat_history"]:
        if role == "user":
            st.write(f"<div style='text-align: right;'><strong>{role.capitalize()}:</strong> {msg}</div>", unsafe_allow_html=True)
        else:
            st.write(f"<div style='text-align: left;'><strong>{role.capitalize()}:</strong> {msg}</div>", unsafe_allow_html=True)
