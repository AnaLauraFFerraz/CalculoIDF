import numpy as np

def set_time_interval():
    time_interval = {
        f"{int(interval)}h" if interval >= 1 else f"{int(interval * 60)}min": interval
        for interval in [24, 12, 10, 8, 6, 4, 2, 1, 0.5, 25/60, 20/60, 15/60, 10/60, 5/60]
    }
    return time_interval

def main(params, dist_r2):
    time_interval = set_time_interval()

    if dist_r2["max_dist"] == "r2_normal":
        precip_24h = params["mean"]
    elif dist_r2["max_dist"] == "r2_log_normal":
        precip_24h = np.exp(params["meanw"])
    elif dist_r2["max_dist"] == "r2_pearson":
        precip_24h = params["yn"]
    elif dist_r2["max_dist"] == "r2_log_pearson":
        precip_24h = np.exp(params["meanw"])
    elif dist_r2["max_dist"] == "r2_gumbel_theo":
        precip_24h = params["yn"]
    elif dist_r2["max_dist"] == "r2_gumbel_finite":
        precip_24h = params["yn"]

    def ven_te_chow_coefficient(precip_24h, interval_24h, interval_sub):
        return (interval_sub / interval_24h) ** (1 / (1 + precip_24h))

    coefficients = {}
    for interval_key, interval in time_interval.items():
        coefficient = ven_te_chow_coefficient(precip_24h, 24, interval)
        # print(f"{interval_key}: {coefficient:.4f}")  # Imprimir valores intermediários
        coefficients[interval_key] = coefficient

    return coefficients, time_interval
