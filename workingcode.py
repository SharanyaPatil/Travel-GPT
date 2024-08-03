import streamlit as st
import ollama
from amadeus import Client, ResponseError

# Amadeus API configuration (replace with your own credentials)
amadeus = Client(client_id='L2ZohM8MVTxjOzeKIg5DfOCHzGBtDfdW', client_secret='wC0svkP11PsRAXF8')

# Set the page configuration
st.set_page_config(page_title="Sarathi Travel Chatbot", page_icon=":airplane:", layout="wide")

st.title("Sarathi")
st.sidebar.title("Travel Chatbot")
st.sidebar.write("Ask me anything about flights, hotels, and trip planning!")

# Initialize session state variables if not already present
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hello! How can I assist you today?"}]
    st.session_state["search_params"] = {}  # Initialize search parameters
    st.session_state["full_message"] = ""
    st.session_state["history"] = []  # Initialize history list

def display_messages():
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.chat_message(msg["role"], avatar="user").write(msg["content"])
        else:
            st.chat_message(msg["role"], avatar="assistant").write(msg["content"])

def generate_response():
    response = ollama.chat(model='llama2', stream=True, messages=st.session_state.messages)
    for partial_resp in response:
        token = partial_resp["message"]["content"]
        st.session_state["full_message"] += token
        yield token

        # Process token to trigger Amadeus search
        if "find flights" in token.lower() or "search flights" in token.lower():
            if "destination" not in st.session_state["search_params"]:
                yield "Where would you like to fly to?"
                st.session_state["search_params"]["destination"] = st.text_input("Enter destination city or airport code", key="destination")
            elif "origin" not in st.session_state["search_params"]:
                yield "What is your departure city or airport code?"
                st.session_state["search_params"]["origin"] = st.text_input("Enter departure city or airport code", key="origin")
            elif "departure_date" not in st.session_state["search_params"]:
                yield "When would you like to depart? (YYYY-MM-DD format)"
                st.session_state["search_params"]["departure_date"] = st.date_input("Enter departure date", key="departure_date")
            else:
                try:
                    flights = amadeus.shopping.flight_offers_search.get(
                        originLocationCode=st.session_state["search_params"]["origin"],
                        destinationLocationCode=st.session_state["search_params"]["destination"],
                        departureDate=st.session_state["search_params"]["departure_date"].strftime('%Y-%m-%d')
                    )

                    if flights.data:
                        yield "Here are some flight options for you:"
                        for flight in flights.data:
                            flight_info = f"""
                            **Airline**: {flight['itineraries'][0]['segments'][0]['carrierCode']}
                            **Departure**: {flight['itineraries'][0]['segments'][0]['departure']['iataCode']} - {flight['itineraries'][0]['segments'][0]['departure']['at']}
                            **Arrival**: {flight['itineraries'][0]['segments'][0]['arrival']['iataCode']} - {flight['itineraries'][0]['segments'][0]['arrival']['at']}
                            **Price**: {flight['price']['total']} {flight['price']['currency']}
                            """
                            yield flight_info
                    else:
                        yield "Sorry, no flights found for your criteria. Try adjusting your search."
                        st.session_state["search_params"] = {}  # Reset search parameters for next attempt
                except ResponseError as e:
                    yield f"An error occurred while searching for flights: {e}"

# Display a loading spinner while generating a response
with st.spinner("Generating response..."):
    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user", avatar="user").write(prompt)

        st.session_state["full_message"] = ""
        response_generator = generate_response()
        response = "".join(list(response_generator))
        st.chat_message("assistant", avatar="assistant").write(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

        # Add only the prompt to history
        st.session_state["history"].append(prompt)

# Display messages in the main area
display_messages()

# Sidebar: Display previous searches or prompts
with st.sidebar.expander("Previous Searches"):
    if st.session_state["history"]:
        for entry in st.session_state["history"]:
            st.write(f"**User:** {entry}")
            st.write("---")
    else:
        st.write("No previous searches.")
    
    # Button to clear history
    if st.sidebar.button("Clear History"):
        st.session_state["history"] = []
        st.experimental_rerun()  # Refresh the page to clear history
