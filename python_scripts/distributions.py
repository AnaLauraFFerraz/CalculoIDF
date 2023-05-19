import numpy as np
from scipy.special import gammaincinv
from scipy.stats import norm, stats, skew


def params_calculation(df, sigmaN, yn, sample_size):
    """
    Calculates and returns a set of parameters derived from the input dataframe.
    Args:
        df (DataFrame): Input DataFrame containing the columns "Pmax_anual" and "P_log".
        sigmaN (float): The standard deviation of the normal distribution.
        yn (float): The mean of the normal distribution.
        sample_size (int): Size of the sample data.
    Returns:
        dict: A dictionary containing statistical parameters.
    """

    mean = df["Pmax_anual"].mean()
    std_dev = df["Pmax_anual"].std()
    meanw = df["P_log"].mean()
    std_devw = df["P_log"].std()
    g = skew(df["Pmax_anual"])
    alpha = 4/g**2
    gw = skew(df['P_log'])
    alphaw = 4/gw**2

    params = {
        "size": sample_size,
        "mean": mean,
        "std_dev": std_dev,
        "g": g,
        "alpha": alpha,
        "meanw": meanw,
        "stdw": std_devw,
        "gw": gw,
        "alphaw": alphaw,
        "sigman": sigmaN,
        "yn": yn
    }

    return params


def yn_sigman_calculation(df, sample_size):
    """
    Function to get 'sigmaN' and 'YN' values from the dataframe based on the sample size.
    Args:
        df (DataFrame): The dataframe to be processed.
        sample_size (int): The size of the sample.
    Returns:
        tuple: Returns a tuple containing sigmaN and yn.
    """

    sigmaN = df.loc[df['Size'] == sample_size, 'sigmaN'].values[0]
    yn = df.loc[df['Size'] == sample_size, 'YN'].values[0]

    return sigmaN, yn


def dist_log_normal(df, params):
    """
    Function to calculate r2 for the log-normal distribution.
    Args:
        df (DataFrame): The dataframe to be processed.
        params (dict): The parameters dictionary.
    Returns:
        float: Returns the r2 value for the log-normal distribution.
    """

    df["WTr"] = params["meanw"] + params["stdw"] * df["KN"]
    df["P_log_normal"] = np.power(10, df['WTr'])

    corr_log_normal, _ = stats.pearsonr(df["Pmax_anual"], df["P_log_normal"])
    r2_log_normal = corr_log_normal ** 2
    r2_log_normal = r2_log_normal.round(4)

    return r2_log_normal


def dist_pearson(df, params):
    """
    Function to calculate r2 for the Pearson distribution.
    Args:
        df (DataFrame): The dataframe to be processed.
        params (dict): The parameters dictionary.
    Returns:
        float: Returns the r2 value for the Pearson distribution.
    """

    if params["gw"] > 0:
        params["alpha"] = params["alphaw"]

    df['YTR'] = np.where(params["alpha"] > 0, gammaincinv(
        params["alpha"], df['one_minus_F']), gammaincinv(params["alpha"], df['F']))

    df["KP"] = (params["g"]/2) * (df['YTR'] - params["alpha"])
    df["P_pearson"] = params["mean"] + params["std_dev"] * df["KP"]

    corr_pearson, _ = stats.pearsonr(df["Pmax_anual"], df["P_pearson"])
    r2_pearson = corr_pearson ** 2
    r2_pearson = r2_pearson.round(4)
    return r2_pearson


def dist_log_pearson(df, params):
    """
    Function to calculate r2 for the log-Pearson distribution.
    Args:
        df (DataFrame): The dataframe to be processed.
        params (dict): The parameters dictionary.
    Returns:
        float: Returns the r2 value for the log-Pearson distribution.
    """

    df["YTRw"] = np.where(params["alphaw"] > 0, gammaincinv(
        params["alphaw"], df['one_minus_F']), gammaincinv(params["alphaw"], df['F']))

    df["KL_P"] = (params["gw"]/2)*(df['YTRw']-params["alphaw"])
    df["WTr_LP"] = params["meanw"] + params["stdw"] * df["KL_P"]

    df["P_log_pearson"] = np.power(10, df['WTr_LP'])

    corr_log_pearson, _ = stats.pearsonr(df["Pmax_anual"], df["P_log_pearson"])
    r2_log_pearson = corr_log_pearson ** 2
    r2_log_pearson = r2_log_pearson.round(4)
    return r2_log_pearson


def dist_gumbel_theoretical(df, params):
    """
    Function to calculate r2 for the theoretical Gumbel distribution.
    Args:
        df (DataFrame): The dataframe to be processed.
        params (dict): The parameters dictionary.
    Returns:
        float: Returns the r2 value for the theoretical Gumbel distribution.
    """

    df["y"] = df["one_minus_F"].apply(lambda x: -np.log(-np.log(x)))

    df["KG_T"] = 0.7797 * df["y"] - 0.45

    df["P_gumbel_theoretical"] = params["mean"] + \
        params["std_dev"] * df["KG_T"]

    corr_gumbel, _ = stats.pearsonr(
        df["Pmax_anual"], df["P_gumbel_theoretical"])

    r2_gumbel_theo = corr_gumbel ** 2
    r2_gumbel_theo = r2_gumbel_theo.round(4)

    return r2_gumbel_theo


def dist_gumbel_finite(df, params):
    """
    Function to calculate r2 for the finite Gumbel distribution.
    Args:
        df (DataFrame): The dataframe to be processed.
        params (dict): The parameters dictionary.
    Returns:
        float: Returns the r2 value for the finite Gumbel distribution.
    """

    df["KG_F"] = (df["y"] - params["yn"]) / params["sigman"]

    df["P_gumbel_finite"] = params["mean"] + params["std_dev"] * df["KG_F"]

    corr_gumbel_finite, _ = stats.pearsonr(
        df["Pmax_anual"], df["P_gumbel_finite"])

    r2_gumbel_finite = corr_gumbel_finite ** 2
    r2_gumbel_finite = r2_gumbel_finite.round(4)

    return r2_gumbel_finite


def dist_calculations(no_oulier_data, sigmaN, yn, sample_size):
    """
    Function to perform various distribution calculations.
    Args:
        no_oulier_data (DataFrame): The processed dataframe with no outliers.
        sigmaN (float): The sigmaN value.
        yn (float): The yn value.
        sample_size (int): The size of the sample.
    Returns:
        tuple: Returns a tuple containing the processed dataframe, parameters, and dist_r2 dictionary.
    """

    no_oulier_data["F"] = (no_oulier_data.index + 1) / (sample_size + 1)
    no_oulier_data["F"] = no_oulier_data["F"].round(4)
    no_oulier_data["one_minus_F"] = 1 - no_oulier_data["F"]
    no_oulier_data["KN"] = norm.ppf(1 - no_oulier_data["F"])
    no_oulier_data["P_log"] = np.log10(no_oulier_data["Pmax_anual"])

    params = params_calculation(no_oulier_data, sigmaN, yn, sample_size)
    # print(params)

    r2_log_normal = dist_log_normal(no_oulier_data, params)

    r2_pearson = dist_pearson(no_oulier_data, params)

    r2_log_pearson = dist_log_pearson(no_oulier_data, params)

    r2_gumbel_theo = dist_gumbel_theoretical(no_oulier_data, params)

    r2_gumbel_finite = dist_gumbel_finite(no_oulier_data, params)

    distributions = {
        "r2_log_normal": r2_log_normal,
        "r2_pearson": r2_pearson,
        "r2_log_pearson": r2_log_pearson,
        "r2_gumbel_theo": r2_gumbel_theo,
        "r2_gumbel_finite": r2_gumbel_finite
    }
    # print(distributions)

    max_dist = max(distributions, key=distributions.get)
    max_r2 = distributions[max_dist]
    # max_dist = "r2_gumbel_finite"
    # max_r2 = distributions["r2_gumbel_finite"]

    dist_r2 = {"max_dist": max_dist,
               "max_value_r2": max_r2}
    # print("\ndist_r2 ", dist_r2)

    return no_oulier_data, params, dist_r2


def main(no_oulier_data, table_yn_sigman):
    """
    Main function to perform various calculations.
    Args:
        no_oulier_data (DataFrame): The processed dataframe with no outliers.
        table_yn_sigman (DataFrame): The dataframe containing yn and sigmaN values.
    Returns:
        tuple: Returns a tuple containing the parameters and dist_r2 dictionary.
    """

    sample_size = len(no_oulier_data)

    sigmaN, yn = yn_sigman_calculation(table_yn_sigman, sample_size)

    no_oulier_data, params, dist_r2 = dist_calculations(
        no_oulier_data, sigmaN, yn, sample_size)

    # no_oulier_data.to_csv('no_outliers_data.csv', sep=',')

    return no_oulier_data, params, dist_r2
