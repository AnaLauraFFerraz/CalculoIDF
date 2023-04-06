import numpy as np


def calculate_statistics(df):
    mean = df['Pmax_anual'].mean()
    ln_mean = df['ln_Pmax_anual'].mean()

    std = df['Pmax_anual'].std()
    ln_std = df['ln_Pmax_anual'].std()

    return mean, ln_mean, std, ln_std


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


def main(processed_data, teste_gb):

    p_mean, ln_p_mean, p_std, ln_p_std = calculate_statistics(processed_data)

    sample_size = processed_data.shape[0] - 1

    t_crit_10, x_h, x_l = calc_critical_values(
        teste_gb, sample_size, ln_p_mean, ln_p_std)

    no_outliers_data = remove_outliers(
        processed_data, p_mean, p_std, t_crit_10, x_h, x_l)

    # no_outliers_data.to_csv('./csv/no_outliers_data.csv', sep=',')

    return no_outliers_data


# if __name__ == "__main__":
#     main()
