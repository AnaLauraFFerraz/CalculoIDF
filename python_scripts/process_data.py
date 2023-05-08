import pandas as pd
import numpy as np


def process_raw_data(df):
    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')
    df = df.sort_values(by='Data', ascending=True)
    return df


def get_consistent_data(df):
    # Retorna os dados com NivelConsistencia == 2
    consistent_data = df.loc[df['NivelConsistencia']
                             == 2, ["Data", "Maxima"]].copy()

    if consistent_data.shape[0] < 10:
        consistent_data.drop(consistent_data.index, inplace=True)
        return consistent_data

    consistent_data = consistent_data.set_index('Data')
    consistent_data = consistent_data.resample('MS')
    consistent_data = consistent_data.ffill()
    consistent_data = consistent_data.reset_index()

    return consistent_data


def get_raw_data(df):
    # Retorna os dados com NivelConsistencia == 1
    raw_data = df.loc[df['NivelConsistencia'] == 1, [
        "Data", "Maxima"]].reset_index(drop=True)

    raw_data = raw_data.set_index('Data')
    raw_data = raw_data.resample('MS')
    raw_data = raw_data.ffill()
    raw_data = raw_data.reset_index()

    return raw_data


def merge_and_fill_data(consistent_data, raw_data):
    # Encontra a última data nos dois DataFrames
    last_date = min(consistent_data['Data'].max(), raw_data['Data'].max())

    # Filtra os DataFrames até a última data
    consistent_data = consistent_data.loc[consistent_data['Data'] <= last_date]
    raw_data = raw_data.loc[raw_data['Data'] <= last_date]

    merged_df = pd.merge(consistent_data, raw_data,
                         on="Data", how="left", suffixes=('', '_y'))

    merged_df['Maxima'].fillna(merged_df['Maxima_y'], inplace=True)
    merged_df.drop('Maxima_y', axis=1, inplace=True)

    merged_df['Maxima'].fillna(0, inplace=True)

    return merged_df


def remove_out_of_cycle_data(df):
    index_first_sep = df.loc[df['Data'].dt.month == 9].index[0]
    index_last_oct = df.loc[df['Data'].dt.month == 10].index[-1]
    index_last = df.shape[0] - 1

    inicial_drop_range = df.iloc[0:index_first_sep + 1]
    final_drop_range = df.iloc[index_last_oct:index_last + 1]

    df = df.drop(inicial_drop_range.index)
    df = df.drop(final_drop_range.index)

    df = df.reset_index(drop=True)

    return df


def add_hydrological_year(df):
    df["AnoHidrologico"] = df["Data"].dt.year.where(
        df["Data"].dt.month >= 10, df["Data"].dt.year - 1)

    hydrological_year_df = df.groupby("AnoHidrologico")["Maxima"].max(
    ).reset_index().rename(columns={"Maxima": "Pmax_anual"})

    hydrological_year_df['ln_Pmax_anual'] = np.log(
        hydrological_year_df['Pmax_anual'])

    hydrological_year_df = hydrological_year_df.sort_values(
        by='Pmax_anual', ascending=False).reset_index(drop=True)

    return hydrological_year_df


def main(raw_df):
    raw_df = raw_df.fillna(0)
    rain_data = process_raw_data(raw_df)

    consistent_rain_data = get_consistent_data(rain_data)
    raw_rain_data = get_raw_data(rain_data)

    if consistent_rain_data.empty:
        print("consistent_rain_data is empty")
        consistent_rain_data = raw_rain_data

    filled_rain_data = merge_and_fill_data(consistent_rain_data, raw_rain_data)

    filled_rain_data = remove_out_of_cycle_data(filled_rain_data)

    hydrological_year_data = add_hydrological_year(filled_rain_data)

    if hydrological_year_data.shape[0] < 10:
        hydrological_year_data.drop(hydrological_year_data.index, inplace=True)
        return hydrological_year_data
    
    # print("\hydrological_year_data\n", hydrological_year_data)
    # hydrological_year_data.to_csv('hydrological_year_data.csv', sep=',')

    return hydrological_year_data
