from flask import Flask, render_template, request, jsonify
import mysql.connector
import google.generativeai as genai
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os
from io import BytesIO
import base64

# Initialize Flask app
app = Flask(__name__)

# Load environment variables (e.g., API keys)
load_dotenv()

# Get API key from environment variables
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Error: GOOGLE_API_KEY not found in the environment variables.")
else:
    print(f"API Key Loaded: {api_key}")

# Configure GenAI API key
genai.configure(api_key=api_key)

# MySQL database connection details
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "admin",
    "database": "Master Data Mysql"
}

# Function to retrieve the schema of the database (for prompt generation)
def fetch_database_schema():
    schema_info = {}
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
    return schema_info

# Function to clean the generated SQL query
def clean_sql_query(sql_query):
    cleaned_query = sql_query.replace("```sql", "").replace("```", "").replace("`", "").strip()
    return cleaned_query

# Function to load Google Gemini model and provide SQL queries as response
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt[0], question])
    sql_query = response.text.strip()
    sql_query = clean_sql_query(sql_query)
    return sql_query

# Function to retrieve query from MySQL database
def read_sql_query(sql):
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

    df = pd.DataFrame(rows, columns=column_names)
    return df

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

# Function to convert plot to base64 image for frontend
def plot_to_base64(plt):
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    base64_img = base64.b64encode(img.read()).decode('utf-8')
    plt.close()
    return base64_img

# Flask route to serve the frontend
@app.route('/')
def index():
    return render_template('index.html')

# Flask route to handle query submission
# Flask route to handle query submission
@app.route('/submit_query', methods=['POST'])
def submit_query():
    question = request.form['question']
    print(f"Received question: {question}")  # Debugging step

    # Fetch the database schema
    schema_info = fetch_database_schema()
    prompt = generate_schema_prompt(schema_info)

    try:
        # Get SQL query from GeminiPro
        sql_query = get_gemini_response(question, prompt)
        print(f"Generated SQL Query: {sql_query}")  # Debugging step

        # Execute the SQL query
        df = read_sql_query(sql_query)

        # Check if visualization is requested
        if 'histogram' in question.lower():
            df.hist(bins=10)
            img = plot_to_base64(plt)
            return jsonify({'image': img, 'generatedSQL': sql_query})
        elif 'line chart' in question.lower():
            df.plot(kind='line')
            img = plot_to_base64(plt)
            return jsonify({'image': img, 'generatedSQL': sql_query})
        elif 'pie chart' in question.lower():
            df.iloc[:, 0].value_counts().plot.pie(autopct='%1.1f%%')
            img = plot_to_base64(plt)
            return jsonify({'image': img, 'generatedSQL': sql_query})
        else:
            return jsonify({'result': df.to_html(), 'generatedSQL': sql_query})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e), 'generatedSQL': sql_query})


if __name__ == '__main__':
    app.run(debug=True)
