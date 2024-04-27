import pandas as pd
import csv
from datetime import datetime

def try_parse_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

def convert_to_int(value):
    if isinstance(value, int):
        return value
    elif isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return 0
    else:
        return 0

data_rows = []

with open('C:/Codes/lab03-software-experimentation/processed_data_pullRequests.csv', 'r', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=';')
    header = next(csvreader)
    
    for row in csvreader:
        try:
            
            row[8] = try_parse_int(row[8])  # Total files
            row[11] = try_parse_int(row[11])  # Total reviews
            row[14] = try_parse_int(row[14])  # Comments
            
            row[4] = pd.to_datetime(row[4])  # Created At
            row[5] = pd.to_datetime(row[5])  # Merged At
            row[6] = pd.to_datetime(row[6])  # Closed At
            
            last_activity = max(row[5], row[6]) if not pd.isnull(row[5]) and not pd.isnull(row[6]) else row[5] if not pd.isnull(row[5]) else row[6]
            analysis_time = (last_activity - row[4]).days
            
            row.append(analysis_time)
            data_rows.append(row)
        except Exception as e:
            print(f"Erro ao processar linha: {e}")
            continue

data = pd.DataFrame(data_rows, columns=header + ['Analysis Time'])

data = data.dropna()

grouped_data = data.groupby(['Owner', 'Repository name']).agg({
    'Pull Request Number': 'count',
    'Total reviews': lambda x: sum(convert_to_int(value) for value in x),
    'Total files': lambda x: sum(convert_to_int(value) for value in x),
    'Analysis Time': 'mean',
    'Body Text': lambda x: sum(len(str(text)) for text in x),
    'Comments': lambda x: sum(convert_to_int(value) for value in x)
}).reset_index()

grouped_data.columns = ['Owner', 'Repository name', 'Total PRs', 'Total reviews', 
                        'Total files', 'Analysis time', 'Description', 'Interactions']

grouped_data.to_csv('processed_data_summary.csv', index=False)

print("Dados processados e salvos com sucesso!")
