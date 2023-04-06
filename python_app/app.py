import pandas as pd

from process_data import main as process_data
from teste_outlier import main as teste_outlier
from distributions import main as distributions
from ventechow import main as ventechow


def load_data():
    input_file_path = "python_app/csv/chuvas_C_01944009.csv"
    input_data = pd.read_csv(input_file_path, sep=";", encoding='ISO 8859-1', skiprows=12,
                             decimal=",", usecols=["NivelConsistencia", "Data", "Maxima"], index_col=False)

    teste_gb_file_path = "python_app/csv/Tabela_Teste_GB.csv"
    teste_gb = pd.read_csv(teste_gb_file_path, sep=",",
                           encoding='ISO 8859-1', decimal=",", index_col=False)

    yn_sigman_file_path = "python_app/csv/Tabela_YN_sigmaN.csv"
    table_yn_sigman = pd.read_csv(yn_sigman_file_path, sep=",", encoding='ISO 8859-1',
                             decimal=",", usecols=["Size", "YN", "sigmaN"], index_col=False)
    
    return input_data, teste_gb, table_yn_sigman


def main():
    raw_df, teste_gb, table_yn_sigman = load_data()

    processed_data = process_data(raw_df)

    no_outlier = teste_outlier(processed_data, teste_gb)

    df, params, max_value_r2 = distributions(no_outlier, table_yn_sigman)

    final_data = ventechow(df, params, max_value_r2)

    return final_data


if __name__ == "__main__":
    main()
