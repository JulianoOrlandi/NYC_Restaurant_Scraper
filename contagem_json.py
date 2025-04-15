import json

def count_places_in_json(json_file):
    try:
        # Open the JSON file and load its content
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Assuming the data is a list of places
        if isinstance(data, list):
            print(f"Total number of places saved: {len(data)}")
        else:
            print("The JSON data is not a list of places.")
    except FileNotFoundError:
        print(f"Error: The file {json_file} does not exist.")
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from the file {json_file}.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Example usage
json_file = "results/nyc_restaurants_04_11_2025_17_03_49.json"  # Replace with your actual JSON file path
count_places_in_json(json_file)
