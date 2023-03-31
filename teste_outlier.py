import pandas as pd
import numpy as np
from scipy.stats import t

from app import ano_hidrologico_df

Pmax_media = ano_hidrologico_df['Pmax_anual'].mean()
media_ln_Pmax = ano_hidrologico_df['ln_Pmax_anual'].mean()

std_Pmax = ano_hidrologico_df['Pmax_anual'].std()
std_ln_Pmax = ano_hidrologico_df['ln_Pmax_anual'].std()

tamanho_amostra = ano_hidrologico_df.shape[0] - 1

# PRECIPITAÇÃO MAXIMA ANUAL

Pmax_anual_maior = ano_hidrologico_df['Pmax_anual'].max()
Pmax_anual_2maior = ano_hidrologico_df['Pmax_anual'].nlargest(2).iloc[1]
Pmax_anual_2menor = ano_hidrologico_df['Pmax_anual'].nsmallest(2).iloc[1]
Pmax_anual_menor = ano_hidrologico_df['Pmax_anual'].min()

T_maior = (Pmax_anual_maior - Pmax_media)/std_Pmax
T_2maior = (Pmax_anual_2maior - Pmax_media)/std_Pmax
T_2menor = (Pmax_media - Pmax_anual_2menor)/std_Pmax
T_menor = (Pmax_media - Pmax_anual_menor)/std_Pmax

teste_GB = pd.read_csv("./csv/Tabela_Teste_GB.csv", sep=",",
                       encoding='ISO 8859-1', decimal=",", index_col=False)

# Simplificar cabeçalho e excluir valores não utilizados da tabela Teste GB

Tcri_10 = teste_GB.loc[teste_GB['Number of observations']
                       == tamanho_amostra, 'Upper 10% Significance Level'].values[0]

result1_maior = ""
result1_2maior = ""
result1_2menor = ""
result1_menor = ""

if T_maior > Tcri_10:
    result1_maior = "outlier"

if T_2maior > Tcri_10:
    result1_2maior = "outlier"

if T_2menor > Tcri_10:
    result1_2menor = "outlier"

if T_menor > Tcri_10:
    result1_menor = "outlier"


kN_10 = -3.62201 + 6.28446*(tamanho_amostra**0.25) - 2.49835*(
    tamanho_amostra**0.5) + 0.491436*(tamanho_amostra**0.75) - 0.037911*tamanho_amostra

Xh_maior = np.exp(media_ln_Pmax + kN_10 * std_ln_Pmax)
Xl_menor = np.exp(media_ln_Pmax - kN_10 * std_ln_Pmax)

resultado2_maior = ""
resultado2_2maior = ""
resultado2_2menor = ""
resultado2_menor = ""

if Pmax_anual_maior > Xh_maior:
    resultado2_maior = "outlier"

if Pmax_anual_2maior > Xh_maior:
    resultado2_2maior = "outlier"

if Pmax_anual_2menor < Xl_menor:
    resultado2_2menor = "outlier"

if Pmax_anual_menor < Xl_menor:
    resultado2_menor = "outlier"

# RESULTADOS FINAIS

resultado_final_maior = ""
resultado_final_2maior = ""
resultado_final_2menor = ""
resultado_final_menor = ""

if result1_maior == "outlier" and resultado2_maior == "outlier":
    resultado_final_maior = "outlier"

if result1_2maior == "outlier" and resultado2_2maior == "outlier":
    resultado_final_2maior = "outlier"

if result1_2menor == "outlier" and resultado2_2maior == "outlier":
    resultado_final_2menor = "outlier"

if result1_menor == "outlier" and resultado2_maior == "outlier":
    resultado_final_menor = "outlier"
