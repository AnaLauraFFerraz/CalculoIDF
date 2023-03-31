import pandas as pd
import numpy as np

from app import ano_hidrologico_df

# Simplificar cabeçalho e excluir valores não utilizados da tabela Teste GB
teste_GB = pd.read_csv("./csv/Tabela_Teste_GB.csv", sep=",",
                       encoding='ISO 8859-1', decimal=",", index_col=False)


Pmedia_anual = ano_hidrologico_df['Pmax_anual'].mean()
ln_Pmedia_anual = ano_hidrologico_df['ln_Pmax_anual'].mean()

Pdesvp_anual = ano_hidrologico_df['Pmax_anual'].std()
ln_Pdesvp_anual = ano_hidrologico_df['ln_Pmax_anual'].std()

tam_amostra = ano_hidrologico_df.shape[0] - 1

Tcri_10 = teste_GB.loc[teste_GB['Number of observations']
                       == tam_amostra, 'Upper 10% Significance Level'].values[0]

kN_10 = -3.62201 + 6.28446*(tam_amostra**0.25) - 2.49835*(
    tam_amostra**0.5) + 0.491436*(tam_amostra**0.75) - 0.037911*tam_amostra

Xh = np.exp(ln_Pmedia_anual + kN_10 * ln_Pdesvp_anual)
Xl = np.exp(ln_Pmedia_anual - kN_10 * ln_Pdesvp_anual)

# VALORES MÁXIMOS

result_final_max = "outlier"

while result_final_max == "outlier":
    Pmax_anual = ano_hidrologico_df['Pmax_anual'].max()
    T_maior = (Pmax_anual - Pmedia_anual)/Pdesvp_anual

    if T_maior > Tcri_10:
        result1_max = "outlier"
    else:
        result1_max = ""

    if Pmax_anual > Xh:
        result2_max = "outlier"
    else:
        result2_max = ""

    if result1_max == "outlier" and result2_max == "outlier":
        result_final_max = "outlier"
    else:
        result_final_max = ""

    if result_final_max == "outlier":
        ano_hidrologico_df = ano_hidrologico_df.drop(
            labels=ano_hidrologico_df[ano_hidrologico_df['Pmax_anual'] == Pmax_anual].index)

# VALORES MÍNIMOS

result_final_min = "outlier"

while result_final_min == "outlier":
    Pmin_anual = ano_hidrologico_df['Pmax_anual'].min()
    T_menor = (Pmedia_anual - Pmin_anual)/Pdesvp_anual

    if T_menor > Tcri_10:
        result1_min = "outlier"
    else:
        result1_min = ""

    if Pmin_anual < Xl:
        result2_min = "outlier"
    else:
        result2_min = ""

    if result1_min == "outlier" and result2_max == "outlier":
        result_final_min = "outlier"
    else:
        result_final_min = ""

    if result_final_min == "outlier":
        ano_hidrologico_df = ano_hidrologico_df.drop(
            labels=ano_hidrologico_df[ano_hidrologico_df['Pmax_anual_menor'] == Pmax_anual].index)


ano_hidrologico_df.to_csv('anoHidrologico.csv', sep=',')
