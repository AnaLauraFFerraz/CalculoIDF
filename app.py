import pandas as pd
# import numpy as np
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
