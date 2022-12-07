##########################################
########### Name: Zahra Gandhi ###########
########### uniqname: gandhiz ############
##########################################

import requests
import json
from urllib.parse import quote

API_Key = "RnptfKoWHmedYQs00_eC02DQgRdu3n2_KzQ2dsHafeGa3EEZ7pMNrMeJBJp5LyfEKv8UzOEI74mo3MnrDgCWMTNJJBLBBIbv7SFo873QJ3OVACHTHRd3iHklwkWGY3Yx"
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.

# Yelp API request functions # From Yelp Fusion Github
def request(host, path, api_key, url_params=None):
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % api_key,
    }

    print(u'Querying {0} ...'.format(url))

    response = requests.request('GET', url, headers=headers, params=url_params)

    return response.json()


def search(api_key, term, location):
    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': 50 # max limit
    }
    return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)


def get_business_review(api_key, business_id): # business reviews
    business_path = BUSINESS_PATH + business_id + "/reviews"

    return request(API_HOST, business_path, api_key)


def get_business(api_key, business_id): # extra details like hours, photos...
    business_path = BUSINESS_PATH + business_id

    return request(API_HOST, business_path, api_key)


# Caching functions
import os
import json
CACHE_FILENAME = "yelp_dict.json" # equivalent to searchname_dict

def open_cache(): # only works when the cache is not empty
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close()

YELP_CACHE = open_cache()

# Graph inputs
import networkx as nx
import datetime
#, "Nature", "Shopping", "Park", "Museum", "Nightlife"
# terms to search API
searchterms = ["Exercise", "Nightlife", "Park",
"Nature", "Shopping", "Museum", "Snacks",
"Dessert", "Bar", "Art", "Music", "Sports",
"Clothes", "Beauty", "Animals", "Kids", "Free",
"Cafe", "Tech", "Theater", "Volunteer", "Books"]
searchname_dict = {} # dict of API results
# dictionaries of attributes that I want to be accessible within the graph
yelp_id = {} # id for further testing
image_url = {} # display picture
url = {} # url of yelp page
review_count = {} # number of reviews
rating = {} # rating
display_address = {} # full address
display_phone = {} # phone number
G = nx.Graph() # Initialize a Graph object
nodes = [] # set to empty list

# Making the Graph
if os.path.exists(CACHE_FILENAME) == False: # if no cache
    t1 = datetime.datetime.now().timestamp()
    for searchterm in searchterms: # adding all the API results to the searchname_list
        searchname = search(API_Key, searchterm, "Ann Arbor, MI")
        options = searchname["businesses"]
        print(len(options))

        searchname_dict[searchterm] = options # appending results to the respective key in the results dictionary

        G.add_node(searchterm) # adding "Exercise", "Nature", etc. as nodes in the Graph

        for entry in searchname_dict[searchterm]:
            nodes.append(entry["name"])
        G.add_nodes_from(nodes)
        for node in nodes:
            G.add_edge(searchterm, node)

        nodes = [] # resetting to empty list for the next searchterm

        for entry in searchname_dict[searchterm]: # assigning attributes (values) to the entries (keys) in the attribute dictionaries
            yelp_id[entry["name"]] = entry['id']
            image_url[entry["name"]] = entry["image_url"]
            url[entry["name"]] = entry["url"]
            review_count[entry["name"]] = entry["review_count"]
            rating[entry["name"]] = entry["rating"]
            display_address[entry["name"]] = entry["location"]["display_address"][0]
            display_phone[entry["name"]] = entry["display_phone"]
    t2 = datetime.datetime.now().timestamp()
else: # if cache exists
    t3 = datetime.datetime.now().timestamp()
    for searchterm in searchterms:
        searchname_dict[searchterm] = YELP_CACHE[searchterm] # building searchname_dict using the cache YELP_CACHE

        G.add_node(searchterm) # adding "Exercise", "Nature", etc. as nodes in the Graph

        for entry in searchname_dict[searchterm]:
            nodes.append(entry["name"])
        G.add_nodes_from(nodes)
        for node in nodes:
            G.add_edge(searchterm, node)

        nodes = [] # resetting to empty list for the next searchterm

        for entry in searchname_dict[searchterm]: # assigning attributes (values) to the entries (keys) in the attribute dictionaries
            yelp_id[entry["name"]] = entry['id']
            image_url[entry["name"]] = entry["image_url"]
            url[entry["name"]] = entry["url"]
            review_count[entry["name"]] = entry["review_count"]
            rating[entry["name"]] = entry["rating"]
            display_address[entry["name"]] = entry["location"]["display_address"][0]
            display_phone[entry["name"]] = entry["display_phone"]
    t4 = datetime.datetime.now().timestamp()

# Saving the cache daily
from datetime import date
from pathlib import Path
path = Path(CACHE_FILENAME)
if os.path.exists(CACHE_FILENAME) == True:
    timestamp = date.fromtimestamp(path.stat().st_mtime) # records today's date

if os.path.exists(CACHE_FILENAME) == True and date.today() == timestamp: # if cache exists and it was made today
    print("Cache was used.") # use cache
    print("Time to build graph with cache:", (t4 - t3) * 1000, "ms")
elif os.path.exists(CACHE_FILENAME) == True and date.today() != timestamp: # if cache exists but it was not made today
    os.remove(path) # remove old cache
    print("Building a new cache...")
    print("Time to build graph with cache:", (t4 - t3) * 1000, "ms")
    for searchterm in searchterms:
        YELP_CACHE[searchterm] = searchname_dict[searchterm]
        save_cache(YELP_CACHE)
else: # if there's no cache at all
    print("Building cache...")
    print("Time to build graph without cache:", (t2 - t1) * 1000, "ms")
    for searchterm in searchterms:
        YELP_CACHE[searchterm] = searchname_dict[searchterm]
        save_cache(YELP_CACHE)

# Assigning dictionary attributes to the nodes themselves
nx.set_node_attributes(G, yelp_id, "yelp_id")
nx.set_node_attributes(G, image_url, "image_url")
nx.set_node_attributes(G, url, "url")
nx.set_node_attributes(G, review_count, "review_count")
nx.set_node_attributes(G, rating, "rating")
nx.set_node_attributes(G, display_address, "display_address")
nx.set_node_attributes(G, display_phone, "display_phone")

# Checks for me
for n in G.nodes(): # Loop through every node, in our data "n" will be the name of the person
    if G.nodes[n] == {}: # for searchterms without api searches (ex: "Exercise")
        print(n)
    else:
        print(n, G.nodes[n]["rating"]) # Access every node by its name, and then by the attribute "rating"
print(nx.info(G)) # Print information about the Graph
#print(nx.node_connected_component(G, "Nightlife")) # getting connected nodes
#print(nx.node_connected_component(G, "Exercise"))
#print(nx.node_connected_component(G, "Park"))
#print(nx.node_connected_component(G, "Nature"))
for searchterm in searchterms:
    print(searchterm, len(searchname_dict[searchterm]))

#for n in G.nodes(): # will print any connections over any distances
#    if len(nx.node_connected_component(G, n)) > 1 and G.nodes[n] != {}:
#        print(n, nx.node_connected_component(G, n))

for n in G.nodes(): # will print direct connections (entry to keyword)
    if len(G.edges(n)) > 1 and G.nodes[n] != {}: # prints entries with connections to more than one keyword
        print(n, G.edges(n))