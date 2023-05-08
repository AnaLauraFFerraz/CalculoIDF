import numpy as np
import pandas as pd
from scipy.stats import norm
from scipy.special import gammaincinv


def k_coeficient_calculation():
    k_coefficient = pd.DataFrame()
    k_coefficient["Tr_anos"] = [2, 5, 10, 20, 30, 50, 75, 100]
    k_coefficient["exceedance"] = 1 / k_coefficient["Tr_anos"]
    k_coefficient["no_exceedance"] = 1 - k_coefficient["exceedance"]
    return k_coefficient


# usar mesmo k da normal na log-normal
def k_dist_log_normal_calc(k_coefficient, params):
    k_coefficient["k"] = params["meanw"] + \
        norm.ppf(k_coefficient["no_exceedance"]) * params["stdw"]
    k_coefficient["k"] = k_coefficient["k"].round(4)
    return k_coefficient


def k_dist_pearson_calc(k_coefficient, params):
    k_coefficient["YTR"] = gammaincinv(params["alpha"], k_coefficient["no_exceedance"]
                                       ) if params["alpha"] > 0 else gammaincinv(params["alpha"], k_coefficient["exceedance"])

    k_coefficient["k"] = (params["g"] / 2) * \
        (k_coefficient["YTR"] - params["alpha"])

    k_coefficient["k"] = k_coefficient["k"].round(4)
    return k_coefficient


def k_dist_log_pearson_calc(k_coefficient, params):
    k_coefficient["YTRw"] = gammaincinv(params["alphaw"], k_coefficient["no_exceedance"]
                                        ) if params["alphaw"] > 0 else gammaincinv(params["alphaw"], k_coefficient["exceedance"])

    k_coefficient["k"] = (params["gw"] / 2) * \
        (k_coefficient["YTRw"] - params["alphaw"])

    k_coefficient["k"] = k_coefficient["k"].round(4)
    return k_coefficient


def k_dist_gumbel_theoretical_calc(k_coefficient, params):
    k_coefficient["y"] = -np.log(-np.log(k_coefficient["no_exceedance"]))

    k_coefficient["k"] = 0.7797 * k_coefficient["y"] - 0.45
    k_coefficient["k"] = k_coefficient["k"].round(4)
    return k_coefficient


def k_dist_gumbel_finite_calc(k_coefficient, params):
    k_coefficient["y"] = -np.log(-np.log(k_coefficient["no_exceedance"]))

    k_coefficient["k"] = (
        k_coefficient["y"] - params["yn"]) / params["sigman"]

    return k_coefficient


def main(params, dist_r2):

    k_coefficient = k_coeficient_calculation()

    if dist_r2["max_dist"] == 'r2_log_normal':
        k = k_dist_log_normal_calc(k_coefficient, params)
    elif dist_r2["max_dist"] == 'r2_pearson':
        k = k_dist_pearson_calc(k_coefficient, params)
    elif dist_r2["max_dist"] == 'r2_log_pearson':
        k = k_dist_log_pearson_calc(k_coefficient, params)
    elif dist_r2["max_dist"] == 'r2_gumbel_theo':
        k = k_dist_gumbel_theoretical_calc(k_coefficient, params)
    elif dist_r2["max_dist"] == 'r2_gumbel_finite':
        k = k_dist_gumbel_finite_calc(k_coefficient, params)

    # print(k)
    return k
