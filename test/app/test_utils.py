from sqlalchemy.orm import Session
from src.app.utils import find_or_create_survey_location
from src.app.database import SurveyLocationDB

def test_find_or_create_survey_location_created_ok(test_db: Session):
    lat, lon = (22.2, 33.3)
    locality = "spam"
    find_or_create_survey_location(test_db, lat, lon, locality)
    test_db.commit()
    survey_location = test_db.query(SurveyLocationDB).one_or_none()
    assert survey_location.latitude == lat
    assert survey_location.longitude == lon
    assert survey_location.locality == locality


def test_find_or_create_survey_location_found_ok(test_db: Session):
    sl = SurveyLocationDB(latitude=42.42, longitude=-42.42)
    test_db.add(sl)
    test_db.commit()
    result = find_or_create_survey_location(test_db, sl.latitude, sl.longitude)
    test_db.query(SurveyLocationDB).one_or_none()
    assert sl == result


# TODO add tests for find_or_create_species

