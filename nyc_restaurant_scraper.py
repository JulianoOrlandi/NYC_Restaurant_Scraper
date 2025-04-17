# 1. Imports
from helpers import (
    create_quadrants,
    get_access_token,
    process_quadrant,
    save_results_to_json,
    save_results_to_csv
)
from datetime import datetime

# 2. Get Google's API access_token
access_token = get_access_token()

# 3. Subdividing the city into quadrants to narrow down the search area
place_name = "New York, New York, USA"
num_divisions = 30
quadrants = create_quadrants(place_name, num_divisions)

# 4.1 Preparing the parameters for the API request
url = "https://places.googleapis.com/v1/places:searchText"

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
    "X-Goog-FieldMask": "places.accessibilityOptions,places.addressComponents,places.adrFormatAddress,places.businessStatus,places.containingPlaces,places.displayName,places.formattedAddress,places.googleMapsUri,places.iconBackgroundColor,places.iconMaskBaseUri,places.location,places.photos,places.plusCode,places.postalAddress,places.primaryType,places.primaryTypeDisplayName,places.pureServiceAreaBusiness,places.shortFormattedAddress,places.subDestinations,places.types,places.utcOffsetMinutes,places.viewport,places.currentOpeningHours,places.currentSecondaryOpeningHours,places.internationalPhoneNumber,places.nationalPhoneNumber,places.priceLevel,places.priceRange,places.rating,places.regularOpeningHours,places.regularSecondaryOpeningHours,places.userRatingCount,places.websiteUri,nextPageToken"
}

# Request body parameters
data_template = {
    "textQuery": "restaurant",  # Search for 'restaurant' in the specified area
    "locationRestriction": {
        "rectangle": {
            "low": {
                "latitude": 0.0,
                "longitude": -1.0
            },
            "high": {
                "latitude": 0.0,
                "longitude": -1.0
            },
        }
    },
    "pageToken": None,  # Used for pagination, initial value is None
}

# List to store all the results from the API
all_places = []

# Counter for number of API requests
request_count = 0

# 5. Loop through the quadrants to perform the search using the process_quadrant function
for i, quadrant in enumerate(quadrants):
    
    # Call the process_quadrant function to handle subdivision and fetching results
    places, request_count = process_quadrant(
        sw=quadrant[0], 
        ne=quadrant[1], 
        data_template=data_template, 
        url=url, 
        headers=headers, 
        request_count=request_count
    )
    
    # Add the found places to the overall list
    all_places.extend(places)

# 6. Save the results to a JSON file after completing the search
save_results_to_json(all_places)

# Print the total number of requests made
print(f"Total number of requests: {request_count}")