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
`configs/user_config.yml`, and the specified analysis configuration file

Parameters
----------
analysis_config : str
    configs/analysis_config.yml

Returns
-------
analysis_obj : Analysis
    Analysis object containing consolidated parameters from the configuration files

"""

class Analysis(analysis_config:str):

    def __init__(self, analysis_config: str) -> None:
        CONFIG_PATHS = ['configs/system_config.yml', 'configs/user_config.yml']

        # add the analysis config to the list of paths to load
        paths = CONFIG_PATHS + [analysis_config]

        # initialize empty dictionary to hold the configuration
        config = {}

        # load each config file and update the config dictionary
        for path in paths:
            with open(path, 'r') as f:
                this_config = yaml.safe_load(f)
            config.update(this_config)

        self.config = config
 

    # Set up logging
        logging.basicConfig(filename='analysis.log', level=logging.INFO)

    # Define functions for data analysis
    def load_data(self) -> None:

        """
        Retrieves data from the specified URL.

        Args:
        url (str): The URL to retrieve data from.

        Returns:
        dict: The retrieved data as a dictionary.
        """
        try:
        # Retrieve data from PokeAPI
            base_url =self.config("base_url")
            param_type =self.config("param_type")

            pokeapi_url = f"{base_url}/{param_type}"
            data = requests.get(pokeapi_url)
            data.raise_for_status()
            self.dataset = data
    
        except Exception as e:
            logging.error(f"Error retrieving data: {e}")
        return None

    def compute_analysis(self):
        """
        Analyzes the data retrieved from PokeAPI.

        Args:
        data (dict): The data retrieved from the PokeAPI.

        Returns:
        analysis_output : pokemon_types and its count
        """
        # Extract relevant information from the data
        pokemon_types = [entry["name"] for entry in self.dataset["results"]]
        pokemon_type_urls = [entry["url"] for entry in self.dataset["results"]]
    
        # Calculate the count of Pokémon types
        type_count = len(pokemon_types)
    
        # Analyze the distribution of Pokémon types
        type_distribution = {type_: pokemon_types.count(type_) for type_ in set(pokemon_types)}
    
        # Identify the most common Pokémon types
        most_common_types = sorted(type_distribution.items(), key=lambda x: x[1], reverse=True)

        print(f'analysis_output : Pokemon Types are:{pokemon_types}, The count of Pokémon types are:{type_count}')

        plot_color = self.config("plot_color")

        pokemon_types = list(type_distribution.keys())
        counts = list(type_distribution.values())

        return type_count, type_distribution, most_common_types


    def plot_data(self,pokemon_types,counts,plot_color) -> plt.Figure:
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
            plt.figure(self.config('figure_size'))
            plt.bar(pokemon_types, counts, color=plot_color)

            # Add labels and title
            plt.xlabel(self.config('plot_x_axis_title'))
            plt.ylabel(self.config('plot_y_axis_title'))
            plt.title(self.config('plot_title'))

            # Rotate x-axis labels for better visibility
            plt.xticks(rotation=45, ha='right')

            # Add grid lines
            plt.grid(axis='y', linestyle='--', alpha=0.7)

            # Adjust layout
            plt.tight_layout()

            # Save the plot
            plt.savefig(self.config('default_save_path'))

            # Show the plot
            plt.show()

        except Exception as e:
            print(f"Error plotting data: {e}")

        pass

    
    def notify_done(self, message: str) -> None:

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
        
            topicname= self.config('topicname')
            title= self.config('title')

            # Define the notification message
            data= 'Analysis is of Pokemon data is complete! Check the results.'

            requests.post(f"https://ntfy.sh/{topicname}", 
            data=f"{data}".encode(encoding='utf-8'),headers={'Title': title})
        
            print("Notification sent successfully!")

        except Exception as e:
            print(f"Error sending notification: {str(e)}")

        pass
