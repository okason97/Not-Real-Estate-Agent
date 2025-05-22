# 🏠 Not-Real-Estate-Agent

An AI-powered assistant that helps you find and analyze real estate properties in Argentina using ZonaProp listings. It is not a real real estate agent.

## 🌟 Features

- **Natural Language Search**: Simply describe what you're looking for, and the assistant will generate the appropriate ZonaProp search URL
- **Automated Scraping**: Collects property listings from ZonaProp based on your search criteria
- **Intelligent Analysis**: Analyzes property data to provide insights on pricing, location, features, and value
- **Personalized Recommendations**: Suggests 3-5 properties that best match your requirements with pros and cons for each

## 🛠️ Technical Architecture

This application uses a state graph architecture with the following components:

1. **Query Data Agent**: Converts natural language queries into structured data for targeted web search
2. **Scraper**: Collects property data from ZonaProp using pagination
3. **Analysis Agent**: Evaluates properties based on user criteria
4. **Recommendation Agent**: Provides personalized property recommendations

## 📋 Prerequisites

- Python 3.13+
- Required Python packages (install via `pip install -r requirements.txt` or `uv add -r requirements.txt`)
- Docker (Optional, for web gui)
- AWS Serverless Application Model Command Line Interface (AWS SAM CLI) (Optional, for web gui)
- Ollama gemma3:12b and apropiate hardware (Optional)

## 🚀 Getting Started

1. Clone this repository:
   ```bash
   git clone https://github.com/okason97/Not-Real-Estate-Agent.git
   cd zonaprop-real-estate-agent
   ```

2. Install dependencies:
   ```bash
   uv add -r requirements.txt
   ```

### 🏃 Running

1. Set up environment variables (If you want to use an API):
   ```bash
   # Create .env file
   touch .env
   # Add necessary environment variables
   ```

2. Or install and run Ollama with the gemma3:12b model locally:
   ```bash
   # Install Ollama: https://ollama.com/
   # Then pull the model
   ollama pull gemma3:12b
   ollama run gemma3:12b
   ```

3. Run the notebook:
   ```bash
   code agent.ipynb
   ```

### 💻 Using the app

1. Build the Docker image and SAM (Serverless Application Model):
   ```bash
   docker build --no-cache --provenance=false --platform linux/amd64 -t nrea .
   sam build --no-cached
   ```

2. Open Ollama server (Optional):
   ```bash
   ollama serve
   ```

2. Start a local API Gateway at http://127.0.0.1:3000/ using SAM (Serverless Application Model):
   ```bash
   sam local start-api
   ```

2. Run the web GUI:
   ```bash
   streamlit run app.py
   ```

## 💬 Example Usage

```
Enter a message: I'm looking for a 2-bedroom apartment to rent in La Plata, with a garage, preferably less than 10 years old.

[The system generates a ZonaProp URL, scrapes listings, analyzes them, and provides recommendations]
```

## 📁 Project Structure

- `agent.ipynb`: Notebook to try the agents
- `frontend.py`: Serves the interactive frontend
- `app/`: Directory containing the agents and the API code
  - `main.py`: Contains the FastAPI behaviour 
  - `src/`: Directory containing the source code
    - `scraper.py`: Contains the `Scrapper` classes for web scraping
    - `graph.py`: Contains the graph building logic
    - `models.py`: Loads the LLM model
    - `nodes.py`: Contains the agentic nodes of the graph
    - `state.py`: Contains the internal state of the graph

## 🔧 Customization

You can customize the application by:

1. Modifying the prompt templates in each agent
2. Extending the scraper to collect information from other sites by subclassing `Scrapper`
3. Extending the scraper to collect additional property details
4. Adjusting the analysis criteria based on your preferences

## 📊 Future Improvements

- [ ] Add a plan-and-execute architecture for the agents 
- [ ] Implement historical price tracking and other useful information for the analysis agent
- [ ] Add visualization tools for property comparisons
- [ ] Support for additional property listing websites
- [ ] Add an image processing gent to include visual information

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for educational purposes only. Please respect ZonaProp's terms of service and implement appropriate rate limiting in production environments.
