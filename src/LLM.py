from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
import os

def create_chains():
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    llm = ChatOpenAI(api_key=os.getenv('OPENAI_KEY'), model_name="gpt-4o-mini", temperature = 0.5)

    context_template = """ 
    Filter out the content of the following documents based on whether they provide useful context when answering the user's prompt.
    Return a single paragraph including the contents of each document that is useful when responding to the user's input.

    Documents: {documents}

    User's Input: {input}

    Assistant's Response: """

    context_prompt = PromptTemplate(
        input_variables=["documents", "input"],
        template = context_template
    )

    context_chain = context_prompt | llm

    response_template = """
    Respond to the user's input using the context when applicable.

    Context: {context}

    User's Input: {input}


    Assistant's Response: """

    response_prompt = PromptTemplate(
        input_variables=["context", "input"],
        template=response_template
    )

    response_chain = response_prompt | llm



    return context_chain, response_chain




