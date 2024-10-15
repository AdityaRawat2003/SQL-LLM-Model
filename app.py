from dotenv import load_dotenv
load_dotenv()  # load all environment variables

import streamlit as st
import os
import sqlite3
import google.generativeai as genai

# Configure Google Gemini Key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load Google Gemini Model and provide queries as response
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt[0], question])
    return response.text

# Function to retrieve query from the database
def read_sql_query(sql, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    return rows

# Define your Prompt
prompt = [
    """
    You are an expert in converting English questions to SQL queries!
    The SQL database has the name STUDENT and has the following columns: NAME, CLASS, SECTION, and MARKS.
    Before generating a query, always verify if the table mentioned in the query exists in the database.
    If the table does not exist, return the message:
    Error: The table <requested_table_name> does not exist. The available table is STUDENT.
    Example 1 - How many entries of records are present?
    SQL command: SELECT COUNT(*) FROM STUDENT;
    
    Example 2 - Tell me all the students studying in Data Science class?
    SQL command: SELECT * FROM STUDENT WHERE CLASS='Data Science';
    
    Avoid using ``` and the word "sql" in the output.
    """
]

# Streamlit App UI

st.set_page_config(page_title="Gemini Text-to-SQL Converter", layout="wide")

# Sidebar for input
st.sidebar.title("Query Builder")
st.sidebar.write("Convert natural language to SQL and fetch data from the database.")
question = st.sidebar.text_input("Enter your query:", key="input")

submit = st.sidebar.button("Generate Results")

# Initialize session state for SQL query and showing the query
if 'generated_sql' not in st.session_state:
    st.session_state.generated_sql = None
if 'show_sql' not in st.session_state:
    st.session_state.show_sql = False

# Main page layout
st.title("🧠 QueryBridge")
st.subheader("Effortlessly transform your natural language questions into SQL queries to get you your desired output!")

st.write("""
This app uses Google's Gemini Model to convert natural language questions into SQL queries and fetch the results from the database.
Simply input your question in the sidebar and retrieve the data from the database.
""")

# Add some visual separation
st.markdown("---")

# If submit button is clicked, generate the SQL query
if submit:
    response = get_gemini_response(question, prompt)
    st.session_state.generated_sql = response
    
    # Reset the "show_sql" state when a new query is generated
    st.session_state.show_sql = False
    
    # Display fetched data based on the generated SQL
    st.subheader("Query Results")
    try:
        results = read_sql_query(st.session_state.generated_sql, "student.db")
        if results:
            # Create columns for a more structured layout
            cols = st.columns(len(results[0]))
            for i, row in enumerate(results):
                for j, value in enumerate(row):
                    cols[j].write(f"{value}")
        else:
            st.write("No data found for the query.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Sidebar button to show or hide the SQL query
if st.session_state.generated_sql:
    if st.sidebar.button('Show SQL'):
        st.session_state.show_sql = not st.session_state.show_sql

# Conditionally show the SQL query
if st.session_state.show_sql and st.session_state.generated_sql:
    st.subheader("Generated SQL Query")
    st.code(st.session_state.generated_sql, language='sql')