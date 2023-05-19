import json
import sys
import os
import pandas as pd

from process_data import main as process_data
from teste_outlier import main as teste_outlier
from distributions import main as distributions
from k_coefficient import main as k_coefficient
from disaggregation_coef import disaggregation_coef
from ventechow import main as ventechow


def load_data(csv_file_path):
    """
    Function to load the required data for further analysis.
    Args:
        csv_file_path (str): Path of the CSV file to be loaded.
    Returns:
        tuple: Returns a tuple containing the input data, Grubbs' test data, and YN SigmaN table data.
    """

    script_dir = os.path.dirname(os.path.abspath(__file__))

    input_data = pd.read_csv(csv_file_path, sep=";", encoding='ISO 8859-1', skiprows=12,
                             decimal=",", usecols=["NivelConsistencia", "Data", "Maxima"], index_col=False)

    gb_test_file_path = os.path.join(script_dir, "csv", "Tabela_Teste_GB.csv")
    gb_test = pd.read_csv(gb_test_file_path, sep=",",
                          encoding='ISO 8859-1', decimal=",", index_col=False)

    yn_sigman_file_path = os.path.join(
        script_dir, "csv", "Tabela_YN_sigmaN.csv")
    table_yn_sigman = pd.read_csv(yn_sigman_file_path, sep=",", encoding='ISO 8859-1',
                                  decimal=",", usecols=["Size", "YN", "sigmaN"], index_col=False)

    return input_data, gb_test, table_yn_sigman


def main(csv_file_path):
    """
    Main function to process the data, test for outliers, determine the distribution, 
    calculate the k coefficient, and calculate the Ven Te Chow parameters.
    Args:
        csv_file_path (str): Path of the CSV file to be processed.
    Returns:
        dict: Returns a dictionary with the calculated parameters and other relevant results.
    """

    raw_df, gb_test, table_yn_sigman = load_data(csv_file_path)

    processed_data = process_data(raw_df)

    if processed_data.empty:
        insufficient_data = "Dados não são sufientes para completar a análise"
        with open('idf_data.json', 'w', encoding='utf-8') as file:
            json.dump(insufficient_data, file)
        return json.dumps(insufficient_data)

    no_outlier = teste_outlier(processed_data, gb_test)

    distribution_data, params, dist_r2 = distributions(
        no_outlier, table_yn_sigman)

    disaggregation_data, time_interval = disaggregation_coef()

    k_coefficient_data = k_coefficient(params, dist_r2)

    output = ventechow(distribution_data, k_coefficient_data,
                       disaggregation_data, params, time_interval, dist_r2)

    with open('output.json', 'w', encoding='utf-8') as json_file:
        json.dump(output, json_file)

    return output


# if __name__ == "__main__":
#     if len(sys.argv) < 2:
#         print("Por favor, forneça o caminho do arquivo CSV como argumento")
#     else:
#         csv_file_path = sys.argv[1]
#         main(csv_file_path)

if __name__ == "__main__":
    csv_file_path = "CalculoIDF/python_scripts/csv/chuvas_C_01844000_CV.csv"
    main(csv_file_path)
