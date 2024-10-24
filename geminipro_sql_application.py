from dotenv import load_dotenv
import os
import mysql.connector
import google.generativeai as genai
import pandas as pd
import matplotlib.pyplot as plt

# Load environment variables (e.g., API keys)
load_dotenv()

# Ensure API key is loaded correctly
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Error: GOOGLE_API_KEY not found in the environment variables. Please check your .env file.")
else:
    print(f"API Key Loaded: {api_key}")  # You can remove this after confirming it's working

# Configure GenAI API key from environment variables
genai.configure(api_key=api_key)

# Function to retrieve the schema of the database
def fetch_database_schema(db_config):
    schema_info = {}
    try:
        conn = mysql.connector.connect(
            host=db_config["host"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"]
        )
        cur = conn.cursor()

        # Fetch all table names
        cur.execute("SHOW TABLES")
        tables = cur.fetchall()

        # For each table, fetch the column names and types
        for table in tables:
            table_name = table[0]
            cur.execute(f"DESCRIBE {table_name}")
            columns = cur.fetchall()
            schema_info[table_name] = [{"Field": col[0], "Type": col[1]} for col in columns]

        conn.close()
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
    return schema_info

# Function to clean the generated SQL query
def clean_sql_query(sql_query):
    # Remove extra backticks, and handle incorrect syntax
    cleaned_query = sql_query.replace("```sql", "").replace("```", "").replace("`", "").strip()
    return cleaned_query

# Function to load Google Gemini model and provide SQL queries as response
def get_gemini_response(question, prompt):
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content([prompt[0], question])
        sql_query = response.text.strip()

        # Clean the SQL query
        sql_query = clean_sql_query(sql_query)

        # Debugging: Print the generated SQL query
        print(f"Generated SQL Query: {sql_query}")

        return sql_query
    except Exception as e:
        print(f"Error in generating SQL: {e}")
        return None

# Function to retrieve query from the MySQL database
def read_sql_query(sql, db_config):
    try:
        conn = mysql.connector.connect(
            host=db_config["host"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"]
        )
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        column_names = [i[0] for i in cur.description]
        conn.close()

        # Convert the result into a pandas DataFrame
        df = pd.DataFrame(rows, columns=column_names)
        return df
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
        return None

# MySQL database connection details
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "admin",
    "database": "Master Data Mysql"
}

# Function to generate a schema-based prompt
def generate_schema_prompt(schema_info):
    schema_description = "The database schema is as follows:\n"
    for table, columns in schema_info.items():
        schema_description += f"Table {table} has the following columns:\n"
        for col in columns:
            schema_description += f"- {col['Field']} ({col['Type']})\n"
    
    prompt = [
        f"""
        You are an expert in converting English questions to SQL queries!
        The SQL database structure is as follows. Use the schema information to generate accurate SQL queries.

        {schema_description}

        When asked a question, return only the SQL query without explanations. Ensure the SQL query is formatted for MySQL.
        """
    ]
    
    return prompt

# Function to visualize the data using different types of charts
def visualize_data(df, chart_type):
    if chart_type == 'histogram':
        df.hist(bins=10)
        plt.show()
    elif chart_type == 'line chart':
        df.plot(kind='line')
        plt.show()
    elif chart_type == 'pie chart':
        df.iloc[:, 0].value_counts().plot.pie(autopct='%1.1f%%')
        plt.show()
    else:
        print("Visualization type not supported")

# Custom logic for frequently asked questions like column count
def handle_common_questions(question):
    if "how many columns" in question.lower():
        return "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'excel_data';"
    return None

# Main console loop for asking questions
def console():
    print("Fetching database schema...")
    schema_info = fetch_database_schema(db_config)
    if not schema_info:
        print("Error fetching database schema.")
        return
    prompt = generate_schema_prompt(schema_info)
    print("Database schema loaded.")

    print("Welcome to the Console-based Gemini SQL Application.")
    
    while True:
        question = input("Please enter your question (or type 'exit' to quit): ")
        
        if question.lower() == 'exit':
            print("Goodbye!")
            break
        
        # Detect if the user is asking for a visualization
        chart_type = None
        if "histogram" in question.lower():
            chart_type = "histogram"
        elif "line chart" in question.lower():
            chart_type = "line chart"
        elif "pie chart" in question.lower():
            chart_type = "pie chart"

        try:
            # Handle common questions manually
            sql_query = handle_common_questions(question)
            
            if not sql_query:
                # Get SQL query from GeminiPro API
                sql_query = get_gemini_response(question, prompt)
                if not sql_query:
                    print("Error: Could not generate a valid SQL query.")
                    continue
            
            print(f"Generated SQL Query: {sql_query}")
            
            # Execute the SQL query and get the results from MySQL
            df = read_sql_query(sql_query, db_config)
            if df is None or df.empty:
                print("No results returned from the query.")
                continue
            
            if chart_type:
                visualize_data(df, chart_type)
            else:
                print("Results:")
                print(df)
        
        except mysql.connector.Error as err:
            print(f"MySQL Error: {err}")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    console()
