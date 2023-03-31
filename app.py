import pandas as pd
import numpy as np
from scipy.stats import t
# import matplotlib.pyplot as plt

main_df = pd.read_csv("./csv/chuvas_C_01944009.csv", sep=";",
                      encoding='ISO 8859-1', skiprows=12, decimal=",", index_col=False)

main_df = main_df[["NivelConsistencia", "Data", "Maxima"]]
main_df['Data'] = pd.to_datetime(main_df['Data'], format='%d/%m/%Y')

main_df = main_df.sort_values(by='Data', ascending=True)

# Para os Dados Consistidos => NivelConsistência = 2

consist_df = main_df.loc[main_df['NivelConsistencia'] == 2, ["Data", "Maxima"]]

start_date = consist_df['Data'].min()
end_date = consist_df['Data'].max()
new_date_range = pd.date_range(
    start=start_date, end=end_date, freq='MS')

new_consist_df = pd.DataFrame({'Data': new_date_range})
new_consist_df['Maxima_novo'] = ''

consist_df = consist_df.set_index('Data').reindex(new_date_range)
new_consist_df = new_consist_df.set_index('Data')


consist_df = consist_df.join(new_consist_df, rsuffix='_novo', how='outer')
consist_df = consist_df.sort_index()
consist_df = consist_df.reset_index()
consist_df = consist_df.drop('Maxima_novo', axis='columns')
consist_df.rename(columns={'index': 'Data'}, inplace=True)

# Para os Dados Brutos => NivelConsistência = 1

bruto_df = main_df.loc[main_df['NivelConsistencia'] == 1, ["Data", "Maxima"]]

# EXCLUIR PRIMEIROS E ÚLTIMOS DADOS FORA DO CICLO

index_first_sep = consist_df.loc[consist_df['Data'].dt.month == 9].index[0]
index_last_oct = consist_df.loc[consist_df['Data'].dt.month == 10].index[-1]
index_last = consist_df.shape[0] - 1

inicial_drop_range = consist_df.iloc[0:index_first_sep+1]
final_drop_range = consist_df.iloc[index_last_oct:index_last + 1]

consist_df = consist_df.drop(inicial_drop_range.index)
consist_df = consist_df.drop(final_drop_range.index)

consist_df = consist_df.reset_index(drop=True)
bruto_df = bruto_df.reset_index(drop=True)

# PREENCHER VALORES VAZIOS DE MAXIMA COM OS DADOS BRUTOS

consist_df.set_index('Data', inplace=True)
bruto_df.set_index('Data', inplace=True)

merged_df = consist_df.merge(
    bruto_df, left_index=True, right_index=True, how='left')

merged_df['Maxima_x'].fillna(merged_df['Maxima_y'], inplace=True)

merged_df.drop('Maxima_y', axis=1, inplace=True)

merged_df.rename(columns={'Maxima_x': 'Maxima'}, inplace=True)

merged_df.reset_index(inplace=True)

# MÁXIMA E LN DA MAXIMA PARA CADA ANO HIDROLÓGICO

merged_df["AnoHidrologico"] = merged_df["Data"].apply(
    lambda x: x.year if x.month >= 10 else x.year - 1)

ano_hidrologico_df = merged_df.groupby("AnoHidrologico")[
    "Maxima"].max().reset_index()

ano_hidrologico_df = ano_hidrologico_df.rename(
    columns={"Maxima": "Pmax_anual"})

ano_hidrologico_df['ln_Pmax_anual'] = np.log(ano_hidrologico_df['Pmax_anual'])

# ---------------------------------- DADOS DA AMOSTRA -----------------------------------

media_Pmax = ano_hidrologico_df['Pmax_anual'].mean()
media_ln_Pmax = ano_hidrologico_df['ln_Pmax_anual'].mean()

std_Pmax = ano_hidrologico_df['Pmax_anual'].std()
std_ln_Pmax = ano_hidrologico_df['ln_Pmax_anual'].std()

tamanho_amostra = ano_hidrologico_df.shape[0] - 1

maior_valor = ano_hidrologico_df['Pmax_anual'].max()
maior2_valor = ano_hidrologico_df['Pmax_anual'].nlargest(2).iloc[1]
menor2_valor = ano_hidrologico_df['Pmax_anual'].nsmallest(2).iloc[1]
menor_valor = ano_hidrologico_df['Pmax_anual'].min()

T_maior = (maior_valor - media_Pmax)/std_Pmax
T_2maior = (maior2_valor - media_Pmax)/std_Pmax
T_2menor = (media_Pmax - menor2_valor)/std_Pmax
T_menor = (media_Pmax - menor_valor)/std_Pmax

teste_GB = pd.read_csv("./csv/Tabela_Teste_GB.csv", sep=",",
                       encoding='ISO 8859-1', decimal=",", index_col=False)

Tcri_10 = teste_GB.loc[teste_GB['Number of observations']
                       == tamanho_amostra, 'Upper 10% Significance Level'].values[0]

resultado1_maior = ""
resultado1_2maior = ""
resultado1_2menor = ""
resultado1_menor = ""

if T_maior > Tcri_10:
    resultado1_maior = "outlier"

if T_2maior > Tcri_10:
    resultado1_2maior = "outlier"

if T_2menor > Tcri_10:
    resultado1_2menor = "outlier"

if T_menor > Tcri_10:
    resultado1_menor = "outlier"


kN_10 = -3.62201 + 6.28446*(tamanho_amostra**0.25) - 2.49835*(
    tamanho_amostra**0.5) + 0.491436*(tamanho_amostra**0.75) - 0.037911*tamanho_amostra

Xh_maior = np.exp(media_ln_Pmax + kN_10 * std_ln_Pmax)
Xl_menor = np.exp(media_ln_Pmax - kN_10 * std_ln_Pmax)

resultado2_maior = ""
resultado2_2maior = ""
resultado2_2menor = ""
resultado2_menor = ""

if maior_valor > Xh_maior:
    resultado2_maior = "outlier"

if maior2_valor > Xh_maior:
    resultado2_2maior = "outlier"

if menor2_valor < Xl_menor:
    resultado2_2menor = "outlier"

if menor_valor < Xl_menor:
    resultado2_menor = "outlier"

# RESULTADOS FINAIS

resultado_final_maior = ""
resultado_final_2maior = ""
resultado_final_2menor = ""
resultado_final_menor = ""

if resultado1_maior == "outlier" and resultado2_maior == "outlier":
    resultado_final_maior = "outlier"

if resultado1_2maior == "outlier" and resultado2_2maior == "outlier":
    resultado_final_2maior = "outlier"

if resultado1_2menor == "outlier" and resultado2_2maior == "outlier":
    resultado_final_2menor = "outlier"

if resultado1_menor == "outlier" and resultado2_maior == "outlier":
    resultado_final_menor = "outlier"


ano_hidrologico_df.to_csv('anoHidrologico.csv', sep=';')
