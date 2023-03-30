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
