import requests
import json
import csv
from datetime import datetime
import osmnx as ox
import os
import copy
from shapely.geometry import box
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# ================================================================================================================================= #

def create_quadrants(place_name, num_divisions):
    """
    Function to generate valid quadrants within the boundaries of a given city.

    Parameters:
    - place_name (str): Name of the city to fetch the boundary for.
    - num_divisions (int): Number of divisions along both latitude and longitude 
      to create square quadrants.
    
    Returns:
    - quadr_val (list): List of tuples, each containing two tuples with low and high 
                         coordinates (latitude, longitude) for each valid quadrant.
    """
    # Get the geographical boundary of the city (polygon)
    city_boundary = ox.geocode_to_gdf(place_name)

    # Extract the geometry of the city's boundary polygon
    city_polygon = city_boundary.geometry.iloc[0]

    # Extract bounding box coordinates for the city
    minx, miny, maxx, maxy = city_polygon.bounds

    # Calculate the width and height of each quadrant
    delta_lat = (maxy - miny) / num_divisions
    delta_lon = (maxx - minx) / num_divisions

    # List to store valid quadrants
    quadr_val = []  # List to store the coordinates of valid quadrants

    # Generate quadrants and check if they are inside the city's polygon
    for i in range(num_divisions):
        for j in range(num_divisions):
            lat_sw = miny + i * delta_lat  # Latitude of the southwest corner
            lon_sw = minx + j * delta_lon  # Longitude of the southwest corner
            lat_ne = lat_sw + delta_lat    # Latitude of the northeast corner
            lon_ne = lon_sw + delta_lon   # Longitude of the northeast corner

            # Create a quadrant as a polygon
            quadrant = box(lon_sw, lat_sw, lon_ne, lat_ne)

            # Check if the quadrant intersects with the city boundary
            if city_polygon.intersects(quadrant):
                # Add coordinates (low, high) as a tuple to the quadr_val list
                quadr_val.append(((lat_sw, lon_sw), (lat_ne, lon_ne)))

    # Return the list of valid quadrants' coordinates
    return quadr_val

# ================================================================================================================================= #

def get_access_token(credentials_file='credentials.json', token_file='token.json', scopes=None):
    """
    Function to get the access token for Google Cloud API using OAuth 2.0.

    Parameters:
    - credentials_file (str): Path to the OAuth 2.0 credentials JSON file.
    - token_file (str): Path to the saved token file.
    - scopes (list): List of scopes required for the API access.

    Returns:
    - access_token (str): The OAuth 2.0 access token.
    """
    if scopes is None:
        scopes = ['https://www.googleapis.com/auth/cloud-platform']

    creds = None

    # Check if there are valid credentials stored in the token file
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scopes)

    # If there are no credentials or they are expired, perform the authentication process
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # Refresh expired credentials if possible
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, scopes)  # Use OAuth 2.0 credentials file
            creds = flow.run_local_server(port=0)  # Interactive authentication in the browser

        # Save the new credentials for future use
        with open(token_file, 'w') as token:
            token.write(creds.to_json())

    # Return the access token
    return creds.token

# ================================================================================================================================= #

def fetch_places_by_quadrant(url, headers, data):
    """
    Function to fetch all pages of results for a given query.
    This function handles pagination and accumulates results from multiple API requests.
    
    Args:
        url (str): The API endpoint.
        headers (dict): Headers for the API request, including authorization.
        data (dict): The request body containing query parameters.
    
    Returns:
        list: A list of places gathered from all pages.
    """
    places = []  # List to store all results (renamed from all_places)
    next_page_token = None  # Variable to track the next page

    # Loop to fetch all pages of results
    while True:
        if next_page_token:
            data["pageToken"] = next_page_token  # Add the nextPageToken for pagination

        # Send the API request
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            response_data = response.json()

            # Add the results from this page to the places list
            places.extend(response_data.get('places', []))

            # Check if there's a next page token
            next_page_token = response_data.get("nextPageToken")
            if not next_page_token:
                break  # No more pages, exit the loop
        else:
            print(f"Error: Status code {response.status_code}")
            print("Parâmetros da requisição com erro:")
            print(f"({data['locationRestriction']['rectangle']['low']['latitude']},{data['locationRestriction']['rectangle']['low']['longitude']}), ({data['locationRestriction']['rectangle']['high']['latitude']}, {data['locationRestriction']['rectangle']['high']['longitude']})")
            break  # Exit the loop on error

    return places  # Return the accumulated places

# ================================================================================================================================= #

def subdivide_quadrant(lat_sw, lon_sw, lat_ne, lon_ne, num_divisions):
    # Calculate the differences in latitude and longitude
    delta_lat = lat_ne - lat_sw
    delta_lon = lon_ne - lon_sw
    
    # Use the same number of divisions for both latitude and longitude
    divisions = num_divisions
    
    # List to store the coordinate pairs of smaller quadrants
    smaller_quadrants = []
    
    # Calculate the dimensions of each smaller quadrant
    width = delta_lon / divisions
    height = delta_lat / divisions
    
    # Generate the coordinates of the smaller quadrants
    for i in range(divisions):
        for j in range(divisions):
            # Calculate the southwest vertex (lat, lon)
            lat_sw_smaller = lat_sw + i * height
            lon_sw_smaller = lon_sw + j * width
            
            # Calculate the northeast vertex (lat, lon)
            lat_ne_smaller = lat_sw_smaller + height
            lon_ne_smaller = lon_sw_smaller + width
            
            # Add the coordinate pair to the result
            smaller_quadrants.append(((lat_sw_smaller, lon_sw_smaller), (lat_ne_smaller, lon_ne_smaller)))
    
    return smaller_quadrants

# ================================================================================================================================= #

def save_results_to_json(data):
    # Ensure the 'results' directory exists
    if not os.path.exists('results'):
        os.makedirs('results')
    
    # Get the current date and time in the USA format (MM_DD_YYYY_HH_mm_ss)
    current_time = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
    
    # Define the filename
    filename = f"results/nyc_restaurants_{current_time}.json"
    
    # Save the data to the file in JSON format
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    
    print(f"Results saved to {filename}")

# ================================================================================================================================= #

def flatten(d, parent_key='', sep='.'):
    """
    Recursively flattens a nested dictionary.
    Example: {'location': {'lat': 40.7128, 'lng': -74.0060}} becomes {'location.lat': 40.7128, 'location.lng': -74.0060}
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
    
    # ================================================================================================================================= #

def save_results_to_csv(data):
    # Ensure the 'results' directory exists
    if not os.path.exists('results'):
        os.makedirs('results')
    
    # Define the filename for the CSV file
    filename = f"results/nyc_restaurants_{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.csv"
    
    # Determine fieldnames dynamically based on the first entry in the data
    # Flatten the first 'place' to get all possible keys for the header
    if data:
        flat_place = flatten(data[0])  # You should have a flatten function here
        fieldnames = list(flat_place.keys())  # Extract all keys as fieldnames
    else:
        fieldnames = []

    # Open the file in write mode
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        # Create a CSV writer object
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write the header (column names)
        writer.writeheader()
        
        # Write the rows (data)
        for place in data:
            # Flatten the place to get all the keys
            flat_place = flatten(place)
            writer.writerow(flat_place)
    
    print(f"Results saved to {filename}")

# ================================================================================================================================= #

def process_quadrant(sw, ne, data_template, url, headers, request_count=0):
    """
    Recursive function to process a quadrant and fetch places.
    If the result hits the API limit (60), the quadrant is subdivided and queried again.

    Args:
        sw (tuple): (lat, lon) of the southwest corner.
        ne (tuple): (lat, lon) of the northeast corner.
        data_template (dict): base API request body.
        url (str): API endpoint.
        headers (dict): request headers.
        request_count (int): current count of requests made.
        depth (int): recursion depth (for debug/logging).
        max_depth (int): maximum allowed depth for recursion.

    Returns:
        tuple: (all_places_found, updated_request_count)
    """
    # Copy the data template to avoid mutation
    data = copy.deepcopy(data_template)
    data['locationRestriction']['rectangle']['low']['latitude'] = sw[0]
    data['locationRestriction']['rectangle']['low']['longitude'] = sw[1]
    data['locationRestriction']['rectangle']['high']['latitude'] = ne[0]
    data['locationRestriction']['rectangle']['high']['longitude'] = ne[1]
    data['pageToken'] = None  # Ensure fresh request

    # Fetch results
    places = fetch_places_by_quadrant(url, headers=headers, data=data)
    print(f"REQUEST {request_count}: ({sw[0]}, {sw[1]}) - ({ne[0]}, {ne[1]}) → {len(places)} places")

    request_count += 1

    # If results are likely truncated, recurse instead of saving
    if len(places) >= 60:
        print(f"SUBDIVIDIU O QUANDRANTE ({sw[0]}, {sw[1]}),({ne[0]}, {ne[1]})-------------------------------------------------------")
        all_found = []
        smaller_quadrants = subdivide_quadrant(sw[0], sw[1], ne[0], ne[1], num_divisions=3)
        for sq in smaller_quadrants:
            results, request_count = process_quadrant(
                sq[0], sq[1], data_template, url, headers,
                request_count=request_count
            )
            all_found.extend(results)
            print(f"FECHOU A SUBDIVISÃO----------------------------------------------------------------------------------------------")
    else:
        all_found = places

    return all_found, request_count

# ================================================================================================================================= #