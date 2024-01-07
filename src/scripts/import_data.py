# Script to import species survey data
# from a file supplied on the command line
# into the database.

import sys
import csv
from sqlalchemy.orm import Session

from src.app.database import SessionLocal, SpeciesLocationDB
from src.app.utils import find_or_create_survey_location, find_or_create_species


def import_data(filepath: str, db: Session):
    """
    Adds species survey data contained in given file to the database.
    """
    print(f"Importing species survey data from {filepath} to database...")
    with open(filepath) as f:
        reader = csv.DictReader(f)
        for row in reader:
            survey_location = find_or_create_survey_location(
                db,
                latitude=row["decimalLatitude"],
                longitude=row["decimalLongitude"],
                locality=row["locality"]
            )
            species = find_or_create_species(
                db,
                id=row["scientificNameID"],
                name=row["scientificName"],
                kingdom=row["kingdom"],
                phylum=row["phylum"],
                species_class=row["class"],
                order=row["order_"],
                family=row["family"],
                genus=row["genus"],
                scientific_name_authorship=row["scientificNameAuthorship"]
            )
            db.flush()
            species_location = SpeciesLocationDB(
                survey_location_id=survey_location.id,
                species_id=species.id
            )
            db.add(species_location)


def main():
    """
    Imports species survey data to the database from a file supplied as a command line arg.
    """
    try:
        filepath = sys.argv[1]
    except IndexError:
        print("Missing argument: please supply path to file containing survey data")
        sys.exit(1)
    with SessionLocal() as db_session, db_session.begin():
        try:
            import_data(filepath, db_session)
        except Exception as err:
            print(f'Error importing data to database: {err}. Reverting changes')
            db_session.rollback()
            sys.exit(1)


if __name__ == "__main__":
    main()
