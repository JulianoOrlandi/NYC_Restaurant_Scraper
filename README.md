# **NEW YORK CITY RESTAURANT SCRAPER**

### **Author: Juliano Orlandi**

<br>

⚠️ Click [here](LEIAME.md) for the portuguese version


### **Description:**

This script implements automated data retrieval of restaurants in New York City, using Google's [Places API (New)](https://developers.google.com/maps/documentation/places/web-service/op-overview). The ultimate goal is to build a database containing information such as address, phone number, business hours, customer reviews, and more.

The main code can be found in the file [nyc_restaurant_scraper.py](nyc_restaurant_scraper.py). However, it relies on a set of helper functions available in the file [helpers.py](helpers.py). For educational purposes, the following explanation accompanies the structure of the main code. As the helper functions appear, their respective implementations in the supporting file will be explained.

---

<br>

### **1. Imports**

In the file [nyc_restaurant_scraper.py](nyc_restaurant_scraper.py), the functions defined in the file [helpers.py](helpers.py) are primarily imported. The dependencies used are as follows:

| Requirement              | Version |
|--------------------------|---------|
| **Python**               | 3.11.9  |
| **google_auth_oauthlib** | 1.2.1   |
| **osmnx**                | 2.0.2   |
| **pandas**               | 2.2.3   |
| **protobuf**             | 6.30.2  |
| **Requests**             | 2.32.3  |
| **Shapely**              | 2.1.0   |


---
<br>

### **2. Get Google's API access_token**

Before using the `get_access_token()` function, which is present in the only line of code in this section, you need to create a project in the [Google Cloud Console](https://console.cloud.google.com/), enable the use of the [Places API (New)](https://developers.google.com/maps/documentation/places/web-service/op-overview), configure the OAuth consent screen, generate the appropriate credentials, and download the `credentials.json` file. Below is the step-by-step process for this. However, before proceeding, it is important to make it clear:

⚠️ **The use of the Places API (New) is paid!** You will be charged to your credit card based on the number of requests made by your application. For more details on costs, refer to [Item 4 below](#4-preparing-the-parameters-for-the-api-request) or [the official API documentation](https://mapsplatform.google.com/intl/en-US/pricing/).

#### **2.1. Create a project in Google Cloud Console:**
- Go to the [Google Cloud Console](https://console.cloud.google.com/);
- Click on "Select a project" at the top of the screen;
- Click on "New Project";
- Fill in the `Project Name`;
- Click `Create`.

#### **2.2. Enable Places API (New):**
- In the navigation menu (top-left corner), click `APIs & Services > Library`;
- In the search bar, search for `Places API (New)`;
- Click on the corresponding option;
- Enable the API by clicking `Enable`;
- Click `Go to Google Cloud Platform`;
- Click `Maybe later`;

#### **2.3. Configure the OAuth consent screen:**
- In the navigation menu (top-left corner), click `APIs & Services > OAuth consent screen`;
- Click `Get started`;
- Fill in the `App Name`;
- Choose your email address in `User support email`;
- Choose `external` in `Audience`;
- Enter your email address in `Contact information`;
- Agree to the [Google API Services: User Data Policy](https://developers.google.com/terms/api-services-user-data-policy) under `Finish`;
- Click `Create`.

#### **2.3. Generate credentials:**
- In the navigation menu (top-left corner), click `APIs & Services > Credentials`;
- Click `Create credentials > OAuth client ID`;
- In `Application Type`, choose `Desktop App`;
- Fill in the `Name`;
- Click `Create`;
- In the `OAuth client created` screen, click `Download JSON`;
- Save the downloaded file as `credentials.json` at the root of your project.

<br>

The `get_access_token()` function takes three parameters:
- `credentials_file` (str): Path to the JSON file with the OAuth 2.0 credentials;
- `token_file` (str): Path where the generated token will be stored for future use;
- `scopes` (list): List of permissions (scopes) the application will need to access the Google API.

If the `scopes` parameter is not provided, the default value will be the broadest scope (`'https://www.googleapis.com/auth/cloud-platform'`), allowing access to the Google Cloud platform. The function then checks if a valid token file already exists. If it does, the token is loaded and returned. If there is no valid token or if the token is expired, the authentication process is initiated using the credentials from the `credentials.json` file. The obtained token is saved in `token.json` for future use and returned to the `access_token` variable in [nyc_restaurant_scraper.py](nyc_restaurant_scraper.py).

---
<br>

### **3. Subdividing the city into quadrants to narrow down the search area**

The goal of this part of the code is to generate a list of tuples, where each item represents a valid geographical quadrant within the city limits. Each tuple contains two sub-tuples, each with two values: latitude and longitude. The first sub-tuple corresponds to the southwest vertex of the quadrant and the second to the northeast vertex. These values will be used to define the areas in which API requests will be made — more on this in [item 4](#4-preparing-the-parameters-for-the-api-request).

An example of the return format would be: `[((40.7, -74.0), (40.72, -73.98)), ((40.72, -74.0), (40.74, -73.98)), ...]`.

The city name is passed as a string to a variable called `place_name`. It should follow the format `"City, State (or Region), Country"`, as this helps the internal geocoding service of the `OSMnx` library: [**Nominatim**](https://nominatim.openstreetmap.org/) (belonging to `OpenStreetMap`). In addition to `place_name`, an integer is passed to the variable `num_divisions`, which defines how many parts (or quadrants) each side of the city map will be divided into. In the code, a 30 x 30 division was used, totaling 900 quadrants.

In the first lines of the `create_quadrants()` function, the code uses the `OSMnx` library to get the geographical boundaries of the city as a polygon (`city_polygon`). Then, it calculates the dimensions of each quadrant based on the value of `num_divisions` and starts a loop to generate the coordinates (latitude and longitude) of the southwest and northeast vertices of each quadrant that the city map will be divided into. Before adding these coordinates to the list `quadr_val` — which will be returned at the end of the function — the code checks if the quadrant intersects with the city's polygon boundaries. If there is an intersection, the quadrant is included in the list; otherwise, it is discarded.

<div style="text-align: center;">
  <img src="images/nyc_quadrants.png" alt="NYC Quadrants" width="500"/>
</div>

<br>

The reason why it is necessary to divide the city's map into several quadrants is directly related to how the [Places API (New)](https://developers.google.com/maps/documentation/places/web-service/op-overview) works. Each request made to the API returns a maximum of **20** items within the specified area. If there are more results, the response will also include a value in the `pageToken` variable. This token allows a new request to be made to fetch the subsequent items. If there are still results, the API returns a new `pageToken`, allowing a third and final call. The problem is that there is a limit of three pages per request, meaning that a maximum of **60** items can be returned per queried area. For example: if the request is made using coordinates that cover the entire city of New York, the response will contain only **20** initial results, plus two additional pages with up to **20** items each — totaling just **60** locations. This is insufficient to capture all the restaurants in the city. This is why dividing the area into quadrants is crucial: it reduces the area of each request, increasing the chance of retrieving all items present in each region. It is also worth noting that the rectangular map used for division can include areas outside the city — such as neighboring regions or even parts of the ocean. Therefore, the `create_quadrants()` function checks if each generated quadrant intersects with the actual boundaries of the city's polygon. Only valid quadrants are included in the search, avoiding unnecessary requests.

---
<br>

### **4. Preparing the parameters for the API request**

After generating the valid quadrants for querying, the next step is to configure the parameters that will be used in requests to the [Places API (New)](https://developers.google.com/maps/documentation/places/web-service/op-overview). This configuration is done through two variables: `url` and `headers`, which represent, respectively, the **API endpoint** and the **HTTP headers** necessary for authentication and request formatting.

The endpoint `https://places.googleapis.com/v1/places:searchText` allows searching for places based on textual terms, such as "restaurant", "pharmacy", "supermarket", etc. This is the same type of search you would perform manually in the **Google Maps** search box. The API response returns places matching the search term, considering the geographic area defined in the request parameters. Since the goal of this script is to obtain data for **all** establishments of a given category, it is recommended to choose the search term from the types listed in the API's documentation. The full list can be found in [Table A](https://developers.google.com/maps/documentation/places/web-service/place-types).

The `headers` variable defines the **HTTP headers** that accompany each request to the API, which are essential to ensure both authentication and proper data formatting. The `Authorization` field uses the access token generated earlier by the `get_access_token()` function, in the `Bearer` format, which is the standard adopted by the OAuth 2.0 protocol. The `Content-Type` field is set to "application/json", indicating that the request body will be sent in JSON format, as required by the [Places API (New)](https://developers.google.com/maps/documentation/places/web-service/op-overview). The `X-Goog-FieldMask` field specifies exactly which fields you want to receive in the response: name, phone, address, user ratings, etc. The full list of fields is available in the [Text Search documentation](https://developers.google.com/maps/documentation/places/web-service/text-search).

⚠️ It is important to emphasize that the possible response fields from the API are organized by **Google** into different categories called `SKUs` (**Stock Keeping Units**), which function as billing units. Each `SKU` corresponds to a set of specific features or information provided by the API. The use of each one has an associated cost, and the prices vary depending on the complexity and value of the data provided. This means that the more fields are included in the `X-Goog-FieldMask` parameter, the higher the cost per request.

⚠️ An example helps to clarify. If a request is made with the fields `places.displayName` and `places.formattedAddress`, which are associated with the `Text Search Pro SKU`, the cost today (04/18/2025) is **$0.032** per request — since, according to the [official pricing table](https://mapsplatform.google.com/intl/en-US/pricing/), 1000 calls to this SKU cost **$32**. On the other hand, if a request is made with the fields `places.priceRange` and `places.rating`, linked to the `Text Search Enterprise SKU`, the cost is **$0.035**, as 1000 calls to this SKU cost **$35**.

⚠️ Now — and here is the most important point —, if the same request includes the **four fields mentioned above, it will trigger two SKUs simultaneously**. In this case, the total cost of the call will be **$0.067**: **$0.032** for the fields from the `Text Search Pro SKU` plus **$0.035** from the `Text Search Enterprise SKU`. It is crucial to be aware of this billing dynamics, as with a high volume of requests, the costs can scale quite significantly. Therefore, before defining the desired fields in the response, it is highly recommended to consult the official documentation and estimate the costs based on the expected volume of calls.

The `data_template` variable serves as a template for constructing the body of the requests sent to the [Places API (New)](https://developers.google.com/maps/documentation/places/web-service/op-overview). It contains the parameters that control the search. The `textQuery` field specifies the term of interest — for example, "restaurant". As discussed above, it is recommended to choose it from the types listed in the [API documentation](https://developers.google.com/maps/documentation/places/web-service/place-types). The `locationRestriction` field defines the geographic area where the search should occur. It is structured as a rectangle (`rectangle`) delimited by two pairs of geographic coordinates. The `low` key represents the southwest vertex, and the `high` key represents the northeast vertex, both containing explicit values for `latitude` and `longitude`. Finally, the `pageToken` field is used to control the pagination of requests and allows access to the additional results of the search that were not included in the response.

There are also two more variables created in this part of the code: `all_places` and `request_count`. The first is a list that will store the content returned by the requests. The second is an `integer` used to track the number of requests made to the [Places API (New)](https://developers.google.com/maps/documentation/places/web-service/op-overview).

---
<br>


### **5. Loop through the quadrants to perform the search using the process_quadrant function**

The script now enters the main execution step: iterating over the valid quadrants of the city and making requests to the API. This operation is performed with a `for` loop, which iterates through each quadrant previously generated by the `create_quadrants()` function. For each item in the `quadrants` list, the code calls the `process_quadrant()` function, which receives the following parameters:

- `sw` (tuple): (latitude, longitude) of the southwest corner;
- `ne` (tuple): (latitude, longitude) of the northeast corner;
- `data_template` (dict): the template for constructing the body of the requests;
- `url` (str): the API endpoint;
- `headers` (dict): the HTTP headers that accompany the request;
- `request_count` (int): the variable to control the number of requests made.

The `process_quadrant()` function is responsible for making the API request and returning the results found within a given quadrant. First, it fills in the latitude and longitude values for the `low` and `high` keys of the `locationRestriction` parameter in `data_template`, using the `sw` and `ne` tuples. It then passes this variable along with `headers` and `url` as the parameters to the `fetch_places_by_quadrant()` function. This function actually makes the API call and returns the results in a list called `places`. Additionally, it automatically manages the API pagination through the `next_page_token` variable, ensuring access to as many items as possible within the queried geographic area.

After obtaining the list of results, the `process_quadrant()` function checks if it contains exactly 60 items — the maximum number that can be returned by the API in a single sequence of requests. If this happens, the code assumes that the data has been truncated, which indicates that there are more establishments in that area than could be obtained with just three pages. To work around this limitation, the function calls `subdivide_quadrant()`, passing the coordinates of the southwest and northeast corners of the original quadrant, as well as the number of divisions desired. This function divides the original quadrant into smaller subareas — in this case, nine subquadrants — which are returned as a list of coordinates. The `process_quadrant()` function then iterates over each of these subquadrants, calling itself recursively to make new requests within these smaller regions. This approach ensures that the limitation of the [Places API (New)](https://developers.google.com/maps/documentation/places/web-service/op-overview) on the maximum number of items per area is efficiently bypassed, allowing the script to retrieve all establishments of a given category, even in densely populated regions.

Finally, the results collected in each iteration — including those from subquadrants, if any — are aggregated into the `all_places` list, which consolidates all the establishments found throughout the script's execution.

---
<br>

### **6. Save the results to a JSON file after completing the search**

After completing the data collection, the results are saved using the `save_results_to_json()` function. It takes the `all_places` list and writes the content to a `.json` file inside the `results` folder. The filename includes the date and time of the execution to prevent overwriting and keep the history organized.
