import numpy as np


def calculate_statistics(df):
    sample_size = df.shape[0] - 1

    mean = df['Pmax_anual'].mean()
    ln_mean = df['ln_Pmax_anual'].mean()

    std = df['Pmax_anual'].std()
    ln_std = df['ln_Pmax_anual'].std()

    return sample_size, mean, ln_mean, std, ln_std


def calc_critical_values(gb_test, sample_size, ln_p_mean, ln_p_std):
    # Calculate the critical values t_crit_10, x_h and x_l
    
    t_crit_10 = gb_test.loc[gb_test['Number of observations']
                                 == sample_size, 'Upper 10% Significance Level'].values[0]

    k_n_10 = -3.62201 + 6.28446*(sample_size**0.25) - 2.49835*(
        sample_size**0.5) + 0.491436*(sample_size**0.75) - 0.037911*sample_size

    x_h = np.exp(ln_p_mean + k_n_10 * ln_p_std)
    x_l = np.exp(ln_p_mean - k_n_10 * ln_p_std)

    return t_crit_10, x_h, x_l


def remove_outliers(df, p_mean, p_std, t_crit_10, x_h, x_l):
    # Remove outlier values from the data based on the critical values
    max_outlier = True

    while max_outlier:
        p_max = df['Pmax_anual'].max()
        t_larger = (p_max - p_mean) / p_std

        if t_larger > t_crit_10 and p_max > x_h:
            max_outlier = True
        else:
            max_outlier = False

        if max_outlier:
            df = df.drop(labels=df[df['Pmax_anual'] == p_max].index)

    min_oulier = True

    while min_oulier:
        p_min = df['Pmax_anual'].min()
        t_smaller = (p_mean - p_min) / p_std

        if t_smaller > t_crit_10 and p_min < x_l:
            min_oulier = True
        else:
            min_oulier = False

        if min_oulier:
            df = df.drop(labels=df[df['Pmax_anual'] == p_min].index)

    return df


def main(processed_data, gb_test):

    sample_size, p_mean, ln_p_mean, p_std, ln_p_std = calculate_statistics(processed_data)

    t_crit_10, x_h, x_l = calc_critical_values(
        gb_test, sample_size, ln_p_mean, ln_p_std)

    no_outliers_data = remove_outliers(
        processed_data, p_mean, p_std, t_crit_10, x_h, x_l)

    # no_outliers_data.to_csv('./csv/no_outliers_data.csv', sep=',')

    return no_outliers_data
