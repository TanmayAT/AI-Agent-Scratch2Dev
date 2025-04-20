import sqlite3
import pandas as pd
import google.generativeai as genai
import re 
import os


hotel_data_path = r"hotel_bookings.csv"  

hotel_booking_df = pd.read_csv(hotel_data_path)

conn = sqlite3.connect("hotel_bookings.db")
hotel_booking_df.to_sql("bookings", conn, if_exists="replace", index=False)

print("Database and table created successfully!")

api_key = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=api_key)

# Define DB Schema for LLM
DB_SCHEMA = """
Table Name: bookings

Columns:
- hotel (TEXT) → Type of hotel (Resort, City)
- is_canceled (INTEGER) → 1 if canceled, 0 if not
- lead_time (INTEGER) → Number of days between booking and check-in
- arrival_date_year (INTEGER) → Year of arrival
- arrival_date_month (TEXT) → Month of arrival (January, February, etc.)
- arrival_date_week_number (INTEGER) → Week number of the year
- arrival_date_day_of_month (INTEGER) → Day of the month
- stays_in_weekend_nights (INTEGER) → Nights stayed on weekends
- stays_in_week_nights (INTEGER) → Nights stayed during weekdays
- adults (INTEGER) → Number of adults in the booking
- children (INTEGER) → Number of children in the booking
- babies (INTEGER) → Number of babies in the booking
- meal (TEXT) → Meal package selected
- country (TEXT) → Country of origin of the booking
- market_segment (TEXT) → Market segment (Direct, Online Travel Agent, etc.)
- distribution_channel (TEXT) → Booking channel (Corporate, Direct, etc.)
- is_repeated_guest (INTEGER) → 1 if a repeated guest, 0 otherwise
- previous_cancellations (INTEGER) → Number of times this guest has canceled before
- previous_bookings_not_canceled (INTEGER) → Number of successful bookings by guest
- reserved_room_type (TEXT) → Room type reserved
- assigned_room_type (TEXT) → Room type assigned
- booking_changes (INTEGER) → Number of changes made to the booking
- deposit_type (TEXT) → Type of deposit paid
- agent (INTEGER) → ID of booking agent
- company (INTEGER) → ID of booking company
- days_in_waiting_list (INTEGER) → Number of days in waiting list
- customer_type (TEXT) → Type of customer (Transient, Group, etc.)
- adr (FLOAT) → Average Daily Rate
- required_car_parking_spaces (INTEGER) → Number of parking spaces required
- total_of_special_requests (INTEGER) → Number of special requests
- reservation_status (TEXT) → Status of reservation (Check-Out, Canceled, No-Show)
- reservation_status_date (DATE) → Date when reservation status was updated
"""

def generate_sql_query(user_query):
    """Use LLM to generate SQL based on schema and user query."""
    prompt = f"""
    You are an SQL expert. Based on the given schema, generate an optimized SQL query for the following user query.

    Schema:
    {DB_SCHEMA}

    User Query: "{user_query}"

    Ensure the query is syntactically correct for SQLite. Do not include explanations, just return the SQL query only.
    """

    
    model = genai.GenerativeModel("gemini-2.0-flash")  # Load Gemini Model
    response = model.generate_content(prompt)

    sql_query =response.text.strip()
    sql_query = re.sub(r"```[\s\S]*?\n|```", "", sql_query).strip()
    
    
    return sql_query

def execute_sql_query(query):
    """Runs the generated SQL query and returns results."""
    try:
        conn = sqlite3.connect("hotel_bookings.db")
        cursor = conn.cursor()

        print(f"Executing SQL Query: {query}")  # Debugging step
        cursor.execute(query)
        results = cursor.fetchall()

        conn.close()
        return results
    except Exception as e:
        print(f"SQL Execution Error: {e}")  # Print error message
        return f"Error: {str(e)}"

# Test the function



def explain_results(user_query, results):
    """Use LLM to explain retrieved data in natural language."""
    prompt = f"""
    The user asked: "{user_query}"

    The database returned the following records:
    {results[:10]}  # Sending first 10 results for efficiency

    Provide a structured, natural language response summarizing the key insights.
    """

    # Correct Gemini API Call
    model = genai.GenerativeModel("gemini-2.0-flash")  # Load Gemini model
    response = model.generate_content(prompt)  # Generate response

    return response.text.strip()


