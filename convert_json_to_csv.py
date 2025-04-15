import pandas as pd
import json

# Caminho para o seu arquivo JSON
file_path = 'results/nyc_restaurants_04_11_2025_17_03_49.json'

# Abrindo e carregando o conteúdo do arquivo JSON
with open(file_path, 'r') as file:
    data = json.load(file)

# Normalizando os dados para criar um DataFrame
df = pd.json_normalize(data, sep='_')

# Salvando o DataFrame como CSV
df.to_csv('business_data.csv', index=False)

print("CSV file 'business_data.csv' has been created successfully.")
