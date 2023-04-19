import pandas as pd
import numpy as np
from scipy.optimize import minimize


def ventechow_calculations(k_coefficient_data, coefficients, params, time_interval):
    ventechow = pd.DataFrame()
    ventechow["Tr_anos"] = [2, 5, 10, 20, 30, 50, 75, 100]

    ventechow["1day"] = params["mean"] + \
        k_coefficient_data["k"] * params["std_dev"]
    ventechow["24h"] = ventechow["1day"] * coefficients["24h"]

    for interval_name in time_interval.keys():
        if interval_name != "24h":
            ventechow[interval_name] = (
                ventechow["1day"] * coefficients[interval_name]) / time_interval[interval_name]

    return ventechow


def transform_dataframe(ventechow, coefficients, time_interval):
    rows = [
        {"Tr (anos)": tr, "td (min)": interval_value * 60, "i_real": (i_24h * coefficients[td]) / interval_value}
        for tr in ventechow["Tr_anos"]
        for td, interval_value in time_interval.items()
        for i_24h in ventechow.loc[ventechow["Tr_anos"] == tr, "24h"]
    ]

    return pd.DataFrame(rows)


def apply_i_calculado(df, parameters_1, parameters_2):
    df["i_calculado"] = df.apply(
        lambda row: calculate_i(row, parameters_1, parameters_2),
        axis=1
    )
    return df


def calculate_i(row, parameters_1, parameters_2):
    k_1, m_1, c_1, n_1 = parameters_1
    k_2, m_2, c_2, n_2 = parameters_2
    
    if 5 <= row["td (min)"] <= 60:
        result = (k_1 * row["Tr (anos)"] ** m_1) / ((c_1 + row["td (min)"]) ** n_1)
    else:
        result = (k_2 * row["Tr (anos)"] ** m_2) / ((c_2 + row["td (min)"]) ** n_2)

    if np.isfinite(result):
        return result
    else:
        return 0


def add_erro_relativo(df):
    df["erro_relativo"] = abs(
        (df["i_calculado"] - df["i_real"]) / df["i_real"]) * 100
    return df


def objective_function(params, df):
    k, m, c, n = params
    try:
        df["i_calculado"] = (k * df["Tr (anos)"] ** m) / \
            ((c + df["td (min)"]) ** n)
        df["erro_relativo"] = abs(
            (df["i_calculado"] - df["i_real"]) / df["i_real"]) * 100
    except (OverflowError, ValueError):
        return np.inf

    return df["erro_relativo"].sum()


def optimize_parameters(df):
    initial_guess = [500, 0.1, 10, 0.7]
    bounds = [(100, 2000), (0, 3), (0, 100), (0, 10)]

    result = minimize(
        objective_function,
        initial_guess,
        args=(df,),
        bounds=bounds,
        method="L-BFGS-B"
    )

    k_opt, m_opt, c_opt, n_opt = result.x
    return k_opt, m_opt, c_opt, n_opt


def recalculate_dataframe(df, k_opt, m_opt, c_opt, n_opt):
    df["i_calculado"] = (k_opt * df["Tr (anos)"] ** m_opt) / ((c_opt + df["td (min)"]) ** n_opt)
    df["erro_relativo"] = abs((df["i_calculado"] - df["i_real"]) / df["i_real"]) * 100
    
    erro_relativo_medio = df["erro_relativo"].mean()
    return erro_relativo_medio, df


def main(k_coefficient_data, disaggregation_data, params, time_interval, dist_r2):

    ventechow_data = ventechow_calculations(
        k_coefficient_data, disaggregation_data, params, time_interval)

    transformed_df = transform_dataframe(
        ventechow_data, disaggregation_data, time_interval)

    initial_parameters = (1000, 0.1, 10, 1)
    transformed_df = apply_i_calculado(transformed_df, initial_parameters, initial_parameters)

    transformed_df = add_erro_relativo(transformed_df)

    k_opt, m_opt, c_opt, n_opt = optimize_parameters(transformed_df)
    print(f"\nValores otimizados: k={k_opt}, m={m_opt}, c={c_opt}, n={n_opt}")

    erro_relativo_medio, transformed_df = recalculate_dataframe(transformed_df, k_opt, m_opt, c_opt, n_opt)
    
    print(f"\nErro relativo médio: {erro_relativo_medio:.2f}%\n")
    print(transformed_df)
    # transformed_df.to_csv('python_app/csv/transformed_df.csv', sep=',')

    return transformed_df
