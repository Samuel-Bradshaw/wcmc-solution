# Sam Bradshaw WCMC Solution

API for querying species survey data.

## Dependencies

Requires Python version 3.10 or later.

## Set up

Before running the app, install dependencies by:
```
pip install -r requirements.txt
```

## Importing data

To import species survey data from a csv file to the database, run the following command
to execute the `import_data.py` script:
```
python -m src.scripts.import_data 'Survey_of_algae,_sponges,_and_ascidians,_Fiji,_2007.csv'
```

## Running locally

To start the API app locally, run:
```
uvicorn src.app.api:api
```
This will start the app running on http://127.0.0.1:8000.

Full documentation for the API will then be available at http://127.0.0.1:8000/redoc.
You can also use the interactive docs at http://127.0.0.1:8000/docs to query the endpoints.


## Printing phylum data

To call the `get_phylum_data.py` API client script to retrieve species survey data
and prints phylum information to stdout, run:
```
python src/scripts/get_phylum_data.py
```

## Testing

Unit tests are located in the `/test` directory. To run all unit tests simply run the command
```
pytest
```

## TODOs

* Configure Python dependencies using Poetry.
* Configure database migrations using alembic.
* Some unit test coverage is missing.
* Improve API documentation.

## Assumptions and notes

* All data in supplied csv file is valid - where there are duplicate entries in the file these are imported twice.
If we want to avoid duplicate entries, we should add a unique constraint to the `specieslocation` table
on the `species_id` and `survey_location_id` columns.
* If any data in the file fed to the `import_data.py` script is in an unexpected format, then
no data from that file should be imported (i.e. the data should never be partially imported).
* Only use latitude and longitude to determine if a survey location is already in the database
(i.e. ignore the locality).

