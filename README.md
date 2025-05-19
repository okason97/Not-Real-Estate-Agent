# 🏠 Not-Real-Estate-Agent

An AI-powered assistant that helps you find and analyze real estate properties in Argentina using ZonaProp listings. It is not a real real estate agent.

## 🌟 Features

- **Natural Language Search**: Simply describe what you're looking for, and the assistant will generate the appropriate ZonaProp search URL
- **Automated Scraping**: Collects property listings from ZonaProp based on your search criteria
- **Intelligent Analysis**: Analyzes property data to provide insights on pricing, location, features, and value
- **Personalized Recommendations**: Suggests 3-5 properties that best match your requirements with pros and cons for each

## 🛠️ Technical Architecture

This application uses a state graph architecture with the following components:

1. **URL Agent**: Converts natural language queries into structured ZonaProp URLs
2. **Scraper**: Collects property data from ZonaProp using pagination
3. **Analysis Agent**: Evaluates properties based on user criteria
4. **Recommendation Agent**: Provides personalized property recommendations

## 📋 Prerequisites

- Python 3.13+
- Required Python packages (install via `pip install -r requirements.txt`)
- Ollama gemma3:12b and apropiate hardware


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

3. Set up environment variables (Not used now, necessary if more models are added):
   ```bash
   # Create .env file
   touch .env
   # Add necessary environment variables
   ```

4. Ensure you have Ollama installed and running with the gemma3:12b model:
   ```bash
   # Install Ollama: https://ollama.com/
   # Then pull the model
   ollama pull gemma3:12b
   ```

5. Run the application:
   ```bash
   python main.py
   ```

5. Build the Docker image:
   ```bash
   docker build --provenance=false --platform linux/amd64 -t nrea .
   ```

5. Start a local API Gateway at http://127.0.0.1:3000/ using SAM (Serverless Application Model):
   ```bash
   sam local start-api
   ```



## 💬 Example Usage

```
Enter a message: I'm looking for a 2-bedroom apartment to rent in La Plata, with a garage, preferably less than 10 years old.

[The system generates a ZonaProp URL, scrapes listings, analyzes them, and provides recommendations]
```

## 📁 Project Structure

- `main.py`: Entry point of the application
- `scraper.py`: Contains the `ZonaPropScrapper` class for web scraping
- `models.py`: Pydantic models for data validation
- `agents/`: Directory containing specialized agents
  - `url_agent.py`: Converts natural language to ZonaProp URLs
  - `analysis_agent.py`: Analyzes property data
  - `recommendation_agent.py`: Generates property recommendations

## 🔧 Customization

You can customize the application by:

1. Modifying the prompt templates in each agent
2. Extending the scraper to collect information from other sites
3. Extending the scraper to collect additional property details
4. Adjusting the analysis criteria based on your preferences

## 📊 Future Improvements

- [ ] Implement historical price tracking and other useful information for the analysis agent
- [ ] Create a web interface for easier interaction
- [ ] Add visualization tools for property comparisons
- [ ] Support for additional property listing websites
- [ ] Add an image processing gent to include visual information

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for educational purposes only. Please respect ZonaProp's terms of service and implement appropriate rate limiting in production environments.