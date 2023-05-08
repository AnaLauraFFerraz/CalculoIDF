import pandas as pd
import sys
import os
import json

from process_data import main as process_data
from teste_outlier import main as teste_outlier
from distributions import main as distributions
from k_coefficient import main as k_coefficient
from disaggregation_coef import disaggregation_coef
from ventechow import main as ventechow


def load_data(csv_file_path):
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
    raw_df, gb_test, table_yn_sigman = load_data(csv_file_path)

    processed_data = process_data(raw_df)

    if processed_data.empty:
        insufficient_data = "Dados não são sufientes para completar a análise"
        with open('idf_data.json', 'w', encoding='utf-8') as f:
            json.dump(insufficient_data, f)
        return json.dumps(insufficient_data)

    no_outlier = teste_outlier(processed_data, gb_test)

    params, dist_r2 = distributions(
        no_outlier, table_yn_sigman)

    disaggregation_data, time_interval = disaggregation_coef()

    k_coefficient_data = k_coefficient(params, dist_r2)

    idf_data = ventechow(k_coefficient_data,
                         disaggregation_data, params, time_interval, dist_r2)

    # Converte o DataFrame em uma lista de dicionários
    idf_data_list = idf_data.to_dict(orient='records')

    # Cria um dicionário vazio
    output_dict = {}

    # Adiciona cada objeto do DataFrame ao dicionário
    for i, row in enumerate(idf_data_list):
        output_dict[str(i)] = row

    with open('idf_data.json', 'w', encoding='utf-8') as f:
        json.dump(output_dict, f)

    # print("\nJSON gerado:")
    # print(json.dumps(output_dict, indent=2))

    # Retorna o dicionário como uma string JSON
    return json.dumps(output_dict)


# if __name__ == "__main__":
#     if len(sys.argv) < 2:
#         print("Por favor, forneça o caminho do arquivo CSV como argumento")
#     else:
#         csv_file_path = sys.argv[1]
#         main(csv_file_path)

if __name__ == "__main__":
    csv_file_path = "CalculoIDF/python_scripts/csv/chuvas_C_01844000_CV.csv"
    main(csv_file_path)
