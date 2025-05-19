from app.src.scrapper import ZonaPropScrapper
import json
from app.src.state import AgentState, MessageURL, PropertySearchParams
from app.src.models import init_llm

def scrape_node(state: AgentState):
    sc = ZonaPropScrapper()

    if 'url' in state:
        url = str(state["url"])
    else:
        query_data = state["query_data"]
        url = sc.generate_url(query_data)
    urls = sc.generate_pagination_urls(url, 1)

    htmls = sc.selenium_scrape(urls)
    properties = sc.parse_property_listings(htmls)
    return {"properties": properties}

class LLM():
    def __init__(self, model='ollama', temperature=0.0):
        self.model = init_llm(model=model, temperature=temperature)

    def url_agent(self, state: AgentState):
        last_message = state["query"][-1]
        url_llm = self.model.with_structured_output(MessageURL)

        result = url_llm.invoke([
            {
                "role": "system",
                "content": f"""
                    You are an assistant that generates ZonaProp property listing URLs based on the user's message.

                    ## ZonaProp URL Format
                    Base structure:
                    https://www.zonaprop.com.ar/[property-type]-[operation]-[location]-[additional-filters].html

                    ### Required Components (must always be included):
                    1. **Property Type**
                    - departamentos (apartments)
                    - casas (houses)
                    - ph (Horizontal Property)
                    - cocheras (parking)
                    - terrenos (land)
                    - oficinas (offices)
                    - locales (commercial)
                    - Combined types: e.g., casas-departamentos-ph

                    2. **Operation**
                    - venta (sale)
                    - alquiler (rent)
                    - alquiler-temporal (temporary rental)

                    3. **Location**
                    - Examples: capital-federal, palermo, la-plata, rosario
                    - Can include neighborhoods, cities, or provinces

                    ---

                    ### Optional Filters (include only if user provides relevant info):
                    4. **Rooms (ambientes)**
                    - e.g., 1-ambiente, 2-ambientes, mas-de-3-ambientes, desde-2-hasta-3-ambientes

                    5. **Bedrooms (habitaciones)**
                    - e.g., 1-habitacion, hasta-3-habitaciones, desde-2-hasta-3-habitaciones

                    6. **Bathrooms (baños)**
                    - e.g., 2-banos, mas-de-1-bano, desde-1-hasta-2-banos

                    7. **Garages**
                    - e.g., 1-garage, sin-garages, mas-de-1-garage, desde-1-hasta-2-garages

                    8. **Price**
                    - e.g., menos-200000-dolares, mas-de-100000-pesos, desde-100000-hasta-300000-dolares

                    9. **Age**
                    - e.g., a-estrenar, hasta-10-anos, mas-de-20-anos

                    10. **Sorting**
                    - orden-precio-ascendente
                    - orden-publicacion-descendente

                    11. **Publication Date**
                    - publicado-hoy
                    - publicado-hace-menos-de-1-semana
                    - publicado-hace-menos-de-1-mes

                    ---

                    ### Rules & Behavior
                    - All terms in the URL must be lowercase and hyphen-separated.
                    - If key info is missing, **infer as a real estate agent would** or omit the filter.
                    - **Always include** property type, operation, and location.
                    - **Only output the URL.**
                """
            },
            {
                "role": "user",
                "content": last_message.content
            }
        ])
        return {"url": result.url}

    def query_data_agent(self, state: AgentState):
        last_message = state["query"][-1]
        query_data_llm = self.model.with_structured_output(PropertySearchParams)

        result = query_data_llm.invoke([
            {
                "role": "system",
                "content": """
                    You are a real estate agent assistant that converts user queries into structured property search requirements. Your only response should be a valid JSON object matching the format below, with no additional text or explanation:

                    {
                        "required": {
                            "propertyType": "departamentos|casas|ph|cocheras|terrenos|oficinas|locales|casas-departamentos-ph",
                            "operation": "venta|alquiler|alquiler-temporal",
                            "location": "capital-federal|palermo|la-plata|rosario|[other-valid-location]"
                        },
                        "optional": {
                            "rooms": "1-ambiente|2-ambientes|mas-de-3-ambientes|desde-2-hasta-3-ambientes",
                            "bedrooms": "1-habitacion|hasta-3-habitaciones|desde-2-hasta-3-habitaciones",
                            "bathrooms": "2-banos|mas-de-1-bano|desde-1-hasta-2-banos",
                            "garages": "1-garage|sin-garages|mas-de-1-garage|desde-1-hasta-2-garages",
                            "price": "menos-200000-dolares|mas-de-100000-pesos|desde-100000-hasta-300000-dolares",
                            "age": "a-estrenar|hasta-10-anos|mas-de-20-anos",
                            "sorting": "orden-precio-ascendente|orden-publicacion-descendente",
                            "publicationDate": "publicado-hoy|publicado-hace-menos-de-1-semana|publicado-hace-menos-de-1-mes"
                        }
                    }

                    Instructions:
                    1. Analyze the user query to identify required and optional property criteria
                    2. Choose ONLY from the exact option values provided above
                    3. For each category, select the SINGLE most appropriate option based on the query
                    4. If a category is not mentioned or implied in the query, do not include it in your response
                    5. For required fields:
                    - Always include propertyType (default to "departamentos" if not specified)
                    - Always include operation (default to "alquiler" if not specified)
                    - Always include location (no default - must be derived from query)
                    6. For optional fields, only include parameters clearly stated or strongly implied in the query
                    7. If a query is ambiguous, make the most reasonable inference based on common rental patterns
                    8. Return only the JSON object with no additional text, explanation, or commentary

                    Example queries and expected responses:

                    Query: "quiero una habitacion en la plata de un departamento"
                    Response:
                    {
                        "required": {
                            "propertyType": "departamentos",
                            "operation": "alquiler",
                            "location": "la-plata"
                        },
                        "optional": {
                            "bedrooms": "1-habitacion"
                        }
                    }

                    Query: "busco casa de 3 ambientes en venta en rosario con 2 baños y garage"
                    Response:
                    {
                        "required": {
                            "propertyType": "casas",
                            "operation": "venta",
                            "location": "rosario"
                        },
                        "optional": {
                            "rooms": "3-ambientes",
                            "bathrooms": "2-banos",
                            "garages": "1-garage"
                        }
                    }
                """
            },
            {
                "role": "user",
                "content": last_message.content
            }
        ])
        
        return {"query_data": result}

    def analize_agent(self, state: AgentState):
        last_message = state["query"][-1]

        result = self.model.invoke([
            {
                "role": "system",
                "content": f"""
                    You are a real estate analysis assistant specializing in properties located in La Plata, Argentina.

                    PROPERTY LISTINGS:
                    {json.dumps(state["properties"], indent=2, ensure_ascii=False)}

                    Please analyze these properties based on the user's query. Focus on the following points:

                    - Which properties best match the user's criteria
                    - Price comparison and value assessment
                    - Pros and cons of the locations
                    - Notable features or amenities
                    - Any other relevant observations

                    Present your analysis in a clear, structured, and easy-to-understand format.
                """
            },
            {
                "role": "user",
                "content": last_message.content
            }
        ])

        return {"analysis": [result]}

    def recomend_agent(self, state: AgentState):
        last_message = state["query"][-1]

        result = self.model.invoke([
            {
                "role": "system",
                "content": f"""
                    Based on the following analysis of real estate listings in La Plata and the user query:
                    
                    PROPERTY LISTINGS:
                    {json.dumps(state["properties"], indent=2, ensure_ascii=False)}

                    ANALYSIS:
                    {state["analysis"][0].content}

                    Generate between 3 and 5 specific recommendations for the user. For each recommendation, provide:

                    -The URL of the property.

                    -A brief justification (1–2 sentences).

                    -Key advantages of this property.

                    -Key disadvantages of this property.
                """
            },
            {
                "role": "user",
                "content": last_message.content
            }
        ])
        
        return {"query": [result]}
