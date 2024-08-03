import streamlit as st
from transformers import pipeline
from amadeus import Client, ResponseError
from datetime import datetime
import re

# Initialize APIs
amadeus = Client(client_id='L2ZohM8MVTxjOzeKIg5DfOCHzGBtDfdW', client_secret='wC0svkP11PsRAXF8')

chatbot = pipeline("text-generation", model="gpt2")

# Streamlit UI setup
st.set_page_config(page_title="Travel Chatbot", page_icon=":airplane:", layout="wide")

# Sidebar
st.sidebar.title("Travel Chatbot")
st.sidebar.write("Ask me anything about flights, hotels, and trip planning!")

# Main interface
st.title("Welcome to the Travel Chatbot")
st.write("Powered by Hugging Face and Amadeus")

# Chat history
if 'messages' not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Helper function to extract flight details
def extract_flight_details(user_input):
    # Regex patterns for airport codes (3-letter IATA codes)
    pattern = re.compile(r'\b([A-Z]{3})\b')
    codes = pattern.findall(user_input)
    return codes[:2] if len(codes) >= 2 else (None, None)

# Helper function to extract city and date details for hotels
def extract_hotel_details(user_input):
    # Regex pattern for date in YYYY-MM-DD format
    date_pattern = re.compile(r'(\d{4}-\d{2}-\d{2})')
    date_match = date_pattern.search(user_input)
    date = date_match.group(0) if date_match else datetime.today().strftime('%Y-%m-%d')
    
    # Extract city name (assuming it's a single word or two words)
    city_pattern = re.compile(r'(?i)hotel\s+in\s+([a-zA-Z\s]+)')
    city_match = city_pattern.search(user_input)
    city = city_match.group(1).strip() if city_match else None
    
    return city, date

# Input box
if user_input := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get response from Hugging Face
    response = chatbot(user_input, max_length=100, num_return_sequences=1)
    reply = response[0]['generated_text']
    
    # Add Hugging Face response to chat history
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

    # Extract flight details if query contains "flight"
    if "flight" in user_input.lower():
        origin, destination = extract_flight_details(user_input)
        if origin and destination:
            try:
                today = datetime.today().strftime('%Y-%m-%d')
                flights = amadeus.shopping.flight_offers_search.get(
                    originLocationCode=origin,
                    destinationLocationCode=destination,
                    departureDate=today,
                    adults=1
                ).data

                if flights:
                    flight_info = f"Found {len(flights)} flights from {origin} to {destination} for today:\n\n"
                    for flight in flights:
                        flight_details = flight['itineraries'][0]['segments'][0]
                        departure = flight_details['departure']
                        arrival = flight_details['arrival']
                        carrier_code = flight_details['carrierCode']
                        flight_number = flight_details['number']
                        flight_info += f"Flight {carrier_code} {flight_number}: {departure['iataCode']} at {departure['at']} -> {arrival['iataCode']} at {arrival['at']}\n"
                else:
                    flight_info = f"No flights found from {origin} to {destination} for today."

                st.session_state.messages.append({"role": "assistant", "content": flight_info})
                with st.chat_message("assistant"):
                    st.markdown(flight_info)
            except ResponseError as error:
                st.error(error)
        else:
            st.error("Please provide valid IATA codes for both origin and destination.")

    # Extract hotel details if query contains "hotel"
    elif "hotel" in user_input.lower():
        city, check_in_date = extract_hotel_details(user_input)
        if city:
            try:
                check_out_date = (datetime.strptime(check_in_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
                hotels = amadeus.shopping.hotel_offers.get(
                    cityCode=city,
                    checkInDate=check_in_date,
                    checkOutDate=check_out_date,
                    roomQuantity=1,
                    adults=1
                ).data

                if hotels:
                    hotel_info = f"Found {len(hotels)} hotels in {city}:\n\n"
                    for hotel in hotels:
                        hotel_name = hotel['hotel']['name']
                        hotel_address = hotel['hotel']['address']['lines'][0]
                        hotel_info += f"{hotel_name}: {hotel_address}\n"
                else:
                    hotel_info = f"No hotels found in {city}."

                st.session_state.messages.append({"role": "assistant", "content": hotel_info})
                with st.chat_message("assistant"):
                    st.markdown(hotel_info)
            except ResponseError as error:
                st.error(error)
        else:
            st.error("Please provide a valid city name for the hotel search.")