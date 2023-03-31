import pandas as pd
import numpy as np
import pickle


def load_data(file_path):
    return pd.read_csv(file_path, sep=";", encoding='ISO 8859-1', skiprows=12, decimal=",", usecols=["NivelConsistencia", "Data", "Maxima"])


def process_data(df):
    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')
    df = df.sort_values(by='Data', ascending=True)
    return df


def get_consistent_data(df):
    consistent_data = df.loc[df['NivelConsistencia'] == 2, ["Data", "Maxima"]]
    start_date = consistent_data['Data'].min()
    end_date = consistent_data['Data'].max()
    new_date_range = pd.date_range(start=start_date, end=end_date, freq='MS')
    consistent_data = consistent_data.set_index('Data').reindex(new_date_range)
    consistent_data = consistent_data.sort_index(
    ).reset_index().rename(columns={'index': 'Data'})
    return consistent_data


def get_raw_data(df):
    return df.loc[df['NivelConsistencia'] == 1, ["Data", "Maxima"]].reset_index(drop=True)


def remove_out_of_cycle_data(df):
    index_first_sep = df.loc[df['Data'].dt.month == 9].index[0]
    index_last_oct = df.loc[df['Data'].dt.month == 10].index[-1]
    index_last = df.shape[0] - 1

    inicial_drop_range = df.iloc[0:index_first_sep+1]
    final_drop_range = df.iloc[index_last_oct:index_last + 1]

    df = df.drop(inicial_drop_range.index)
    df = df.drop(final_drop_range.index)

    return df.reset_index(drop=True)


def merge_and_fill_data(consistent_data, raw_data):
    merged_df = consistent_data.merge(
        raw_data, left_index=True, right_index=True, how='left', suffixes=('', '_y'))
    merged_df['Maxima'].fillna(merged_df['Maxima_y'], inplace=True)
    merged_df.drop('Maxima_y', axis=1, inplace=True)
    return merged_df.reset_index(drop=True)


def add_hydrological_year(df):
    df["AnoHidrologico"] = df["Data"].apply(
        lambda x: x.year if x.month >= 10 else x.year - 1)
    ano_hidrologico_df = df.groupby("AnoHidrologico")["Maxima"].max(
    ).reset_index().rename(columns={"Maxima": "Pmax_anual"})
    ano_hidrologico_df['ln_Pmax_anual'] = np.log(
        ano_hidrologico_df['Pmax_anual'])
    return ano_hidrologico_df


def save_data(data, file_path):
    with open(file_path, 'wb') as f:
        pickle.dump(data, f)


def main():
    input_file_path = "./csv/chuvas_C_01944009.csv"
    rain_data = load_data(input_file_path)
    rain_data = process_data(rain_data)

    consistent_rain_data = get_consistent_data(rain_data)
    raw_rain_data = get_raw_data(rain_data)

    consistent_rain_data = remove_out_of_cycle_data(consistent_rain_data)

    filled_rain_data = merge_and_fill_data(consistent_rain_data, raw_rain_data)

    hydrological_year_data = add_hydrological_year(filled_rain_data)

    print(hydrological_year_data)

    output_file_path = "hydrological_year_data.pkl"
    save_data(hydrological_year_data, output_file_path)

    consistent_rain_data.to_csv('./csv/consistent_rain_data.csv', sep=',')
    raw_rain_data.to_csv('./csv/raw_rain_data.csv', sep=',')


if __name__ == "__main__":
    main()
