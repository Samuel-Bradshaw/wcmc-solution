
from fastapi import Response
from sqlalchemy.orm import Session
from src.app.database import SpeciesDB, SurveyLocationDB, SpeciesLocationDB
from src.app.api import DEFAULT_PAGE_SIZE

from ..conftest import client
from .helpers import create_species, species_response, add_species_location_at_location

#
# get_species_at_location tests
#
def test_get_species_at_location_invalid_param(test_db):
    for invalid_param_url in (
        "/location/species",
        "/location/species?latitude=-16.556",
        "/location/species?longitude=10.77",
        "/location/species?latitude=a&longitude=b",

    ):
        response = client.get(invalid_param_url)
        assert response.status_code == 422

def test_get_species_at_location_ok(test_db: Session):
    def run_test(
        latitude: float,
        longitude: float,
        matching_species: list[SpeciesDB]
    ):
        response = client.get(f"/location/species?longitude={longitude}&latitude={latitude}")
        assert response.status_code == 200
        assert response.json() == [species_response(s) for s in matching_species]
    
    s1, s2, s3 = create_species(test_db)
    lat, lon = -17.12, 20.55

    # Test no species observed at location
    run_test(lat, lon, [])

    # 1 species observed at location
    add_species_location_at_location(s1, lat, lon, test_db)
    add_species_location_at_location(s2, 1.2, 2.3, test_db)
    run_test(lat, lon, [s1])

    # 2 species observed at location
    add_species_location_at_location(s2, lat, lon, test_db)
    add_species_location_at_location(s3, 100.000, 42.222, test_db)
    run_test(lat, lon, [s1, s2])

    # 3 species observed at location
    add_species_location_at_location(s3, lat, lon, test_db)
    run_test(lat, lon, [s1, s2, s3])

def test_get_species_at_location_with_radius_ok(test_db: Session):
    def run_test(
        latitude: float,
        longitude: float,
        radius: float,
        matching_species: list[SpeciesDB]
    ):
        response = client.get(f"/location/species?longitude={longitude}&latitude={latitude}&radius={radius}")
        assert response.status_code == 200
        assert response.json() == [species_response(s) for s in matching_species]

    def change_survey_location(
        survey_location: SurveyLocationDB,
        new_latitude: float,
        new_longitude: float,
        db: Session
    ):
        survey_location.latitude = new_latitude
        survey_location.longitude = new_longitude
        db.commit()

    s1, s2, s3 = create_species(test_db)
    lat, lon = (0.0, 0.0)
    radius = 10

    # Test no species observed within radius
    sl1 = add_species_location_at_location(s1, 100.0, -100.0, test_db)
    run_test(lat, lon, radius, [])

    # Add 2 species observed within radius
    sl2 = add_species_location_at_location(s2, lat, radius, test_db)
    sl3 = add_species_location_at_location(s3, lat, lon, test_db)
    run_test(lat, lon, radius, [s2, s3])

    for new_lat, new_lon in [
        (radius, lat),
        (-6.5, 5.5),
        (7.0, -7.0)
    ]:
        change_survey_location(s2, new_lat, new_lon, test_db)
        run_test(lat, lon, radius, [s2, s3])

    # Move sl1 inside radius, and sl2 and sl3 outside of radius
    change_survey_location(sl2, radius+5, radius+1, test_db)
    change_survey_location(sl3, radius, -radius, test_db)
    change_survey_location(sl1, radius/2, radius/3, test_db)
    run_test(lat, lon, radius, [s1])

#
# get_all_species_tests
#

def test_get_all_location_ok(test_db: Session):

    def check_response(
        response: Response,
        matching_species: list[SpeciesDB],
        page: int = 0,
        page_size: int = DEFAULT_PAGE_SIZE
    ):
        assert response.status_code == 200
        last_page = int(test_db.query(SpeciesDB).count()/page_size)
        assert response.json() == dict(
            data=[species_response(s) for s in matching_species],
            page=page,
            page_size=page_size,
            last_page=last_page
        )

    response = client.get("/species")
    check_response(response, [])

    species = sorted(create_species(test_db), key=lambda s: s.name)
    response = client.get("/species")
    check_response(response, species)

    # Test paging 
    page_size = 1
    for page in range(3):
        response = client.get(f"/species?page={page}&page_size={page_size}")
        check_response(response, [species[page]], page=page, page_size=page_size)


#
# get_species_locations tests
#

def test_get_species_locations_id_not_found(test_db):
    response = client.get("/species/123/locations")
    assert response.status_code == 404


def test_get_species_locations_ok(test_db: Session):
    species: SpeciesDB
    species, *_ = create_species(test_db)

    response = client.get(f"/species/{species.id}/locations")
    assert response.status_code == 200
    assert response.json() == []

    for lat, lon in [(0.0, 0.0), (-16.999, 17.22), (52.77, -66.66)]:
        add_species_location_at_location(species, lat, lon, test_db)
    
    response = client.get(f"/species/{species.id}/locations")
    assert response.status_code == 200
    survey_locations = test_db.query(SurveyLocationDB).all()
    assert response.json() == [
        dict(
            id=sl.id,
            latitude=sl.latitude,
            longitude=sl.longitude
        ) for sl in survey_locations
    ]

#
# delete_species tests
#

def test_get_delete_species_id_not_found(test_db):
    response = client.delete("/species/123")
    assert response.status_code == 404


def test_get_delete_species_id_ok(test_db: Session):
    species: SpeciesDB
    species, *_ = create_species(test_db)
    species_id = str(species.id)
    add_species_location_at_location(species, 0.0, 0.0, test_db)

    response = client.delete(f"/species/{species_id}")
    assert response.status_code == 200
    assert not test_db.get(SpeciesDB, species_id)
    # Check delete is cascaded to specieslocations table
    assert not test_db.query(SpeciesLocationDB).count()


# TODO: add tests for patch_species

# TODO: add tests for report_species_location
