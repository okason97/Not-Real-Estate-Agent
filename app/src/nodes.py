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

    htmls = sc.curl_scrape(urls)
    properties = sc.parse_property_listings(htmls)
    return {"properties": properties}

class LLM():
    def __init__(self, model='ollama', api_key=None, temperature=0.0):
        self.model = init_llm(model=model, api_key=api_key, temperature=temperature)

    def url_agent(self, state: AgentState):
        last_message = state["query"][-1]
        url_llm = self.model.with_structured_output(MessageURL)


        print("Calling URL agent")
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
        print("Received URL agent response")
        return {"url": result.url}

    def query_data_agent(self, state: AgentState):
        last_message = state["query"][-1]
        query_data_llm = self.model.with_structured_output(PropertySearchParams)

        print("Calling query data agent")
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
                            "rooms": "1-ambiente|2-ambientes|mas-de-x-ambientes|desde-x-hasta-y-ambientes",
                            "bedrooms": "1-habitacion|hasta-x-habitaciones|desde-x-hasta-y-habitaciones",
                            "bathrooms": "2-baños|mas-de-x-baños|desde-x-hasta-y-baños",
                            "garages": "x-garage|sin-garages|mas-de-x-garage|desde-x-hasta-y-garages",
                            "price": "menos-x-dolares|mas-de-x-pesos|desde-x-hasta-x-dolares",
                            "age": "a-estrenar|hasta-x-anos|mas-de-x-anos",
                            "sorting": "orden-precio-ascendente|orden-publicacion-descendente",
                            "publicationDate": "publicado-hoy|publicado-hace-menos-de-1-semana|publicado-hace-menos-de-1-mes"
                        }
                    }

                    Instructions:
                    1. Analyze the user query to identify required and optional property criteria
                    2. Choose ONLY from the exact option values provided above, replace x and y with numbers apropiate for the query
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
        print("Received query data agent response")

        return {"query_data": result}

    def analize_agent(self, state: AgentState):
        last_message = state["query"][-1]

        print("Calling analysis agent")
        result = self.model.invoke([
            {
                "role": "system",
                "content": f"""
                    You are a real estate analysis assistant specializing in properties located in La Plata, Argentina.

                    ---

                    TASK:
                    Generate a machine-readable analysis with no aditional text or explanation

                    ---
                    
                    OUTPUT FORMAT:

                    1. MARKET_OVERVIEW:
                    • Price_range: [minimum]-[maximum] ARS/USD
                    • Average_price_per_sqm: [value] ARS/USD
                    • Market_context: [brief market description]

                    2. PROPERTY_MATCHES:
                    • For each relevant property:
                        - property_id: [ID from listings]
                        - property_url: [Direct url to the listing]
                        - match_reasons: [comma-separated list of key matching criteria]
                        - price_value_assessment: [below_market/at_market/premium]
                        - location_advantages: [comma-separated list of location advantages, like proximity to amenities, safety, and transportation)]
                        - location_concerns: [comma-separated list]
                        - location_quality: [numerical 1-10]
                        - standout_features: [comma-separated list]
                        - concerns: [comma-separated list]
                        - match_score: [numerical 1-10]

                    3. COMPARATIVE_INSIGHTS:
                    • best_value: [property_id]
                    • best_location: [property_id]
                    • best_condition: [property_id]
                    • best_investment: [property_id]
                    • unique_opportunity: [property_id, reason]

                    ---

                    REQUIREMENTS:

                    - Use consistent key names and data types
                    - Ensure all property references use IDs from the original listings
                    - Maintain a structured, machine-parsable format
                    - Avoid marketing language or subjective claims
                    - Include only factual data derived from the listings
                    - Omit subjective claims, recommendations, questions or commentary
                    - Do not introduce properties not included in the provided listings
                    - Do not ask follow-up questions or add closing statements
                    - Present facts without recommendations for further action
                    - URLs are direct links to property listings
                    - Price assessments use only: below_market/at_market/premium
                    - Location advantages/concerns are factual, comma-separated
                """
            },
            {
                "role": "user",
                "content": f"""
                    PROPERTY LISTINGS:
                    {json.dumps(state["properties"], indent=2, ensure_ascii=False)}
                    QUERY:
                    {last_message.content}
                """
            }
        ])

        print("Received analysis agent response")
        return {"analysis": [result]}

    def recomend_agent(self, state: AgentState):
        last_message = state["query"][-1]

        print("Calling recommendation agent")
        result = self.model.invoke([
            {
                "role": "system",
                "content": f"""
                You are a real estate analyst providing personalized property recommendations.

                ---

                
                TASK: Generate 3-5 property recommendations from the provided listings that best match the user's query.

                ---

                OUTPUT FORMAT for each recommendation:

                ### Property Name: [Descriptive name of the property, e.g., "Modern 3BR Condo in Mission Bay"]
                [LEAVE BLANK LINE HERE]

                **URL:** [Complete URL from listing]
                [LEAVE BLANK LINE HERE]

                **Match Score:** [numerical 1-10] [Brief explanation of why this property fits the user's criteria]
                [LEAVE BLANK LINE HERE]

                **Location Score:** [numerical 1-10] [Brief explanation of the location's advantages and disadvantages]
                [LEAVE BLANK LINE HERE]  

                **Price Score:** [numerical 1-10] [Brief explanation of the price in relation to the market]
                [LEAVE BLANK LINE HERE]

                #### Key Features:
                [LEAVE BLANK LINE HERE] 

                 • [Specific detail 1 - include numbers/measurements when available]
                [LEAVE BLANK LINE HERE]

                 • [Specific detail 2 - highlight unique amenities or location benefits]  
                [LEAVE BLANK LINE HERE]

                 • [Specific detail 3 - mention standout characteristics]
                [LEAVE BLANK LINE HERE]

                #### Considerations:
                [LEAVE BLANK LINE HERE]

                 • [Potential limitation 1]
                [LEAVE BLANK LINE HERE]

                 • [Potential limitation 2]
                [LEAVE BLANK LINE HERE]

                ---

                REQUIREMENTS:
                - Use only properties from the provided PROPERTY LISTINGS
                - Base recommendations solely on the ANALYSIS and user QUERY
                - Include complete, accurate URLs
                - Present factual information without marketing language
                - No follow-up questions or closing statements
                - No disclaimers or suggestions for additional help

                OUTPUT DESTINATION: This will be displayed in markdown format where spacing is critical for readability.
                Maintain all line breaks and spacing exactly as specified.

                ---

                EXAMPLE OUTPUT (for reference):

                ### Property Name: Modern 3BR Condo in Mission Bay
                
                **URL:** https://example.com/listing/12345
                
                **Match Score:** 8/10 Strong fit for user’s desire for a modern 3-bedroom near tech hubs, with walkable access to parks and transit.
                
                **Location Score:** 8/10 Located in a vibrant area with easy access to public transport, restaurants, and parks, but can be noisy during events.
                
                **Price Score:** 7/10 Priced slightly above average for the area, but offers modern amenities and a desirable location.

                #### Key Features:
               
                 • 1,450 sq ft with open-concept kitchen and floor-to-ceiling windows
               
                 • Rooftop pool and gym access included in HOA
               
                 • 5-minute walk to Caltrain and Oracle Park

                
                #### Considerations:
              
                  • HOA fee is relatively high at $820/month
              
                  • Limited street parking in surrounding area
                
                """
            },
            {
                "role": "user",
                "content": f"""
                    ANALYSIS:
                    {state["analysis"][0].content}

                    PROPERTY LISTINGS:
                    {json.dumps(state["properties"], indent=2, ensure_ascii=False)}

                    QUERY:
                    {last_message.content}
                """
            }
        ])
        
        print("Received recommendation agent response")
        return {"query": [result]}
