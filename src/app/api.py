from typing import Annotated
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, HTTPException, Query, Response

from .database import SessionLocal, SurveyLocationDB, SpeciesDB, SpeciesLocationDB
from .schemas import (
    Species,
    PaginatedResponse,
    SurveyLocation,
    SpeciesPatch,
    SpeciesLocationCreate,
    SpeciesLocationResponse
)
from .utils import find_or_create_survey_location

MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 25

api = FastAPI(title="Species survey data API")

def get_db():
    """
    Yield database session and close after finishing.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API endpoints

@api.get("/location/species", response_model=list[Species])
def get_species_at_location(
    latitude: float,
    longitude: float,
    radius: float | None = None,
    db: Session = Depends(get_db)
):
    """
    Retrieves a list of all species at a particular latitude and longitude.

    If radius is specified, then all species within the specified radius of 
    the given latitude and longitude are returned.
    """
    if radius:
        # Return all species within given radius of provided latitude and longitude
        return (
            db.query(SpeciesDB)
            .join(SpeciesLocationDB, SpeciesDB.id == SpeciesLocationDB.species_id)
            .join(SurveyLocationDB, SpeciesLocationDB.survey_location_id == SurveyLocationDB.id)
            .filter(
                func.pow(SurveyLocationDB.latitude - latitude, 2)
                + func.pow(SurveyLocationDB.longitude - longitude, 2)
                <= radius**2
            )
        )
    # Return all species at exact latitude and longitude
    return (
        db.query(SpeciesDB)
        .join(SpeciesLocationDB, SpeciesDB.id == SpeciesLocationDB.species_id)
        .join(SurveyLocationDB, SpeciesLocationDB.survey_location_id == SurveyLocationDB.id)
        .filter(
            SurveyLocationDB.latitude == latitude,
            SurveyLocationDB.longitude == longitude
        )
    )

@api.get(
    "/species",
    response_model=PaginatedResponse[Species],
    responses={404: dict(description="Page number out of range")}
)
def get_all_species(
    db: Session = Depends(get_db),
    page: Annotated[int, Query(ge=0)] = 0,
    page_size: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE
):
    """
    Retrieve a paginated list of all species records.
    """
    # Verify supplied page number within allowed range
    species_count = db.query(SpeciesDB).count()
    max_page_number = int(species_count/page_size)
    if page > max_page_number:
        raise HTTPException(
            status_code=404,
            detail=f"Page number {page} out of range."
        )
    species = (
        db.query(SpeciesDB)
        .order_by(SpeciesDB.name)
        .limit(page_size)
        .offset(page*page_size)
    )
    return PaginatedResponse(
        page=page,
        page_size=page_size,
        last_page=max_page_number,
        data=species
    )

@api.get(
    "/species/{scientific_name_id}/locations",
    response_model=list[SurveyLocation],
    response_model_exclude_none=True,
    responses={404: dict(description="Species not found")}
)
def get_species_locations(
    scientific_name_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieve a list of all locations where a specific species is found.
    """
    # Check supplied species id is valid
    if not db.get(SpeciesDB, scientific_name_id):
        raise HTTPException(
            status_code=404,
            detail=f"Species with id {scientific_name_id} not found"
        )
    return (
        db.query(SurveyLocationDB)
        .join(SpeciesLocationDB, SpeciesLocationDB.survey_location_id == SurveyLocationDB.id)
        .join(SpeciesDB, SpeciesDB.id == SpeciesLocationDB.species_id)
        .where(
            SpeciesDB.id == scientific_name_id
        )
    )

@api.delete(
    "/species/{scientific_name_id}",
    responses={404: dict(description="Species not found")}
)
def delete_species(scientific_name_id: int, db: Session = Depends(get_db)):
    """
    Delete species with given id from the database.
    """
    species = db.get(SpeciesDB, scientific_name_id)
    if not species:
        raise HTTPException(
            status_code=404,
            detail=f"Species with id {scientific_name_id} not found"
        )
    db.delete(species)
    db.commit()
    return Response(status_code=200)


@api.patch(
    "/species/{scientific_name_id}",
    response_model=Species,
    responses={404: dict(description="Species not found")}
)
def patch_species(
    scientific_name_id: int,
    species_patch: SpeciesPatch,
    db: Session = Depends(get_db)
):
    """
    Update a species with given id from database.
    """
    # Check supplied species id is valid
    species: SpeciesDB = db.get(SpeciesDB, scientific_name_id)
    if not species:
        raise HTTPException(
            status_code=404,
            detail=f"Species with id {scientific_name_id} not found"
        )
    # Update species entry in database
    for field, value in species_patch:
        setattr(species, field, value)
    db.commit()
    return species


@api.post(
    "/species/{scientific_name_id}/locations",
    response_model=SpeciesLocationResponse,
    responses={404: dict(description="Species not found")}
)
def report_species_location(
    scientific_name_id: int,
    species_location: SpeciesLocationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new species location record in the database.

    If there is not an existing survey location with the coordinates provided in the request body,
    then a new servey location record is also created in the database.
    """
    # Check supplied species id is valid
    species: SpeciesDB = db.get(SpeciesDB, scientific_name_id)
    if not species:
        raise HTTPException(
            status_code=404,
            detail=f"Species with id {scientific_name_id} not found"
        )
    survey_location: SurveyLocationDB = find_or_create_survey_location(
        species_location.latitude,
        species_location.longitude
    )
    db.commit()
    species_location = SpeciesLocationDB(
        species_id=species.id,
        location_id=survey_location.id
    )
    db.add(species_location)
    db.commit()
    return SpeciesLocationResponse(
        species=species,
        survey_location=survey_location
    )

