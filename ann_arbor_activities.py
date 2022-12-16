##########################################
########### Name: Zahra Gandhi ###########
########### uniqname: gandhiz ############
##########################################

# Importing modules
import requests
import json
from urllib.parse import quote
import os
import networkx as nx
import datetime
from pathlib import Path
import webbrowser
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from tripadvisor_dict import tripadvisor_dict # importing the dictionary from tripadvisor_dict.py

# Yelp API information
API_Key = "" # INSERT API KEY HERE
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
    #print(u'Querying {0} ...'.format(url))
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
path = Path(CACHE_FILENAME)
# Setting up date/time
if os.path.exists(CACHE_FILENAME) == True:
    timestamp = datetime.date.fromtimestamp(path.stat().st_mtime) # records today's date

# Terms to search Yelp API
searchterms = ["Exercise", "Nightlife", "Park",
"Nature", "Shopping", "Museum", "Snacks",
"Dessert", "Bar", "Art", "Music", "Sports",
"Clothes", "Beauty", "Animals", "Kids", "Free",
"Cafe", "Tech", "Theater", "Volunteer", "Books",
"Games", "Group"]
searchname_dict = {} # dict of API results
# Dictionaries of attributes that I want to be accessible within the graph
yelp_id = {} # id for further testing
image_url = {} # display picture
url = {} # url of yelp page
review_count = {} # number of reviews
rating = {} # rating
display_address = {} # full address
display_phone = {} # phone number
G = nx.Graph() # Initialize a Graph object
nodes = [] # set to empty list

# Constructing the Graph
if os.path.exists(CACHE_FILENAME) == False or datetime.date.today() != timestamp: # if no cache, or if cache was not made today
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
else: # if cache exists and was made today
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
if os.path.exists(CACHE_FILENAME) == True and datetime.date.today() == timestamp: # if cache exists and it was made today
    print("Cache was used.") # use cache
    print("Time to build graph with cache:", (t4 - t3) * 1000, "ms")
elif os.path.exists(CACHE_FILENAME) == True and datetime.date.today() != timestamp: # if cache exists but it was not made today
    os.remove(path) # remove old cache
    print("Building a new cache...")
    print("Time to build graph without cache:", (t2 - t1) * 1000, "ms")
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

print(nx.info(G)) # Print information about the Graph

# Start of user input
if __name__ == "__main__":
    turns = 1
    while True:
        if turns == 1:
            print(" ")
            print("Welcome to the Ann Arbor Activities Program.")
            print("Please enter 1-3 categories you would like your activity to include. Separate them by spaces.")
            print("Here are the possible categories:")
            print("Animals      Clothes         Kids            Shopping")
            print("Art          Dessert         Museum          Snacks")
            print("Bar          Exercise        Music           Sports")
            print("Books        Free            Nature          Tech")
            print("Beauty       Games           Nightlife       Theater")
            print("Cafe         Group           Park            Volunteer")
            categories = input("Categories: ")
            categories_list = categories.split(" ") # splitting input by spaces to recognize categories
            if(set(categories_list).issubset(set(searchterms))): # checks if the entered categories are within the possible list
                activities = [] # list for initial activities
                for n in G.nodes():
                    for item in categories_list:
                        if G.has_edge(n, item): # checking if there is an edge between each node and each category
                            activities.append(n)
                completed_activities = [] # list for activities that match all categories
                for i in activities:
                    if activities.count(i) == len(categories_list): # if an activity has appeared for every category
                        if (i, G.nodes[i]["rating"]) not in completed_activities: # and that activity isn't already in completed_activities
                            completed_activities.append((i, G.nodes[i]["rating"]))
                if completed_activities == []: # if there are no activities that are included in each category, redo search
                    print(" ")
                    print("I'm sorry. No activities satisfy all your categories. Please do another search. ")
                sorted_activities = sorted(completed_activities, key=lambda rating: rating[1], reverse=True) # sort by highest rating
                for item in sorted_activities[:5]: # prints top 5 rated activities
                    print(item[0] + " (" + str(item[1]) + ")")
                if completed_activities == []:
                    pass
                else:
                    turns += 1
            else:
                print(" ")
                print("Please check that your categories are the same as the possible categories.")
        if turns >= 2:
            print(" ")
            print("Now, select a number to get more information, do another search, or exit the program.")
            print("1. Get ALL of the activities related to your categories. ")
            print("2. Get additional information about one of the activities. ")
            print("3. Get 3 reviews about one of the activities. ")
            print("4. Get redirected to a URL to the Yelp page of one of the activities. ")
            print("5. See a scale of the ratings from all of the activities. ")
            print("6. See a chart of the hours of operations of all of the activities. ")
            print("7. Get reviews from a different website (TripAdvisor). ")
            print("8. Do a new search. ")
            print("9. Exit the program. ")
            number = input("Number: ")
            if number == "1": # get all the activities related to the keywords (sorted_activities)
                print(" ")
                for item in sorted_activities:
                    print(item[0] + " (" + str(item[1]) + ")")
            elif number == "2": # get additional information
                print("Type the name of the activity you are interested in. ")
                activity = input("Activity: ")
                if G.__contains__(activity):
                    print(" ")
                    print(activity)
                    print("Activity image:", G.nodes[activity]["image_url"])
                    print("Yelp url:", G.nodes[activity]["url"])
                    print("Number of reviews:", G.nodes[activity]["review_count"])
                    print("Rating:", G.nodes[activity]["rating"])
                    print("Address:", G.nodes[activity]["display_address"])
                    print("Phone number:", G.nodes[activity]["display_phone"])
                else:
                    print("Please check the spelling of your activity. ")
            elif number == "3": # get 3 reviews (API call)
                print("Type the name of the activity you are interested in. ")
                activity = input("Activity: ")
                if G.__contains__(activity):
                    print(" ")
                    reviews = get_business_review(API_Key, G.nodes[activity]["yelp_id"]) # API call
                    review_list = reviews["reviews"]
                    for i in review_list:
                        print(" ")
                        print("Review published: " + i["time_created"])
                        print(i["text"] + " (" + str(i["rating"]) + "/5)")
                        print("See full review at: " + i["url"])
                else:
                    print("Please check the spelling of your activity. ")
            elif number == "4": # get redirected to Yelp URL
                print("Type the name of the activity you are interested in. ")
                activity = input("Activity: ")
                if G.__contains__(activity):
                    print(" ")
                    print("Launching", activity, "in web browser...")
                    webbrowser.open(G.nodes[activity]["url"], new=1) # opens url in a new browser window
                else:
                    print("Please check the spelling of your activity. ")
            elif number == "5": # scale of ratings
                print(" ")
                fig = plt.figure() # initialize plot
                ax = fig.add_subplot(111)
                ax.set_xlim(-1,6)
                ax.set_ylim(-5,5)
                x = [0, 1, 2, 3, 4, 5]
                y = 0
                plt.hlines(y, x[0], x[-1])
                for i in x: # making vertical ticks
                    plt.vlines(i, y-0.5, y+0.5)
                    plt.text(i, y-1, str(i), verticalalignment='bottom')
                height = -0.5
                for i in sorted_activities: # plotting points with arrows and labels
                    intervals = 1/(len(sorted_activities)) # intervals between the points so they are not plotted on top of each other
                    plt.plot(i[1], y+height, 'ro', ms=5, mfc="r")
                    plt.annotate(i[0], (i[1], y+height), xytext=(i[1]-1,y+1+height*7), arrowprops=dict(facecolor="black"), horizontalalignment="right")
                    height += intervals
                plt.axis('off')
                plt.show()
            elif number == "6": # hours of operation (API call)
                print(" ")
                details_dict = {}
                for i in sorted_activities:
                    details = get_business(API_Key, G.nodes[i[0]]["yelp_id"]) # API call
                    details_dict[i[0]] = details
                columns = ("Activity", "Open Now?", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday") # table columns
                cell_data = [] # data for table
                for i in sorted_activities:
                    i_data = [i[0]] # data for each row (activity) that will be filled with each loop, starts with the activity name
                    if "hours" in details_dict[i[0]]: # if there are hours of operation
                        open_now = details_dict[i[0]]["hours"][0]["is_open_now"]
                        if open_now == False: # if it's not open now
                            i_data.append("No")
                        else: # if it is open now
                            i_data.append("Yes")
                        day_of_the_week = details_dict[i[0]]["hours"][0]["open"]
                        if day_of_the_week[0]["day"] == 0: # if there are hours for Monday
                            times = day_of_the_week[0]["start"] + "-" + day_of_the_week[0]["end"]
                            i_data.insert(2, times) # insert the hours at the second index of i_data (under the Monday column)
                            day_of_the_week.pop(0) # removes the first item in the list if it's Monday
                        else:
                            i_data.insert(2, "Closed") # otherwise, closed on Monday
                        if day_of_the_week != [] and day_of_the_week[0]["day"] == 1: # if there are still hours and hours for Tuesday
                            times = day_of_the_week[0]["start"] + "-" + day_of_the_week[0]["end"]
                            i_data.insert(3, times) # add to the Tuesday column
                            day_of_the_week.pop(0) # removes the first item in the list if it's Tuesday
                        else: # if there are no more hours or no hours for Tuesday
                            i_data.insert(3, "Closed")
                        if day_of_the_week != [] and day_of_the_week[0]["day"] == 2:
                            times = day_of_the_week[0]["start"] + "-" + day_of_the_week[0]["end"]
                            i_data.insert(4, times)
                            day_of_the_week.pop(0)
                        else:
                            i_data.insert(4, "Closed")
                        if day_of_the_week != [] and day_of_the_week[0]["day"] == 3:
                            times = day_of_the_week[0]["start"] + "-" + day_of_the_week[0]["end"]
                            i_data.insert(5, times)
                            day_of_the_week.pop(0)
                        else:
                            i_data.insert(5, "Closed")
                        if day_of_the_week != [] and day_of_the_week[0]["day"] == 4:
                            times = day_of_the_week[0]["start"] + "-" + day_of_the_week[0]["end"]
                            i_data.insert(6, times)
                            day_of_the_week.pop(0)
                        else:
                            i_data.insert(6, "Closed")
                        if day_of_the_week != [] and day_of_the_week[0]["day"] == 5:
                            times = day_of_the_week[0]["start"] + "-" + day_of_the_week[0]["end"]
                            i_data.insert(7, times)
                            day_of_the_week.pop(0)
                        else:
                            i_data.insert(7, "Closed")
                        if day_of_the_week != [] and day_of_the_week[0]["day"] == 6:
                            times = day_of_the_week[0]["start"] + "-" + day_of_the_week[0]["end"]
                            i_data.insert(8, times)
                        else:
                            i_data.insert(8, "Closed")
                    else: # if there are no hours for the activity
                        i_data.append("Yes") # for open now
                        i_data.append("Open")
                        i_data.append("All")
                        i_data.append("The")
                        i_data.append("Time")
                        i_data.append("So")
                        i_data.append("Come")
                        i_data.append("In!")
                    cell_data.append(i_data)
                fig, ax = plt.subplots() # initialize plot
                hours_table = plt.table(cellText=cell_data, colLabels=columns, loc='center')
                hours_table.auto_set_font_size(False)
                hours_table.set_fontsize(6)
                hours_table.scale(1.1, 1.1)
                column_numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8]
                hours_table.auto_set_column_width(col=column_numbers) # auto sizing the first column
                fig.tight_layout()
                plt.axis("off")
                plt.show()
            elif number == "7": # tripadvisor reviews (Scraping)
                print("Type the name of the activity you are interested in. ")
                activity = input("Activity: ")
                if G.__contains__(activity):
                    if activity in tripadvisor_dict:
                        print(" ")
                        print("Here's the website", tripadvisor_dict[activity])
                        URL = tripadvisor_dict[activity]
                        from bs4 import BeautifulSoup
                        import requests
                        print("Fetching reviews...")
                        header = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36","X-Requested-With": "XMLHttpRequest"}
                        r = requests.get(URL, headers = header)
                        soup = BeautifulSoup(r.text, 'html.parser')
                        print(" ")
                        overall_rating_text = soup.find('div', class_='biGQs _P fiohW hzzSG uuBRH').get_text() # overall rating
                        print("Overall rating:", overall_rating_text)
                        number_of_reviews_text = soup.find('div', class_='jVDab o W f u w GOdjs').find('span').get_text() # number of reviews
                        print("Number of reviews:", number_of_reviews_text)
                        all_reviews = soup.find('div', class_='LbPSX') # Review class
                        all_reviews_divs = all_reviews.find_all('div', recursive=False) # finding each review
                        for single in all_reviews_divs[0:3]: # the first 3 reviews
                            print(" ")
                            review_title_block = single.find('div', class_='biGQs _P fiohW qWPrE ncFvv fOtGX').find('a')
                            review_title = review_title_block.find('span', class_='yCeTE').get_text()
                            print(review_title)
                            review_date = single.find('div', class_='RpeCd').get_text()
                            print(review_date)
                            review_text = single.find('div', class_='biGQs _P pZUbB KxBGd').find('span').get_text()
                            print(review_text)
                    else:
                        print(" ")
                        print("I'm sorry. TripAdvisor does not have reviews for that activity. ")
                else:
                    print("Please check the spelling of your activity. ")
            elif number == "8": # do a new search
                print(" ")
                turns = 1 # resetting turns to go through first loop
            elif number == "9": # exit the program
                print("Thank you for using Ann Arbor Activities!.")
                break
            else:
                print("Please print a number from 1-9. ")