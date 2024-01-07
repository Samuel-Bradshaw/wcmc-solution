# wcmc-solution

# Dependencies

Requires Python version 3.10 or later.

# Set up

To install dependencies, run the following command
```
pip install -r requirements.txt
```


# Importing data
```
python -m src.scripts.import_data 'Survey_of_algae,_sponges,_and_ascidians,_Fiji,_2007.csv'
```

```
uvicorn app.api:api 
```

```
python -m scripts.get_phylum_data
```

## Testing

Unit tests are located in the `/test` directory. To run all unit tests simply run the command
```
pytest
```

