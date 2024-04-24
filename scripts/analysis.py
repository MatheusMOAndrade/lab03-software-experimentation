import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def load_data(file_path, separator=';'):
    data = pd.read_csv(file_path, sep=separator)
    return data

def remove_missing_values(data, columns):
    data = data.dropna(subset=columns)
    return data

def calculate_text_length(data, column):
    data['Text Length'] = data[column].astype(str).apply(len)
    return data

def days_difference(df, column_start, column_end):
    list_closed_at = []
    for _, row in df.iterrows():
        created_at = datetime.fromisoformat(row[column_start])
        closed_at = datetime.fromisoformat(row[column_end])
        closed_difference = abs(closed_at - created_at).days
        list_closed_at.append(closed_difference)
    
    return list_closed_at

def scatter_plot(df, x_column, y_column, x_label=None, y_label=None, title=None, x_range=None, y_range=None):
    plt.figure(figsize=(10, 4))
    plt.scatter(df[x_column], df[y_column])
    plt.xlabel(x_label if x_label else x_column)
    plt.ylabel(y_label if y_label else y_column)
    plt.title(title)
    if x_range:
        plt.xlim(x_range)
    if y_range:
        plt.ylim(y_range)
    plt.grid(True)
    plt.show()

# Carregar o arquivo CSV
file_path = 'C:/Codes/lab03-software-experimentation/processed_data_pullRequests.csv'
data = load_data(file_path)

# Verificar as primeiras linhas e informações do DataFrame
data.head()
data.info()

# Verificar valores ausentes por coluna
data.isna().sum()

# Remover linhas com valores ausentes em colunas essenciais
essential_columns = ['Repository name', 'Title', 'Pull Request Created At']
data = remove_missing_values(data, essential_columns)

# Diferença entre eventos: criação do PR e fechamento
closed_diff = days_difference(data, 'Pull Request Created At', 'Pull Request Closed At')
data['Closed At'] = closed_diff

data = calculate_text_length(data, 'Body Text')

# A. Feedback Final das Revisões (Status do PR):
# RQ 01. Qual a relação entre o tamanho dos PRs e o feedback final das revisões?
scatter_plot(data, 'Total files', 'Review decision', title='Tamanho dos PRs x Feedback das Revisões')

# RQ 02. Qual a relação entre o tempo de análise dos PRs e o feedback final das revisões?
scatter_plot(data, 'Closed At', 'Review decision', title='Tempo de Análise x Feedback das Revisões')

# RQ 03. Qual a relação entre a descrição dos PRs e o feedback final das revisões?
scatter_plot(data, 'Text Length', 'Review decision', title='Tamanho do Texto x Feedback das Revisões')

# RQ 04. Qual a relação entre as interações nos PRs e o feedback final das revisões?
scatter_plot(data, 'Participants', 'Review decision', title='Participantes x Feedback das Revisões')
scatter_plot(data, 'Comments', 'Review decision', title='Comentários x Feedback das Revisões')
scatter_plot(data, 'Interações', 'Review decision', title='Interações x Feedback das Revisões')

# B. Número de Revisões:
# RQ 05. Qual a relação entre o tamanho dos PRs e o número de revisões realizadas?
scatter_plot(data, 'Total files', 'Total reviews', title='Tamanho dos PRs x Número de Revisões')

# RQ 06. Qual a relação entre o tempo de análise dos PRs e o número de revisões realizadas?
scatter_plot(data, 'Closed At', 'Total reviews', title='Tempo de Análise x Número de Revisões')

# RQ 07. Qual a relação entre a descrição dos PRs e o número de revisões realizadas?
scatter_plot(data, 'Text Length', 'Total reviews', title='Tamanho do Texto x Número de Revisões')

# RQ 08. Qual a relação entre as interações nos PRs e o número de revisões realizadas?
scatter_plot(data, 'Participants', 'Total reviews', title='Participantes x Número de Revisões')
scatter_plot(data, 'Comments', 'Total reviews', title='Comentários x Número de Revisões')
scatter_plot(data, 'Interações', 'Total reviews', title='Interações x Número de Revisões')

# Calculando a correlação de Spearman
correlation_data = data[['Text Length', 'Closed At', 'Participants', 'Comments', 'Interações', 'Review decision']]
correlation_matrix = correlation_data.corr(method='spearman')

correlation_matrix.to_csv('correlation_matrix.csv')

sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Matriz de Correlação (Spearman)')
plt.show()
