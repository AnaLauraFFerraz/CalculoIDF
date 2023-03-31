import pandas as pd
import numpy as np

dados_completos_chuvas = pd.read_csv("./csv/chuvas_C_01944009.csv", sep=";",
                                     encoding='ISO 8859-1', skiprows=12, decimal=",", usecols=["NivelConsistencia", "Data", "Maxima"], index_col=False)

dados_completos_chuvas['Data'] = pd.to_datetime(
    dados_completos_chuvas['Data'], format='%d/%m/%Y')

dados_completos_chuvas = dados_completos_chuvas.sort_values(
    by='Data', ascending=True)

print(dados_completos_chuvas)

# Para os Dados Consistidos => NivelConsistência = 2

dados_consistentes = dados_completos_chuvas.loc[dados_completos_chuvas['NivelConsistencia'] == 2, [
    "Data", "Maxima"]]

start_date = dados_consistentes['Data'].min()
end_date = dados_consistentes['Data'].max()
new_date_range = pd.date_range(
    start=start_date, end=end_date, freq='MS')

new_consist_df = pd.DataFrame({'Data': new_date_range})
new_consist_df['Maxima_novo'] = ''

dados_consistentes = dados_consistentes.set_index(
    'Data').reindex(new_date_range)
new_consist_df = new_consist_df.set_index('Data')


dados_consistentes = dados_consistentes.join(
    new_consist_df, rsuffix='_novo', how='outer')
dados_consistentes = dados_consistentes.sort_index()
dados_consistentes = dados_consistentes.reset_index()
dados_consistentes = dados_consistentes.drop('Maxima_novo', axis='columns')
dados_consistentes.rename(columns={'index': 'Data'}, inplace=True)

# Para os Dados Brutos => NivelConsistência = 1

dados_brutos = dados_completos_chuvas.loc[dados_completos_chuvas['NivelConsistencia'] == 1, [
    "Data", "Maxima"]]

# EXCLUIR PRIMEIROS E ÚLTIMOS DADOS FORA DO CICLO

index_first_sep = dados_consistentes.loc[dados_consistentes['Data'].dt.month == 9].index[0]
index_last_oct = dados_consistentes.loc[dados_consistentes['Data'].dt.month == 10].index[-1]
index_last = dados_consistentes.shape[0] - 1

inicial_drop_range = dados_consistentes.iloc[0:index_first_sep+1]
final_drop_range = dados_consistentes.iloc[index_last_oct:index_last + 1]

dados_consistentes = dados_consistentes.drop(inicial_drop_range.index)
dados_consistentes = dados_consistentes.drop(final_drop_range.index)

dados_consistentes = dados_consistentes.reset_index(drop=True)
dados_brutos = dados_brutos.reset_index(drop=True)

# PREENCHER VALORES VAZIOS DE MAXIMA COM OS DADOS BRUTOS

dados_consistentes.set_index('Data', inplace=True)
dados_brutos.set_index('Data', inplace=True)

merged_df = dados_consistentes.merge(
    dados_brutos, left_index=True, right_index=True, how='left')

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
