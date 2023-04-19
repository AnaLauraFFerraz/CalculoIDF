import numpy as np
import pandas as pd
from scipy.stats import norm, gamma, gumbel_r
from scipy.special import gammaincinv
from scipy.optimize import curve_fit


def k_coeficient_calculation():
    k_coefficient = pd.DataFrame()
    k_coefficient["Tr_anos"] = [2, 5, 10, 20, 30, 50, 75, 100]

    k_coefficient["exceedance"] = 1 / k_coefficient["Tr_anos"]

    k_coefficient["no_exceedance"] = 1 - k_coefficient["exceedance"]

    return k_coefficient


def k_dist_normal_calc(k_coefficient):

    k_coefficient["k"] = norm.ppf(k_coefficient["no_exceedance"])

    return k_coefficient


def k_dist_log_normal_calc(k_coefficient, params):
    k_coefficient["k"] = params["meanw"] + norm.ppf(k_coefficient["no_exceedance"]) * params["stdw"]

    return k_coefficient


def k_dist_pearson_calc(k_coefficient, params):
    k_coefficient["YTR"] = gammaincinv(params["alpha"], k_coefficient["no_exceedance"]
                                       ) if params["alpha"] > 0 else gammaincinv(params["alpha"], k_coefficient["exceedance"])
    ytr_values = k_coefficient["YTR"]
    no_exceedance_values = k_coefficient["no_exceedance"]

    k_coefficient_pearson = find_k_coefficient_pearson(
        ytr_values, no_exceedance_values)
    k_coefficient["k"] = k_coefficient_pearson

    return k_coefficient


def pearson_type_III_cdf(x, alpha, loc, beta):
    return gamma.cdf(x, alpha, loc=loc, scale=beta)


def find_k_coefficient_pearson(ytr_values, no_exceedance_values):
    popt, _ = curve_fit(pearson_type_III_cdf, ytr_values, no_exceedance_values, bounds=(
        (0, -np.inf, 0), (np.inf, np.inf, np.inf)))

    alpha, loc, beta = popt
    k_coefficient_pearson = gamma.ppf(
        no_exceedance_values, alpha, loc=loc, scale=beta) - loc

    return k_coefficient_pearson


def k_dist_log_pearson_calc(k_coefficient, params):
    k_coefficient["YTRw"] = gammaincinv(params["alphaw"], k_coefficient["no_exceedance"]
                                        ) if params["alphaw"] > 0 else gammaincinv(params["alphaw"], k_coefficient["exceedance"])

    k_coefficient["k"] = np.exp(params["meanw"] + np.sqrt(
        params["stdw"]) * find_k_coefficient_pearson(k_coefficient["YTRw"], k_coefficient["no_exceedance"]))

    return k_coefficient


def k_dist_gumbel_theoretical_calc(k_coefficient, params):

    # Estime a média e o desvio padrão da distribuição de Gumbel
    loc, scale = gumbel_r.fit(params["yn"])
    mu = loc + scale * 0.5772
    beta = scale * np.pi / np.sqrt(6)

    def calculate_k_dist_gumbel_theoretical(row, mu, beta):
        # Obtenha a probabilidade de não excedência para o valor de k
        no_exceedance = row["no_exceedance"]

        # Calcule y usando a fórmula de Gumbel e os parâmetros estimados (µ e β)
        epsilon = np.finfo(float).eps
        k = mu + beta * np.log(-np.log(no_exceedance + epsilon))

        # Retorne o valor de k correspondente ao valor calculado de y
        return k

    k_coefficient["k"] = k_coefficient.apply(
        lambda row: calculate_k_dist_gumbel_theoretical(row, mu, beta), axis=1)

    return k_coefficient



def k_dist_gumbel_finite_calc(k_coefficient, params):
    k_coefficient["y"] = -np.log(-np.log(k_coefficient["no_exceedance"]))

    k_coefficient["k"] = (
        k_coefficient["y"] - params["yn"]) / params["sigman"]

    return k_coefficient


def main(params, dist_r2):

    k_coefficient = k_coeficient_calculation()

    if dist_r2["max_dist"] == 'r2_normal':
        k = k_dist_normal_calc(k_coefficient)
    elif dist_r2["max_dist"] == 'r2_log_normal':
        k = k_dist_log_normal_calc(k_coefficient, params)
    elif dist_r2["max_dist"] == 'r2_pearson':
        k = k_dist_pearson_calc(k_coefficient, params)
    elif dist_r2["max_dist"] == 'r2_log_pearson':
        k = k_dist_log_pearson_calc(k_coefficient, params)
    elif dist_r2["max_dist"] == 'r2_gumbel_theo':
        k = k_dist_gumbel_theoretical_calc(k_coefficient, params)
    elif dist_r2["max_dist"] == 'r2_gumbel_finite':
        k = k_dist_gumbel_finite_calc(k_coefficient, params)

    return k
