import pandas as pd
import numpy as np
import pickle


def load_data(file_path):
    with open(file_path, 'rb') as f:
        hydrological_year_data = pickle.load(f)

    teste_GB = pd.read_csv("python_app/csv/Tabela_Teste_GB.csv", sep=",",
                           encoding='ISO 8859-1', decimal=",", index_col=False)

    return hydrological_year_data, teste_GB


def calculate_statistics(df):
    """Calculate mean and standard deviation of Pmax_anual and ln_Pmax_anual."""
    p_mean = df['Pmax_anual'].mean()
    ln_p_mean = df['ln_Pmax_anual'].mean()

    p_std = df['Pmax_anual'].std()
    ln_p_std = df['ln_Pmax_anual'].std()

    return p_mean, ln_p_mean, p_std, ln_p_std


def calc_critical_values(test_gb_data, sample_size, ln_p_mean, ln_p_std):
    """Calculate the critical values t_crit_10, x_h and x_l."""
    t_crit_10 = test_gb_data.loc[test_gb_data['Number of observations']
                                 == sample_size, 'Upper 10% Significance Level'].values[0]

    k_n_10 = -3.62201 + 6.28446*(sample_size**0.25) - 2.49835*(
        sample_size**0.5) + 0.491436*(sample_size**0.75) - 0.037911*sample_size

    x_h = np.exp(ln_p_mean + k_n_10 * ln_p_std)
    x_l = np.exp(ln_p_mean - k_n_10 * ln_p_std)

    return t_crit_10, x_h, x_l


def remove_outliers(df, p_mean, p_std, t_crit_10, x_h, x_l):
    """Remove outlier values from the data based on the critical values."""
    outlier = True

    while outlier:
        p_max = df['Pmax_anual'].max()
        t_larger = (p_max - p_mean) / p_std

        if t_larger > t_crit_10 and p_max > x_h:
            outlier = True
        else:
            outlier = False

        if outlier:
            df = df.drop(labels=df[df['Pmax_anual'] == p_max].index)

    outlier = True

    while outlier:
        p_min = df['Pmax_anual'].min()
        t_smaller = (p_mean - p_min) / p_std

        if t_smaller > t_crit_10 and p_min < x_l:
            outlier = True
        else:
            outlier = False

        if outlier:
            df = df.drop(labels=df[df['Pmax_anual'] == p_min].index)

    return df


def save_data(data, file_path):
    with open(file_path, 'wb') as file:
        pickle.dump(data, file)


def main():
    input_file_path = "python_app/pkl/hydrological_year_data.pkl"
    hydrological_year_data, teste_GB = load_data(input_file_path)

    p_mean, ln_p_mean, p_std, ln_p_std = calculate_statistics(
        hydrological_year_data)

    sample_size = hydrological_year_data.shape[0] - 1

    t_crit_10, x_h, x_l = calc_critical_values(
        teste_GB, sample_size, ln_p_mean, ln_p_std)

    no_outliers_data = remove_outliers(
        hydrological_year_data, p_mean, p_std, t_crit_10, x_h, x_l)

    # no_outliers_data.to_csv('./csv/no_outliers_data.csv', sep=',')

    output_file_path = "python_app/pkl/no_outliers_data.pkl"
    save_data(no_outliers_data, output_file_path)

    return no_outliers_data


if __name__ == "__main__":
    main()
