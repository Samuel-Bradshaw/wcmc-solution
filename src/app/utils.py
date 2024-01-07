from sqlalchemy.orm import Session
from .database import SurveyLocationDB, SpeciesDB

def find_or_create_survey_location(
    db: Session,
    latitude: float,
    longitude: float,
    locality: str | None = None
) -> SurveyLocationDB:
    """
    Search for an entry in surveylocation table with given latitude and longitude.

    If an existing entry is found, then it is returned.

    If no existing entry is found then a new entry to the surveylocation table
    is created(but not committed).
    """
    survey_location = db.query(SurveyLocationDB).filter(
        SurveyLocationDB.latitude == latitude,
        SurveyLocationDB.longitude == longitude
    ).one_or_none()
    if not survey_location:
        # Add location to db
        survey_location = SurveyLocationDB(
            latitude=latitude,
            longitude=longitude,
            locality=locality
        )
        db.add(survey_location)
    return survey_location

def find_or_create_species(
    db: Session,
    id: str,
    name: str,
    kingdom: str,
    phylum: str,
    species_class: str,
    order: str,
    family: str,
    genus: str,
    scientific_name_authorship: str
) -> SpeciesDB:
    """
    Search for an entry in species table with given id.

    If an existing entry is found, then it is returned.

    If no existing entry is found then a new entry to the species table
    is created (but not committed).
    """
    # Check id field is valid integer
    try:
        id = int(id)
    except ValueError:
        # If not a valid integer, integer id can be at end of colon-delimited string
        id = int(id.split(':')[-1])

    species: SpeciesDB | None = db.get(SpeciesDB, id)
    if not species:
        species = SpeciesDB(
            id=id,
            name=name,
            kingdom=kingdom,
            phylum=phylum,
            species_class=species_class,
            order=order,
            family=family,
            genus=genus,
            scientific_name_authorship=scientific_name_authorship
        )
        db.add(species)
    return species

