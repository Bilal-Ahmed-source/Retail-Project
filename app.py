import os
from dotenv import load_dotenv
import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

user = ""
password = ""
host = ""
name = ""
port = ""

def init_database(user: str, password: str, host: str, port: str, database: str) -> SQLDatabase:
  db_uri = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
  return SQLDatabase.from_uri(db_uri)

# Initialize DB and store in session_state
if "db" not in st.session_state:
    st.session_state.db = init_database(user, password, host, port, name)

def get_sql_chain(db):
    template = """
        You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
        Based on the table schema below, write a SQL query that would answer the user's question. Take the conversation history into account.
        
        <SCHEMA>{schema}</SCHEMA>
        
        Conversation History: {chat_history}
        
        Write only the SQL query and nothing else. Do not wrap the SQL query in any other text, not even backticks.
        
        For example:
        Question: List all customers in France with a credit limit over 20,000
        SQL Query: SELECT * FROM customers WHERE country = 'France' AND creditLimit > 20000;
        Question: Get the highest payment amount made by any customer.
        SQL Query: SELECT MAX(amount) FROM payments;
        Question: Show product details for products in the 'Motorcycles' product line.
        SQL Query: SELECT * FROM products WHERE productLine = 'Motorcycles';
        Question: Retrieve the names of employees who report to employee number 1002.
        SQL Query: SELECT firstName, lastName FROM employees WHERE reportsTo = 1002
        Question: List all products with a stock quantity less than 7000.
        SQL Query: SELECT productName, quantityInStock FROM products WHERE quantityInStock < 7000;
        Qestion: what is price of `1968 Ford Mustang`
        SQL Query: SELECT `buyPrice`, `MSRP` FROM products  WHERE `productName` = '1968 Ford Mustang' LIMIT 1;


        Your turn:
        
        Question: {question}
        SQL Query:
        """
    
    prompt = ChatPromptTemplate.from_template(template)

    llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")

    def get_schema(_):
        return db.get_table_info()
    
    return (
        RunnablePassthrough.assign(schema=get_schema)
        | prompt
        | llm
        | StrOutputParser()
    )

def get_response(user_query:str, db: SQLDatabase, chat_history: list):
    sql_chain = get_sql_chain(db)

    template = """
    You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
    Based on the table schema below, question, sql query, and sql response, write a natural language response.
    <SCHEMA>{schema}</SCHEMA>

    Conversation History: {chat_history}
    SQL Query: <SQL>{query}</SQL>
    User question: {question}
    SQL Response: {response}"""

    prompt = ChatPromptTemplate.from_template(template)

    llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")

    chain = (
        RunnablePassthrough.assign(query=sql_chain).assign(
            schema=lambda _: db.get_table_info(),
            response=lambda vars: db.run(vars["query"]),

        )
        | prompt
        | llm
        | StrOutputParser()

    )
    return chain.invoke({
        "question": user_query,
        "chat_history": chat_history
    })
 

if  "chat_history" not in st.session_state:
    st.session_state.chat_history =[
            AIMessage(content="Hello! I'm your assistant. How can I help you with the retail database today?")
        ]

load_dotenv()

st.set_page_config(page_title="Chat with Retail DB")

st.title("Chat with Retail DB")

with st.sidebar:
    st.header("About")
    st.markdown(
        """
        This app allows you to chat with a retail database using natural language.
        It leverages a large language model to interpret your queries and fetch relevant data from the database.
        """
    )
    st.markdown(
        """
        **Instructions:**
        - Enter your questions in the Type a message bar.
        - The app will process your query and return relevant information from the retail database.
        """
    )

for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.markdown(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Humam"):
            st.markdown(message.content)

user_query = st.chat_input("Type a message:")
if user_query is not None and user_query.strip() != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    

    with st.chat_message("Human"):
        st.markdown(user_query)

    with st.chat_message("AI"):
        response = get_response(user_query, st.session_state.db, st.session_state.chat_history)
        st.markdown(response)

    st.session_state.chat_history.append(AIMessage(content=response))
