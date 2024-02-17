"""
Analysis Module
====================

This module retrieves data from the PokeAPI, analyzes it, and plots the results.

Functions:
    - load_data: Retrieves and loads data from the PokeAPI.
    - compute_analysis: Analyzes the retrieved data.
    - plot_data: Plots the analyzed data.
    - notify_done: To send the notification to the user once Analysis is complete.
"""

import requests
import yaml
import logging
import matplotlib.pyplot as plt
import numpy

"""" 

Load config into an Analysis object

Load system-wide configuration from `configs/system_config.yml`, user configuration from
`configs/user_config.yml`, and `configs/job_file.yml`

Parameters
----------
analysis_config : str
    configs/analysis_config.yml

Returns
-------
analysis_obj : Analysis
    Analysis object containing consolidated parameters from the configuration files

"""

class Analysis():

    def __init__(self, analysis_config: str) -> None:
        self.system_config = {}
        self.user_config = {}
        self.job_config = {}

        # Load system configuration
        with open('configs/system_config.yml', 'r') as sys_config_file:
            self.system_config = yaml.safe_load(sys_config_file)

        # Load user configuration
        with open('configs/user_config.yml', 'r') as user_config_file:
            self.user_config = yaml.safe_load(user_config_file)

        # Load job-specific configuration
        with open('configs/job_file.yml', 'r') as job_config_file:
            self.job_config = yaml.safe_load(job_config_file)

        # Consolidate configurations
        self.analysis_obj = {
            "system_config": self.system_config,
            "user_config": self.user_config,
            "job_config": self.job_config
        }

    def get_value(self, key):
        # Search for the key in each configuration dictionary
        for config_name, config in self.analysis_obj.items():
            if key in config:
                return config[key]
        # If key is not found in any configuration file
        return None
    
if __name__ == "__main__":

    analysis_instance = Analysis("configs/analysis_config.yml")

    base_url = analysis_instance.get_value("base_url")
    param_type = analysis_instance.get_value('param_type')
 

# Set up logging
logging.basicConfig(filename='analysis.log', level=logging.INFO)

# Define functions for data analysis
def load_data(url) -> None:

    """
    Retrieves data from the specified URL.

    Args:
        url (str): The URL to retrieve data from.

    Returns:
        dict: The retrieved data as a dictionary.
    """

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    except Exception as e:
        logging.error(f"Error retrieving data: {e}")
        return None

def compute_analysis(data):
    """
    Analyzes the data retrieved from PokeAPI.

    Args:
        data (dict): The data retrieved from the PokeAPI.

    Returns:
        analysis_output : pokemon_types and its count
    """
    # Extract relevant information from the data
    pokemon_types = [entry["name"] for entry in data["results"]]
    pokemon_type_urls = [entry["url"] for entry in data["results"]]
    
    # Calculate the count of Pokémon types
    type_count = len(pokemon_types)
    
    # Analyze the distribution of Pokémon types
    type_distribution = {type_: pokemon_types.count(type_) for type_ in set(pokemon_types)}
    
    # Identify the most common Pokémon types
    most_common_types = sorted(type_distribution.items(), key=lambda x: x[1], reverse=True)

    print(f'analysis_output : Pokemon Types are:{pokemon_types}, The count of Pokémon types are:{type_count}')

    # After analysis is done, call the notify_done() function
    notify_done()

    plot_color = analysis_instance.get_value("plot_color")

    pokemon_types = list(type_distribution.keys())
    counts = list(type_distribution.values())

    # Call the plot_data function
    plot_data(pokemon_types,counts,plot_color)

    return type_count, type_distribution, most_common_types, data


def plot_data(pokemon_types,counts,plot_color) -> plt.Figure:
    """
    Plots the data using matplotlib.

    Args:
        pokemon_types (list): List of Pokémon types.
        counts (list): List of counts corresponding to each Pokémon type.
        plot_color (str): Color for the bar chart.

    Returns:
        fig : matplotlib.Figure
    """
    try:
        # Ensure data consistency
        assert len(pokemon_types) == len(counts), "Length of pokemon_types and counts should be the same."

        # Create the bar chart
        plt.figure(analysis_instance.get_value('figure_size'))
        plt.bar(pokemon_types, counts, color=plot_color)

        # Add labels and title
        plt.xlabel(analysis_instance.get_value('plot_x_axis_title'))
        plt.ylabel(analysis_instance.get_value('plot_y_axis_title'))
        plt.title(analysis_instance.get_value('plot_title'))

        # Rotate x-axis labels for better visibility
        plt.xticks(rotation=45, ha='right')

        # Add grid lines
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # Adjust layout
        plt.tight_layout()

        # Save the plot
        plt.savefig(analysis_instance.get_value('default_save_path'))

        # Show the plot
        plt.show()

    except Exception as e:
        print(f"Error plotting data: {e}")

    
def notify_done() -> None:

    """
    Notify the user that analysis is complete.

    Send a notification to the user through the ntfy.sh webpush service.

    Parameters
    ----------
    message : str
    Text of the notification to send

    Returns
    -------
    Printed message

    """ 
    try:
        
        topicname= analysis_instance.get_value('topicname')
        title= analysis_instance.get_value('title')

        # Define the notification message
        data= 'Analysis is of Pokemon data is complete! Check the results.'

        requests.post(f"https://ntfy.sh/{topicname}", 
        data=f"{data}".encode(encoding='utf-8'),headers={'Title': title})
        
        print("Notification sent successfully!")

    except Exception as e:
        print(f"Error sending notification: {str(e)}")


if __name__ == "__main__":
    # Retrieve data from PokeAPI
    pokeapi_url = f"{base_url}/{param_type}"
    data = load_data(pokeapi_url)
    if data:
        # Analyze and plot the data
        compute_analysis(data)
    else:
        print("Failed to retrieve data from PokeAPI.")
