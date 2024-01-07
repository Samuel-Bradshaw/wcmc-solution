# Client script that requests data from species survey API.
#
# Prints a line for each phylum in the database along with
# the name of the species in that phylum which was observed
# at the most locations.

import aiohttp
import asyncio
from collections import defaultdict

API_BASE_URL = 'http://127.0.0.1:8000'

async def main():
    """
    Retrieves species data from species survey API and prints 
    each phylum along the most observed species for each phylum.
    """
    all_species = await get_all_species()
    await get_locations_count(all_species)
    phyla = defaultdict(list)
    for species in all_species:
        phyla[species["phylum"]].append(species)
    most_observed_phylum_species = find_most_observed_species(phyla)
    for phylum in most_observed_phylum_species:
        print(phylum)

async def get_all_species() -> list[dict]:
    """
    Retrieves all species data from species survey API
    """
    print(f"Fetching species data...")
    species = []
    async with aiohttp.ClientSession() as session:
        # Results are paginateed - keep requesting pages until we get a 404 response
        page = 0
        while True:
            async with session.get(
                f'{API_BASE_URL}/species',
                params=dict(page=page)
            ) as response:
                if response.status == 404:
                    break
                page += 1
                json = await response.json()
                species += json["data"]
    return species

async def get_locations_count(species: list[dict]) -> None:
    """
    Retrieves the number of times each species was observed
    from the species survey API and appends the result
    to each item in the list of species.
    """
    print("Fetching species location data...")
    async with aiohttp.ClientSession() as session:
        for s in species:
            async with session.get(
                f"{API_BASE_URL}/species/{s['id']}/locations"
            ) as response:
                json = await response.json()
                s.update(locations_count=len(json))


def find_most_observed_species(phyla: dict[list]) -> list[dict]:
    """
    Finds the species in each phylum that was observed the most times.
    Returns the results as a list of dicts with one item for each phylum.
    """
    most_observed_phylum_species = []
    for phylum, phylum_species in phyla.items():
        max_observed_locations = max(s["locations_count"] for s in phylum_species)
        most_observed_species = [
            s["name"] for s in phylum_species
            if s["locations_count"] == max_observed_locations
        ]
        most_observed_phylum_species.append(
            dict(
                kingdom=phylum_species[0]["kingdom"],
                phylum=phylum,
                most_observed_species= most_observed_species,
                observed_locations_count=max_observed_locations
            )
        )
    # Sort results in alphabetical order of kingdom and phylum
    most_observed_phylum_species.sort(key=lambda phylum: (phylum["kingdom"], phylum["phylum"]))
    return most_observed_phylum_species


if __name__ == "__main__":
    asyncio.run(main())

