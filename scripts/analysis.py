import pandas as pd
import matplotlib.pyplot as plt
from math import ceil

def load_data(file_path, separator=','):
    data = pd.read_csv(file_path, sep=separator)
    return data

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

file_path = 'C:/Codes/lab03-software-experimentation/processed_data_summary.csv'
data = load_data(file_path)

data['Analysis time'] = data['Analysis time'].apply(lambda x: ceil(x))

print(data.head())
print(data.info())

# RQ 01. Qual a relação entre o número de PRs mergeados e fechados e o total de arquivos?
scatter_plot(data, 'Total PRs', 'Total files', title='Número de PRs (Mergeados e fechados) x Total de arquivos')

# RQ 02. Qual a relação entre o número de PRs mergeados e fechados e o tempo de análise dos PRs?
scatter_plot(data, 'Total PRs', 'Analysis time', title='Número de PRs (Mergeados e fechados) x Tempo médio de análise [Dias]')

# RQ 03. Qual a relação entre o número de PRs mergeados e fechados e o número de caracteres do corpo de descrição do PR?
scatter_plot(data, 'Total PRs', 'Description', title='Número de PRs (Mergeados e fechados) x Tamanho do texto da descrição [Caracteres]')

# RQ 04. Qual a relação entre o número de PRs mergeados e fechados e o número de comentários?
scatter_plot(data, 'Total PRs', 'Interactions', title='Número de PRs (Mergeados e fechados) x Número de Comentários')

# B. Número de Revisões:
# RQ 05. Qual a relação entre o tamanho dos PRs e o número de revisões realizadas?
scatter_plot(data, 'Total files', 'Total reviews', title='Tamanho dos PRs x Total de arquivos')

# RQ 06. Qual a relação entre o tempo de análise dos PRs e o número de revisões realizadas?
scatter_plot(data, 'Analysis time', 'Total reviews', title='Tempo médio de análise [Dias] x Número de Revisões')

# RQ 07. Qual a relação entre a descrição dos PRs e o número de revisões realizadas?
scatter_plot(data, 'Description', 'Total reviews', title='Tamanho do texto da descrição [Caracteres] x Número de Revisões')

# RQ 08. Qual a relação entre as interações nos PRs e o número de revisões realizadas?
scatter_plot(data, 'Interactions', 'Total reviews', title='Número de Comentários x Número de Revisões')


# Calculando a correlação de Spearman
# correlation_data = data[['Total PRs', 'Total reviews', 'Total files', 'Analysis time', 'Description', 'Interactions']]
# correlation_matrix = correlation_data.corr(method='spearman')

# correlation_matrix.to_csv('correlation_matrix.csv')

# sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
# plt.title('Matriz de Correlação (Spearman)')
# plt.show()
