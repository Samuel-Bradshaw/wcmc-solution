# Sam Bradshaw WCMC Solution

Contains scripts 

## Dependencies

Requires Python version 3.10 or later.

## Set up

Before running the app, install dependencies by:
```
pip install -r requirements.txt
```

## Importing data

To import species survey data from a csv file to the database, run the following command:
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
```
python -m src.scripts.get_phylum_data
```

## Testing

Unit tests are located in the `/test` directory. To run all unit tests simply run the command
```
pytest
```

## TODOs

* Configure Python dependencies using poetry.
* Configure database migrations.
* Some unit test coverage is missing.
* Improve documentation for API.
