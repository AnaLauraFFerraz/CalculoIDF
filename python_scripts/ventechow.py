import pandas as pd
import numpy as np
from scipy.optimize import minimize
import pprint


def ventechow_calculations(k_coefficient_data, coefficients, params, time_interval, dist_r2):
    """
    Calculates the initial rainfall intensity values for different return periods and time intervals.
    Args:
        k_coefficient_data (DataFrame): DataFrame containing k coefficient data.
        coefficients (dict): Coefficients for different time intervals.
        params (dict): Parameters for the distribution.
        time_interval (dict): Time intervals for calculations.
        dist_r2 (dict): A dictionary containing information about the type of distribution.
    Returns:
        DataFrame: DataFrame with the calculated rainfall intensity values.
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
    Args:
        ventechow (DataFrame): DataFrame containing calculated rainfall intensity values.
        coefficients (dict): Coefficients for different time intervals.
        time_interval (dict): Time intervals for calculations.
    Returns:
        DataFrame: Transformed DataFrame with the appropriate format for calculating relative error.
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


def calculate_i(row, parameters):
    """
    Calculates the estimated rainfall intensity.
    Args:
        row (Series): A row of the DataFrame.
        parameters (tuple): Parameters for the Ven Te Chow equation.
    Returns:
        float: Calculated rainfall intensity.
    """

    k, m, c, n = parameters
    result = (k * row["Tr (anos)"] ** m) / ((c + row["td (min)"]) ** n)
    # Use np.where para condição vetorizada
    result = np.where(np.isfinite(result), result, 0)
    return result


def apply_i_calculated(df, parameters_1, parameters_2):
    """
    Applies the Ven Te Chow equation to calculate the estimated rainfall intensity (i_calculated) for each row.
    Args:
        df (DataFrame): DataFrame with the data.
        parameters_1 (tuple): Parameters for the Ven Te Chow equation for condition 1.
        parameters_2 (tuple): Parameters for the Ven Te Chow equation for condition 2.
    Returns:
        DataFrame: DataFrame with the added i_calculated column.
    """

    df["i_calculado"] = df.apply(
        lambda row: calculate_i(
            row, parameters_1) if row["condition"] == 1 else calculate_i(row, parameters_2),
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
    return df


def objective_function(params, df):
    """
    Defines the objective function for optimization.
    Args:
        params (tuple): Parameters for the Ven Te Chow equation.
        df (DataFrame): DataFrame with the data.
    Returns:
        float: Sum of the relative errors.
    """

    df_temp = df.copy()
    k, m, c, n = params
    df_temp["i_calculado"] = calculate_i(df_temp, params)
    df_temp["erro_relativo"] = abs(
        (df_temp["i_calculado"] - df_temp["i_real"]) / df_temp["i_real"]) * 100
    return df_temp["erro_relativo"].sum()


def optimize_parameters(df, condition):
    """
    Uses the L-BFGS-B algorithm to minimize the objective function and find the optimal parameters.
    Args:
        df (DataFrame): DataFrame with the data.
        condition (int): Condition to filter the DataFrame.
    Returns:
        tuple: Optimal parameters for the Ven Te Chow equation.
    """

    initial_guess = [500, 0.1, 10, 0.7]
    bounds = [(100, 2000), (0, 3), (0, 100), (0, 10)]
    df_condition = df[df['condition'] == condition]

    result = minimize(
        objective_function,
        initial_guess,
        args=(df_condition,),
        bounds=bounds,
        method="L-BFGS-B"
    )

    k_opt, m_opt, c_opt, n_opt = result.x

    return k_opt.round(4), m_opt.round(4), c_opt.round(4), n_opt.round(4)


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
        lambda row: calculate_i(
            row, parameters_1) if row["condition"] == 1 else calculate_i(row, parameters_2),
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

    # mean_relative_error = df["erro_relativo"].mean()
    # return mean_relative_error, df

    return mean_relative_errors, df


def print_formatted_output(output):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(output)


def find_P_max_dist(df, dist_r2):
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

    initial_parameters = (1000, 0.1, 10, 1)
    transformed_df = add_condition(transformed_df)
    transformed_df = apply_i_calculated(
        transformed_df, initial_parameters, initial_parameters)

    transformed_df = add_relative_error(transformed_df)

    k_opt1, m_opt1, c_opt1, n_opt1 = optimize_parameters(transformed_df, 1)
    k_opt2, m_opt2, c_opt2, n_opt2 = optimize_parameters(transformed_df, 2)

    # print(f"\ntd de 5 a 60 minutos: k1={k_opt1}, m1={m_opt1}, c1={c_opt1}, n1={n_opt1}")
    # print(f"\ntd acima de 60 minutos: k2={k_opt2}, m2={m_opt2}, c2={c_opt2}, n2={n_opt2}")

    mean_relative_errors, transformed_df = recalculate_dataframe(
        transformed_df, (k_opt1, m_opt1, c_opt1, n_opt1), (k_opt2, m_opt2, c_opt2, n_opt2))

    # print(f"\nErro relativo médio: {erro_relativo_medio}")
    # print("\ntransformed_df :\n", transformed_df)

    P_dist = find_P_max_dist(distribution_data, dist_r2)

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
