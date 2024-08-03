import streamlit as st
from openai import OpenAI
import time
import tempfile
import os
import re

# Initialize the OpenAI client
client = OpenAI(base_url="http://localhost:8080/v1", api_key="lm-studio")

# Initialize chat history in Streamlit session state if it does not exist
if 'history' not in st.session_state:
    st.session_state.history = [
        {"role": "system", "content": "You are a travel assistant that queries Amadeus API for flight information."},
        {"role": "system", "content": "Generate code for flight searches based on user queries."},
        {"role": "user", "content": "Hello, introduce yourself to someone opening this program for the first time. Be concise."},
    ]

def generate_code(query_type, params):
    """Generate Python code for querying the Amadeus API based on the query type."""
    if query_type == 'flight_destinations':
        code = f"""
import os
from amadeus import Client as AmadeusClient

AMADEUS_CLIENT_ID = "Qk0Sgf3JUDpurllwfBbGWPf7J8keFA1m"
AMADEUS_CLIENT_SECRET = "PLud2KKjmJKZYHsd"

amadeus = AmadeusClient(
    client_id=AMADEUS_CLIENT_ID,
    client_secret=AMADEUS_CLIENT_SECRET
)

def flight_destinations_search():
    return amadeus.shopping.flight_destinations.get(origin='{params.get("originLocationCode")}')
"""
        
    elif query_type == 'flight_dates':
        code = f"""
import os
from amadeus import Client as AmadeusClient

AMADEUS_CLIENT_ID = "Qk0Sgf3JUDpurllwfBbGWPf7J8keFA1m"
AMADEUS_CLIENT_SECRET = "PLud2KKjmJKZYHsd"

amadeus = AmadeusClient(
    client_id=AMADEUS_CLIENT_ID,
    client_secret=AMADEUS_CLIENT_SECRET
)

def flight_dates_search():
    return amadeus.shopping.flight_dates.get(
        origin='{params.get("originLocationCode")}',
        destination='{params.get("destinationLocationCode")}'
    )
"""

    elif query_type == 'flight_offers_search_get':
        code = f"""
import os
from amadeus import Client as AmadeusClient

AMADEUS_CLIENT_ID = "Qk0Sgf3JUDpurllwfBbGWPf7J8keFA1m"
AMADEUS_CLIENT_SECRET = "PLud2KKjmJKZYHsd"

amadeus = AmadeusClient(
    client_id=AMADEUS_CLIENT_ID,
    client_secret=AMADEUS_CLIENT_SECRET
)

def flight_offers_search():
    return amadeus.shopping.flight_offers_search.get(
        originLocationCode='{params.get("originLocationCode")}',
        destinationLocationCode='{params.get("destinationLocationCode")}',
        departureDate='{params.get("departureDate")}',
        adults={params.get("adults")}
    )
"""

    elif query_type == 'flight_offers_search_post':
        code = f"""
import os
from amadeus import Client as AmadeusClient

AMADEUS_CLIENT_ID = "Qk0Sgf3JUDpurllwfBbGWPf7J8keFA1m"
AMADEUS_CLIENT_SECRET = "PLud2KKjmJKZYHsd"

amadeus = AmadeusClient(
    client_id=AMADEUS_CLIENT_ID,
    client_secret=AMADEUS_CLIENT_SECRET
)

def flight_offers_search_post(body):
    return amadeus.shopping.flight_offers_search.post(body)
"""

    elif query_type == 'flight_offers_pricing':
        code = f"""
import os
from amadeus import Client as AmadeusClient

AMADEUS_CLIENT_ID = "Qk0Sgf3JUDpurllwfBbGWPf7J8keFA1m"
AMADEUS_CLIENT_SECRET = "PLud2KKjmJKZYHsd"

amadeus = AmadeusClient(
    client_id=AMADEUS_CLIENT_ID,
    client_secret=AMADEUS_CLIENT_SECRET
)

def flight_offers_pricing(flights):
    return amadeus.shopping.flight_offers.pricing.post(flights[0])
"""

    elif query_type == 'flight_orders':
        code = f"""
import os
from amadeus import Client as AmadeusClient

AMADEUS_CLIENT_ID = "Qk0Sgf3JUDpurllwfBbGWPf7J8keFA1m"
AMADEUS_CLIENT_SECRET = "PLud2KKjmJKZYHsd"

amadeus = AmadeusClient(
    client_id=AMADEUS_CLIENT_ID,
    client_secret=AMADEUS_CLIENT_SECRET
)

def create_flight_order(flight, traveler):
    return amadeus.booking.flight_orders.post(flight, traveler)
"""

    else:
        raise ValueError("Unsupported query type.")

    # Print the generated code for debugging
    print("Generated Code:\n", code)
    return code

def execute_code(code, params):
    """Execute dynamically generated Python code."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as temp_file:
        temp_file.write(code.encode('utf-8'))
        temp_file_path = temp_file.name

    result = None
    try:
        exec_globals = {'params': params}
        with open(temp_file_path) as file:
            exec(file.read(), exec_globals)
        # Print the available functions and objects for debugging
        print("Available Functions and Objects:", exec_globals)
        # Find the callable function
        function_name = None
        for key, value in exec_globals.items():
            if callable(value):
                function_name = key
                break
        if function_name:
            result = exec_globals[function_name]()
        else:
            raise ValueError("No callable function found in the generated code.")
    finally:
        os.remove(temp_file_path)

    return result

def parse_user_input(user_message):
    """Parse the user message to extract parameters for the Amadeus API."""
    params = {}

    # Simple regex patterns to extract common parameters (extend as needed)
    origin_pattern = re.compile(r'\bfrom\s+(\w+)\b', re.IGNORECASE)
    destination_pattern = re.compile(r'\bto\s+(\w+)\b', re.IGNORECASE)
    date_pattern = re.compile(r'\bdate\s+(\d{4}-\d{2}-\d{2})\b', re.IGNORECASE)
    adults_pattern = re.compile(r'\badults\s+(\d+)\b', re.IGNORECASE)

    origin_match = origin_pattern.search(user_message)
    if origin_match:
        params['originLocationCode'] = origin_match.group(1).upper()

    destination_match = destination_pattern.search(user_message)
    if destination_match:
        params['destinationLocationCode'] = destination_match.group(1).upper()

    date_match = date_pattern.search(user_message)
    if date_match:
        params['departureDate'] = date_match.group(1)

    adults_match = adults_pattern.search(user_message)
    if adults_match:
        params['adults'] = int(adults_match.group(1))

    return params

def get_chat_response(user_message):
    """Get response from the chatbot and generate code if needed."""
    st.session_state.history.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF",
        messages=st.session_state.history,
        temperature=0.7,
        stream=True,
    )

    new_message = {"role": "assistant", "content": ""}
    for chunk in response:
        if chunk.choices[0].delta.content:
            new_message["content"] += chunk.choices[0].delta.content
            yield new_message["content"]
            time.sleep(0.01)

    st.session_state.history.append(new_message)

    # Parse user input to extract parameters
    params = parse_user_input(user_message)

    # Determine query type based on extracted parameters
    if 'originLocationCode' in params and 'destinationLocationCode' in params and 'departureDate' in params:
        query_type = 'flight_offers_search_get'
    elif 'originLocationCode' in params:
        query_type = 'flight_destinations'
    elif 'originLocationCode' in params and 'destinationLocationCode' in params:
        query_type = 'flight_dates'
    else:
        query_type = None

    if query_type:
        generated_code = generate_code(query_type, params)
        result = execute_code(generated_code, params)
        st.session_state.history.append(
            {"role": "assistant", "content": str(result)})

def main():
    st.title("Travel Chatbot")
    st.write("Ask me anything about travel, flight bookings, and more!")

    user_input = st.text_input("Your question:", "")

    if st.button("Send"):
        if user_input:
            # Create an empty container to update with streaming response
            response_container = st.empty()

            for response_chunk in get_chat_response(user_input):
                response_container.write(f"**Assistant:** {response_chunk}")

        else:
            st.write("Please enter a question.")

    if st.checkbox("Show chat history"):
        st.write("**Chat History:**")
        for message in st.session_state.history:
            role = "You" if message["role"] == "user" else "Assistant"
            st.write(f"**{role}:** {message['content']}")

if __name__ == "__main__":
    main()