from typing import Annotated, Optional, Any, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field, Json
from pydantic.networks import AnyUrl
from langgraph.graph.message import add_messages

class MessageURL(BaseModel):
    url: AnyUrl = Field(description="A functional ZonaProp URL based on the user's real estate query")

class RequiredFields(BaseModel):
    propertyType: Literal[
        "departamentos", "casas", "ph", "cocheras", "terrenos", 
        "oficinas", "locales", "casas-departamentos-ph"
    ]
    operation: Literal["venta", "alquiler"]
    location: str = Field(
        description="Valid location slug like 'capital-federal', 'palermo', 'la-plata', 'rosario', etc."
    )

class OptionalFields(BaseModel):
    rooms: Optional[str] = None
    bedrooms: Optional[str] = None
    bathrooms: Optional[str] = None
    garages: Optional[str] = None
    price: Optional[str] = None
    age: Optional[str] = None
    sorting: Optional[str] = None
    publicationDate: Optional[str] = None

class PropertySearchParams(BaseModel):
    required: RequiredFields
    optional: OptionalFields = Field(default_factory=OptionalFields)

class AgentState(TypedDict):
    query: Annotated[list, add_messages]
    url: Optional[AnyUrl] = None
    properties: Optional[list] = None
    analysis: Optional[str] = None
    query_data: Optional[PropertySearchParams] = None