

# Sarathi - Travel Chatbot 🧭✈️

**Sarathi** is a travel chatbot designed to make trip planning and travel inquiries seamless and efficient. Built with **Streamlit** for an interactive user interface and **Ollama** for responsive conversational capabilities, Sarathi integrates with the **Amadeus API** to provide real-time information about flights, hotels, and travel itineraries.

---

## Features 🌟

- **Interactive User Interface**: A sleek and responsive UI powered by Streamlit.
- **Real-Time Travel Information**: Integrated with the Amadeus API to provide up-to-date details about:
  - Flight schedules and availability.
  - Hotel options and bookings.
  - Personalized trip planning and recommendations.
- **Conversational Engagement**: Uses Ollama for natural and human-like chatbot interactions.
- **Enhanced User Experience**: Seamless access to travel-related information with a focus on user efficiency and satisfaction.

---

## Tech Stack 🛠️

- **Streamlit**: For building the web application interface.
- **Ollama**: For chatbot conversational intelligence.
- **Amadeus API**: To fetch real-time travel data.
- **Python**: Core programming language for application logic and API integrations.

---

## Installation 🚀

### Prerequisites
- Python 3.8 or higher
- API keys for Amadeus
- Ollama setup

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/sarathi-travel-chatbot.git
   cd sarathi-travel-chatbot
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your API keys:
   - Add your Amadeus API key in a `.env` file:
     ```
     AMADEUS_API_KEY=your_api_key
     AMADEUS_API_SECRET=your_api_secret
     ```
   - Configure Ollama according to its documentation.

5. Run the application:
   ```bash
   streamlit run app.py
   ```

---

## Usage 💡

1. Launch the app in your browser by following the provided Streamlit URL.
2. Interact with Sarathi by asking travel-related questions, such as:
   - "Find me flights from New York to London."
   - "Suggest hotels near Eiffel Tower."
   - "Plan a trip to Tokyo for 5 days."
3. Sarathi will fetch and display the requested information using the Amadeus API.

---

## Future Enhancements 🔮

- Expand support to include car rentals and travel insurance.
- Multi-language support for global travelers.
- Advanced itinerary optimization with budget and preference filters.
- Offline access to saved itineraries.

---

## Contributing 🤝

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add feature-name"
   ```
4. Push to your branch and submit a pull request.

---

## License 📄

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments 🙏

- **Amadeus API** for providing travel-related data.
- **Streamlit** for simplifying the web app development.
- **Ollama** for conversational AI capabilities.

