
import pandas as pd
import os

def gmt_brazil(Dataframe):
    """ Converte coordenas UTC em GMT """
    #Separa texto UTC do valor de hora
    Dataframe[['Hora', 'UTC']] = Dataframe['Hora UTC'].str.extract(r'(\d+)\s+(.*)')

    #Formatação dos valores de hora
    Dataframe['Hora'] = Dataframe['Hora'].astype('int')
    Dataframe['Hora'] = Dataframe['Hora'].apply(lambda x: f"{x//100}:{x%100:02d}")
    Dataframe['Hora'] = pd.to_datetime(Dataframe['Hora'], format='%H:%M')
    
    #Converte data e tempo em apenas tempo
    Dataframe['Hora'] = Dataframe['Hora'].dt.time
    
    #Une data e tempo de colunas diferentes
    Dataframe['DateTime'] = pd.to_datetime(Dataframe['Data'].astype(str) + ' ' + Dataframe['Hora'].astype(str))
    
    #Subtrai 3 horas dos valores em UTC
    Dataframe['DateTime'] = Dataframe['DateTime'] - pd.Timedelta(hours=3)
    
    #Substitui os valores da coluna Hora por apenas o tempo GMT
    Dataframe['Hora'] = Dataframe['DateTime'].dt.time
    
def empilhar_planilhas(caminho_pasta):
    """Formata e empilha todos os arquivos CSV exportados do INMET"""
    # Lista para armazenar os DataFrames de cada planilha
    dfs = []

    # Percorre todos os arquivos na pasta
    for arquivo in os.listdir(caminho_pasta):
        if arquivo.endswith('.CSV'):
            caminho_arquivo = os.path.join(caminho_pasta, arquivo)

            # Leitura da planilha e adição ao DataFrame
            df_unico = pd.read_csv(caminho_arquivo,
            sep = ';', encoding= 'latin1', header = None, names = range(20))
            df_unico.columns = df_unico.iloc[8]
            df_unico['Região'] = df_unico.iloc[0,1]
            df_unico['UF'] = df_unico.iloc[1,1]
            df_unico['Estação'] = df_unico.iloc[2,1]
            df_unico = df_unico.drop([0,1,2,3,4,5,6,7,8], axis = 0)
            df_unico.reset_index(drop = True, inplace = True)
            
            #Converter UTM para GMT-3
            gmt_brazil(df_unico)
            
            #Adicionar df_unico a uma lista de Dataframes
            dfs.append(df_unico)
            
    #Concatenando cada DataFrame da lista de Dataframes
    df_final = pd.concat(dfs, ignore_index=True)
    
    #Excluir colunas com datas e horas UTC
    df_final = df_final.drop(['Data','Hora UTC','UTC'],axis = 1)
    
    #Exportando consolidado csv
    df_final.to_csv('df_consolidado.csv', index= False)
    
#Caminho relativo para o diretório atual
##OBS: __file__ não roda em notebooks
dir_tual = os.path.dirname(__file__)
dados_INMET = os.path.join(dir_tual, 'Dados Meorologicos 1S 2024')

#Execução da concatenação dos CSV's
empilhar_planilhas(dados_INMET)