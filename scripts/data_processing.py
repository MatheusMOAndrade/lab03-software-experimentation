import pandas as pd
import csv
from datetime import datetime

# Lista para armazenar os dados lidos do arquivo CSV
data_rows = []

# Abrir o arquivo CSV e ler linha por linha
with open('C:/Codes/lab03-software-experimentation/processed_data_pullRequests.csv', 'r', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=';')
    header = next(csvreader)  # Ler o cabeçalho
    
    for row in csvreader:
        try:
            # Tentar converter as datas para o tipo datetime
            row[4] = pd.to_datetime(row[4])  # Created At
            row[5] = pd.to_datetime(row[5])  # Merged At
            row[6] = pd.to_datetime(row[6])  # Closed At
            
            # Calcular o intervalo de dias entre a criação e a última atividade
            last_activity = max(row[5], row[6]) if not pd.isnull(row[5]) and not pd.isnull(row[6]) else row[5] if not pd.isnull(row[5]) else row[6]
            analysis_time = (last_activity - row[4]).days
            
            # Adicionar a linha processada à lista
            row.append(analysis_time)
            data_rows.append(row)
        except Exception as e:
            print(f"Erro ao processar linha: {e}")
            continue

# Criar DataFrame a partir dos dados processados
data = pd.DataFrame(data_rows, columns=header + ['Analysis Time'])

# Remover linhas com valores nulos
data = data.dropna()

# Agrupar os dados por Owner e Repository name e calcular as métricas solicitadas
grouped_data = data.groupby(['Owner', 'Repository name']).agg({
    'Pull Request Number': 'count',
    'Total reviews': 'sum',
    'Total files': 'sum',
    'Analysis Time': 'mean',
    'Body Text': lambda x: sum(len(str(text)) for text in x),
    'Comments': 'sum'
}).reset_index()

# Renomear as colunas
grouped_data.columns = ['Owner', 'Repository name', 'Total PRs', 'Total reviews', 
                        'Total files', 'Analysis time', 'Description', 'Interactions']

# Salvar os dados processados em um novo arquivo CSV
grouped_data.to_csv('processed_data_summary.csv', index=False)

print("Dados processados e salvos com sucesso!")