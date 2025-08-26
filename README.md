# Retail-Project
Natural language to SQL Query for Retail Database

This project creates a chatbot that understands everyday language and turns it into SQL queries using GPT-4o mini! This guide shows you how to build a chatbot that can understand questions asked in normal language, create the right SQL commands, and get answers from a SQL database. It’s easy to use and works through a simple interface made with Streamlit.

**Features**:
---

- Understands and answers questions in natural language using GPT-4o mini.

- Automatically creates SQL queries from what the user asks.

- Connects to a SQL database to get real answers.

- Has a simple and friendly user interface built with Streamlit.

- Made completely in Python, using modern programming techniques.

**How the Chatbot Works**:
---
The chatbot listens to what the user asks in normal language, uses GPT-4 to turn that into a SQL command, runs the command on a database, and then shows the results in a clear, easy-to-understand way. All this happens smoothly inside the Streamlit app.

**Installation**:
---
Ensure to have python in your local machine and then clone this repo:
```
git clone [repository-link]
cd [repository-directory]
```
Install the required packages:
```
pip install -r requirements.txt
```
Create your own .env file with any model you want to work
```
YOURMODEL_API_KEY=[your-model-api-key]
```
**Usage**
---
To launch streamlit app
```
streamlit run app.py
```

