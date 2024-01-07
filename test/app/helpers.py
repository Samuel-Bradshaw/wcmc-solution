from sqlalchemy.orm import Session
from src.app.database import SpeciesDB, SurveyLocationDB, SpeciesLocationDB


SPECIES1 = dict(
    id=145123,
    name="Jania adhaerens",
    kingdom="Plantae",
    phylum="Rhodophyta",
    species_class="Florideophyceae",
    order="Corallinales",
    family="Corallinaceae",
    genus="Jania",
    scientific_name_authorship="J.V.Lamouroux, 1816"
)
SPECIES2 = dict(
    id=372311,
    name="Rhipiliella verticillata",
    kingdom="Plantae",
    phylum="Chlorophyta",
    species_class="Ulvophyceae",
    order="Bryopsidales",
    family="Udoteaceae",
    genus="Rhipiliella",
    scientific_name_authorship="Kraft, 1986"
)
SPECIES3 = dict(
    id=165287,
    name="Phyllospongia papyracea",
    kingdom="Animalia",
    phylum="Porifera",
    species_class="Demospongiae",
    order="Dictyoceratida",
    family="Thorectidae",
    genus="Phyllospongia",
    scientific_name_authorship="Esper, 1794"
)

def create_species(db: Session):
    species = (
        SpeciesDB(**SPECIES1),
        SpeciesDB(**SPECIES2),
        SpeciesDB(**SPECIES3)
    )
    db.add_all(species)
    db.commit()
    return species

def add_species_location_at_location(
    species: SpeciesDB,
    latitude: float,
    longitude: float,
    db: Session
) -> SurveyLocationDB:
    survey_location = SurveyLocationDB(
        latitude=latitude,
        longitude=longitude
    )
    db.add(survey_location)
    db.commit()
    species_location = SpeciesLocationDB(
        survey_location_id=survey_location.id,
        species_id=species.id
    )
    db.add(species_location)
    db.commit()
    return survey_location

def species_response(species: SpeciesDB) -> dict:
    return dict(
        id=species.id,
        name=species.name,
        kingdom=species.kingdom,
        phylum=species.phylum,
        order=species.order,
        species_class=species.species_class,
        family=species.family,
        genus=species.genus,
        scientific_name_authorship=species.scientific_name_authorship
    )