from pydantic import BaseModel
from typing import Generic, TypeVar

DataT = TypeVar('DataT')

class PaginatedResponse(BaseModel, Generic[DataT]):
    page: int
    page_size: int
    last_page: int
    data: list[DataT]

class Species(BaseModel):
    id: int
    name: str
    kingdom: str
    phylum: str
    species_class: str
    order: str
    family: str
    genus: str
    scientific_name_authorship: str

    model_config = dict(from_attributes=True)

class SpeciesPatch(BaseModel):
    name: str

class SurveyLocation(BaseModel):
    id: int
    latitude: float
    longitude: float
    locality: str | None

    model_config = dict(from_attributes=True)

class SpeciesLocationCreate(BaseModel):
    latitude: float
    longitude: float

class SpeciesLocationResponse(BaseModel):
    species: Species
    survey_location: SurveyLocation

