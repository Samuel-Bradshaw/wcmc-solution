import copy
from aioresponses import aioresponses
import asyncio

from src.scripts.get_phylum_data import get_all_species, get_locations_count, API_BASE_URL

SPECIES = [
    {"id": 1, "name": "Species1", "phylum": "Phylum1", "kingdom": "Kingdom1"},
    {"id": 2, "name": "Species2", "phylum": "Phylum2", "kingdom": "Kingdom1"},
    {"id": 3, "name": "Species3", "phylum": "Phylum3", "kingdom": "Kingdom3"},
]

def test_get_all_species():
    with aioresponses() as mock_session:
        mock_session.get(
            f'{API_BASE_URL}/species?page=0',
            payload={"data": SPECIES[:2]}
        )
        mock_session.get(
            f'{API_BASE_URL}/species?page=1',
            payload={"data": SPECIES[2:]}
        )
        mock_session.get(
            f'{API_BASE_URL}/species?page=2',
            status=404
        )
        result = asyncio.run(get_all_species())
        assert result == SPECIES

def test_get_locations_count():
    species = copy.deepcopy(SPECIES)
    responses = [
        [],
        [{"latitude": 55.5, "longitude" : 22.5}],
        [{"latitude": -55.1, "longitude" : -11.111}, {"latitude": -99.9, "longitude" : 7.2}]
    ]
    with aioresponses() as mock_session:
        for i, s in enumerate(species):
            mock_session.get(
                f"{API_BASE_URL}/species/{s['id']}/locations",
                payload=responses[i]
            )
        expected_species = copy.deepcopy(SPECIES)
        for i, s in enumerate(expected_species):
            s["locations_count"] = len(responses[i])
        asyncio.run((get_locations_count(species)))
        assert species == expected_species


# TODO: test find_most_observed_species

# TODO: test main
