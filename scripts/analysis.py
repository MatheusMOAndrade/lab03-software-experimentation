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

def days_difference(df, column_start, column_1, column_2):
    list_merge_at = []
    list_closed_at = []
    for _, row in df.iterrows():
        created_at = datetime.fromisoformat(row[column_start])
        
        if isinstance(row[column_1], str):
            merged_at = datetime.fromisoformat(row[column_1])
            merge_difference = abs(merged_at - created_at).days
        else:
            merge_difference = None
        list_merge_at.append(merge_difference)
        
        if isinstance(row[column_2], str):
            closed_at = datetime.fromisoformat(row[column_2])
            closed_difference = abs(closed_at - created_at).days
        else:
            closed_difference = None
        list_closed_at.append(closed_difference)
    
    return list_merge_at, list_closed_at

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
essential_columns = ['Repository name', 'Title', 'Created At']
data = remove_missing_values(data, essential_columns)

# Preencher valores nulos em 'Merged At' e 'Closed At' com a data de criação
data['Merged At'] = data['Merged At'].fillna(data['Created At'])
data['Closed At'] = data['Closed At'].fillna(data['Created At'])

# Diferença entre eventos: criação do PR, merge e fechamento
merge_diff, closed_diff = days_difference(data, 'Created At', 'Merged At', 'Closed At')
data['Merge At'] = merge_diff
data['Closed At'] = closed_diff

data = calculate_text_length(data, 'Body Text')

# RQ 01. Qual a relação entre o número de PRs mergeados e fechados e o total de arquivos?
# Gráfico de dispersão do número de PRs mergeados em relação ao total de arquivos
scatter_plot(data, 'Merged At', 'Total files', title='Número de PRs Mergeados x Total de Arquivos')

# Gráfico de dispersão do número de PRs fechados em relação ao total de arquivos
scatter_plot(data, 'Closed At', 'Total files', title='Número de PRs Fechados x Total de Arquivos')

# RQ 02. Qual a relação entre o número de PRs mergeados e fechados e o tempo de análise dos PRs?
# Tempo de análise: intervalo entre a criação do PR e a última atividade (fechamento ou merge)
# Calculando o tempo de análise para os PRs
merge_diff, closed_diff = days_difference(data, 'Created At', 'Merged At', 'Closed At')
data['Merge Analysis Time'] = merge_diff
data['Closed Analysis Time'] = closed_diff

# Gráfico de dispersão do número de PRs mergeados em relação ao tempo de análise
scatter_plot(data, 'Merged At', 'Merge Analysis Time', title='Número de PRs Mergeados x Tempo de Análise')

# Gráfico de dispersão do número de PRs fechados em relação ao tempo de análise
scatter_plot(data, 'Closed At', 'Closed Analysis Time', title='Número de PRs Fechados x Tempo de Análise')

# RQ 03. Qual a relação entre o número de PRs mergeados e fechados e o número de caracteres do corpo de descrição do PR?
# Gráfico de dispersão do número de PRs mergeados em relação ao tamanho do texto da descrição
scatter_plot(data, 'Merged At', 'Text Length', title='Número de PRs Mergeados x Tamanho do Texto da Descrição')

# Gráfico de dispersão do número de PRs fechados em relação ao tamanho do texto da descrição
scatter_plot(data, 'Closed At', 'Text Length', title='Número de PRs Fechados x Tamanho do Texto da Descrição')

# RQ 04. Qual a relação entre o número de PRs mergeados e fechados e o número de comentários?
# Gráfico de dispersão do número de PRs mergeados em relação ao número de comentários
scatter_plot(data, 'Merged At', 'Comments', title='Número de PRs Mergeados x Número de Comentários')

# Gráfico de dispersão do número de PRs fechados em relação ao número de comentários
scatter_plot(data, 'Closed At', 'Comments', title='Número de PRs Fechados x Número de Comentários')

# B. Número de Revisões:
# RQ 05. Qual a relação entre o tamanho dos PRs e o número de revisões realizadas?
# Gráfico de dispersão do tamanho dos PRs em relação ao número de revisões
scatter_plot(data, 'Total files', 'Total reviews', title='Tamanho dos PRs x Número de Revisões')

# RQ 06. Qual a relação entre o tempo de análise dos PRs e o número de revisões realizadas?
# Gráfico de dispersão do tempo de análise em relação ao número de revisões
scatter_plot(data, 'Merge Analysis Time', 'Total reviews', title='Tempo de Análise - Merged x Número de Revisões')
scatter_plot(data, 'Closed Analysis Time', 'Total reviews', title='Tempo de Análise - Closed x Número de Revisões')

# RQ 07. Qual a relação entre a descrição dos PRs e o número de revisões realizadas?
# Gráfico de dispersão do tamanho do texto da descrição em relação ao número de revisões
scatter_plot(data, 'Text Length', 'Total reviews', title='Tamanho do Texto x Número de Revisões')

# RQ 08. Qual a relação entre as interações nos PRs e o número de revisões realizadas?
# Gráfico de dispersão do número de participantes em relação ao número de revisões
scatter_plot(data, 'Participants', 'Total reviews', title='Participantes x Número de Revisões')

# Gráfico de dispersão do número de comentários em relação ao número de revisões
scatter_plot(data, 'Comments', 'Total reviews', title='Comentários x Número de Revisões')


# Calculando a correlação de Spearman
correlation_data = data[['Text Length', 'Merge Analysis Time', 'Participants', 'Comments', 'Total reviews']]
correlation_matrix = correlation_data.corr(method='spearman')

correlation_matrix.to_csv('correlation_matrix.csv')

sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Matriz de Correlação (Spearman)')
plt.show()
