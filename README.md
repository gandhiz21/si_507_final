# si_507_final
Final project repository for SI 507, Fall 2022

# Welcome to the Ann Arbor Activities program!
Please download the contents of this github repository into one folder
You must add the API key to line ____ of ann_arbor_activities.py. The API key is shown below:

API_Key = "RnptfKoWHmedYQs00_eC02DQgRdu3n2_KzQ2dsHafeGa3EEZ7pMNrMeJBJp5LyfEKv8UzOEI74mo3MnrDgCWMTNJJBLBBIbv7SFo873QJ3OVACHTHRd3iHklwkWGY3Yx"

# Then, you may run the code for ann_arbor_activities.py
    If it is the first time today you are using the program, and yelp_dict.json was not made today, a series of API calls will be made at first
    If yelp_dict.json was made today, the program will use the information in the cache to build the Graph
    The program will prompt you to enter 1-3 of the 24 categories you would like your activity to include. Make sure the categories are spelled correctly and separated by spaces.
    Assuming there are activities that fit in all your categories, the program will return up to 5 of the highest rated activities, according to Yelp.
    From here, you may enter a number from 1-9 to obtain more information about the activities, do another search, or exit the program. 
          1. Get ALL of the activities related to your categories.
          2. Get additional information about one of the activities.
          3. Get 3 reviews about one of the activities.
          4. Get redirected to a URL to the Yelp page of one of the activities.
          5. See a scale of the ratings from all of the activities.
          6. See a chart of the hours of operations of all of the activities.
          7. Get reviews from a different website (TripAdvisor).
          8. Do a new search.
          9. Exit the program.

# You must import the following python packages to ensure the script will run correctly
import requests

import json

import os

import networkx as nx

import datetime

from pathlib import Path

import webbrowser

import matplotlib.pyplot as plt

from bs4 import BeautifulSoup

from tripadvisor_dict import tripadvisor_dict #(importing the dictionary from tripadvisor_dict.py)
