import pandas as pd
import numpy as np
from scipy.optimize import least_squares, minimize
import pprint


def ventechow_calculations(k_coefficient_data, coefficients, params, time_interval, dist_r2):
    """
    Calculates the initial rainfall intensity values for different return periods and time intervals.
    Args: k_coefficient_data (DataFrame): DataFrame containing k coefficient data.
        coefficients (dict): Coefficients for different time intervals.
        params (dict): Parameters for the distribution.
        time_interval (dict): Time intervals for calculations.
        dist_r2 (dict): A dictionary containing information about the type of distribution.
    Returns: DataFrame: DataFrame with the calculated rainfall intensity values.
    """

    ventechow = pd.DataFrame()
    ventechow["Tr_anos"] = [2, 5, 10, 20, 30, 50, 75, 100]

    if dist_r2["max_dist"] == ("r2_log_normal" or "r2_log_pearson"):
        ventechow["1day"] = params["mean"] + \
            k_coefficient_data["k"] * params["std_dev"]
    else:
        ventechow["1day"] = params["meanw"] + \
            k_coefficient_data["k"] * params["stdw"]

    ventechow["24h"] = ventechow["1day"] * coefficients["24h"]

    for interval_name in time_interval.keys():
        if interval_name != "24h":
            ventechow[interval_name] = (
                ventechow["1day"] * coefficients[interval_name]) / time_interval[interval_name]

    return ventechow


def transform_dataframe(ventechow, coefficients, time_interval):
    """
    Transforms the original DataFrame to facilitate the calculation of the relative error.
    Args: ventechow (DataFrame): DataFrame containing calculated rainfall intensity values.
        coefficients (dict): Coefficients for different time intervals.
        time_interval (dict): Time intervals for calculations.
    Returns: Transformed DataFrame with the appropriate format for calculating relative error.
    """

    rows = [
        {"Tr (anos)": tr, "td (min)": interval_value * 60,
         "i_real": (i_24h * coefficients[td]) / interval_value}
        for tr in ventechow["Tr_anos"]
        for td, interval_value in time_interval.items()
        for i_24h in ventechow.loc[ventechow["Tr_anos"] == tr, "24h"]
    ]
    return pd.DataFrame(rows)


def add_condition(df):
    """
    Adds a column to the DataFrame with the condition based on the time duration.
    Args:
        df (DataFrame): DataFrame to add the condition column to.
    Returns:
        DataFrame: DataFrame with the added condition column.
    """

    df["condition"] = df["td (min)"].apply(lambda x: 1 if 5 <= x <= 60 else 2)
    return df


def calculate_i(params, Tr, td):
    k, m, c, n = params
    result = (k * Tr ** m) / ((c + td) ** n)
    result = np.where(np.isfinite(result), result, 0)
    return result


def apply_i_calculated(df, parameters_1, parameters_2):
    df["i_calculado"] = df.apply(
        lambda row: calculate_i(parameters_1, row['Tr (anos)'], row['td (min)']) if row["condition"] == 1 else calculate_i(
            parameters_2, row['Tr (anos)'], row['td (min)']),
        axis=1
    )
    return df


def add_relative_error(df):
    """
    Adds a column to the DataFrame with the relative error.
    Args:
        df (DataFrame): DataFrame to add the relative error column to.
    Returns:
        DataFrame: DataFrame with the added relative error column.
    """

    df["erro_relativo"] = abs(
        (df["i_calculado"] - df["i_real"]) / df["i_real"]) * 100
    print(
        f"erro_relativo min: {df['erro_relativo'].min()}, max: {df['erro_relativo'].max()}, mean: {df['erro_relativo'].mean()}")

    return df


def objective_function(params, Tr, td, i_real):
    k, m, c, n = params
    i_calculated = (k * Tr ** m) / ((c + td) ** n)
    i_calculated = np.where(np.isfinite(i_calculated), i_calculated, 0)
    relative_error = abs((i_calculated - i_real) / i_real) * 100
    return np.mean(relative_error)


def optimize_parameters(df, initial_guess):
    bounds = [(0, None), (0, None), (0, None), (0, None)]
    result = minimize(
        objective_function,
        initial_guess,
        args=(df['Tr (anos)'], df['td (min)'], df['i_real']),
        method='SLSQP',
        bounds=bounds
    )
    return result.x


def recalculate_dataframe(df, parameters_1, parameters_2):
    """
    Recalculates the DataFrame with the optimal parameters found.
    Args:
        df (DataFrame): DataFrame with the data.
        parameters_1 (tuple): Optimal parameters for the Ven Te Chow equation for condition 1.
        parameters_2 (tuple): Optimal parameters for the Ven Te Chow equation for condition 2.
    Returns:
        float: Mean relative error.
        DataFrame: Recalculated DataFrame.
    """

    df = df.copy()

    df["i_calculado"] = df.apply(
        lambda row: calculate_i(parameters_1, row['Tr (anos)'], row['td (min)']) if row["condition"] == 1 else calculate_i(
            parameters_2, row['Tr (anos)'], row['td (min)']),
        axis=1
    )

    df = add_relative_error(df)

    df_interval_1 = df[df["condition"] == 1]
    df_interval_2 = df[df["condition"] == 2]

    mean_relative_error_1 = df_interval_1["erro_relativo"].mean()
    mean_relative_error_2 = df_interval_2["erro_relativo"].mean()

    # Retornar um dicionário contendo os erros relativos médios para cada intervalo de tempo
    mean_relative_errors = {
        "interval_1": mean_relative_error_1,
        "interval_2": mean_relative_error_2
    }

    return mean_relative_errors, df


def print_formatted_output(output):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(output)


def find_P_max_dist(dist_r2):
    if dist_r2["max_dist"] == 'r2_log_normal':
        P_dist = "P_log_normal"
    elif dist_r2["max_dist"] == 'r2_pearson':
        P_dist = "P_pearson"
    elif dist_r2["max_dist"] == 'r2_log_pearson':
        P_dist = "P_log_pearson"
    elif dist_r2["max_dist"] == 'r2_gumbel_theo':
        P_dist = "P_gumbel_theoretical"
    elif dist_r2["max_dist"] == 'r2_gumbel_finite':
        P_dist = "P_gumbel_finite"

    return P_dist


def main(distribution_data, k_coefficient_data, disaggregation_data, params, time_interval, dist_r2):
    """
    Main function to calculate optimal parameters and recalculate the DataFrame.
    Args:
        k_coefficient_data (DataFrame): DataFrame containing k coefficient data.
        disaggregation_data (dict): Disaggregation data.
        params (dict): Parameters for the distribution.
        time_interval (dict): Time intervals for calculations.
        dist_r2 (dict): A dictionary containing information about the type of distribution.
    Returns:
        dict: Dictionary containing the data for the graph, the optimal parameters, and a flag indicating if the sample size is above 30 years.
    """

    ventechow_data = ventechow_calculations(
        k_coefficient_data, disaggregation_data, params, time_interval, dist_r2)

    transformed_df = transform_dataframe(
        ventechow_data, disaggregation_data, time_interval)

    # initial_parameters = (1000, 0.1, 10, 1)
    transformed_df = add_condition(transformed_df)

    k_opt1, m_opt1, c_opt1, n_opt1 = optimize_parameters(transformed_df, 1)
    print(
        f"Optimized parameters for condition 1: k1={k_opt1}, m1={m_opt1}, c1={c_opt1}, n1={n_opt1}")
    k_opt2, m_opt2, c_opt2, n_opt2 = optimize_parameters(transformed_df, 2)
    print(
        f"Optimized parameters for condition 2: k2={k_opt2}, m2={m_opt2}, c2={c_opt2}, n2={n_opt2}")

    transformed_df = apply_i_calculated(
        transformed_df, (k_opt1, m_opt1, c_opt1, n_opt1), (k_opt2, m_opt2, c_opt2, n_opt2))
    transformed_df = add_relative_error(transformed_df)

    mean_relative_errors, transformed_df = recalculate_dataframe(
        transformed_df, (k_opt1, m_opt1, c_opt1, n_opt1), (k_opt2, m_opt2, c_opt2, n_opt2))

    # print(f"\nErro relativo médio: {erro_relativo_medio}")
    # print("\ntransformed_df :\n", transformed_df)

    P_dist = find_P_max_dist(dist_r2)

    output = {
        "graph_data": {
            "Tr (anos)": transformed_df["Tr (anos)"].values.tolist(),
            "i_real": transformed_df["i_real"].values.tolist(),
            "P_dist": P_dist
        },
        "parameters": {
            "parameters_1": {
                "k1": k_opt1,
                "m1": m_opt1,
                "c1": c_opt1,
                "n1": n_opt1
            },
            "parameters_2": {
                "k2": k_opt2,
                "m2": m_opt2,
                "c2": c_opt2,
                "n2": n_opt2
            }
        },
        "mean_relative_errors": mean_relative_errors,
        "sample_size_above_30_years": params['size'] >= 30
    }

    # print_formatted_output(output)
    # transformed_df.to_csv('transformed_df.csv', sep=',')

    return output
