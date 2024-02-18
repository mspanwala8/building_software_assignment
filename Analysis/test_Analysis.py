import pytest
from Analysis import load_data, compute_analysis

# Define test cases for load_data function
def test_load_data():
    # Define a sample URL
    url = "https://pokeapi.co/api/v2/type"
    # Test loading data from the URL
    data = load_data(url)
    # Assert that data is not None
    assert data is not None

# Define test cases for compute_analysis function
def test_compute_analysis():
    
    url = "https://pokeapi.co/api/v2/type"
    data = load_data(url)
    pokemon_types = [entry["name"] for entry in data["results"]]

    # Calculate the count of Pokémon types
    type_count = len(pokemon_types)

    # Perform assertions to ensure the analysis is correct
    assert type_count == 20

if __name__ == "__main__":
    pytest.main()
