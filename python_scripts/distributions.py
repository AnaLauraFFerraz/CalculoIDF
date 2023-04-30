import numpy as np
import scipy.special as sc
from scipy.special import gammaincinv
from scipy.stats import norm, lognorm, stats, skew
from sklearn.metrics import r2_score


def yn_sigman_calculation(df, sample_size):
    sigmaN = df.loc[df['Size'] == sample_size, 'sigmaN'].values[0]
    yn = df.loc[df['Size'] == sample_size, 'YN'].values[0]

    return sigmaN, yn


def dist_normal(df, mean, std_dev):
    df["KN"] = norm.ppf(1 - df["F"])
    df["P_normal"] = mean + std_dev * df["KN"]

    corr_normal, _ = stats.pearsonr(df["Pmax_anual"], df["P_normal"])
    r2_normal = corr_normal ** 2
    r2_normal = r2_normal.round(4)
    return r2_normal

# def dist_normal(df, mean, std_dev):
#     # Usando a distribuição normal para calcular a precipitação máxima anual esperada
#     df['Pmax_anual_estimada'] = norm.ppf(
#         df['one_minus_F'], loc=mean, scale=std_dev)

#     # Calculando o R²
#     r_squared = r2_score(df['Pmax_anual'], df['Pmax_anual_estimada'])

#     return r_squared


def dist_log_normal(df):
    # Usando a distribuição log-normal para calcular a precipitação máxima anual esperada
    shape, loc, scale = lognorm.fit(df['Pmax_anual'], floc=0)
    df['Pmax_anual_estimada'] = lognorm.ppf(
        df['one_minus_F'], shape, loc, scale)

    # Calculando o R²
    r_squared = r2_score(df['Pmax_anual'], df['Pmax_anual_estimada'])

    return r_squared

# def dist_log_normal(df):
#     df["P_log"] = np.log10(df["Pmax_anual"])
#     meanw = df["P_log"].mean()
#     std_devw = df["P_log"].std()

#     df["WTr"] = meanw + std_devw * df["KN"]
#     df["P_log_normal"] = np.power(10, df['WTr'])

#     corr_log_normal, _ = stats.pearsonr(df["Pmax_anual"], df["P_log_normal"])
#     r2_log_normal = corr_log_normal ** 2
#     r2_log_normal = r2_log_normal.round(4)
#     return r2_log_normal, meanw, std_devw


def dist_pearson(df, mean, std_dev):
    g = skew(df["Pmax_anual"])
    alpha = 4/g**2

    df['YTR'] = np.where(alpha > 0, sc.gammaincinv(
        alpha, df['one_minus_F']), sc.gammaincinv(alpha, df['F']))
    df["KP"] = (g/2)*(df['YTR']-alpha)
    df["P_pearson"] = mean + std_dev * df["KP"]

    corr_pearson, _ = stats.pearsonr(df["Pmax_anual"], df["P_pearson"])
    r2_pearson = corr_pearson ** 2
    r2_pearson = r2_pearson.round(4)
    return r2_pearson, g, alpha


def dist_log_pearson(df, meanw, std_devw):
    Gw = skew(df['P_log'])
    alphaw = 4/Gw**2

    df["YTRw"] = np.where(alphaw > 0, sc.gammaincinv(
        alphaw, df['one_minus_F']), sc.gammaincinv(alphaw, df['F']))

    df["KL_P"] = (Gw/2)*(df['YTRw']-alphaw)
    df["WTr_LP"] = meanw + std_devw * df["KL_P"]
    df["P_log_pearson"] = np.power(10, df['WTr_LP'])

    corr_log_pearson, _ = stats.pearsonr(df["Pmax_anual"], df["P_log_pearson"])
    r2_log_pearson = corr_log_pearson ** 2
    r2_log_pearson = r2_log_pearson.round(4)
    return r2_log_pearson, Gw, alphaw


def dist_gumbel_theoretical(df, mean, std_dev):
    df["y"] = df["one_minus_F"].apply(lambda x: -np.log(-np.log(x)))
    df["KG_T"] = 0.7797 * df["y"] - 0.45
    df["P_gumbel_theoretical"] = mean + std_dev * df["KG_T"]

    corr_gumbel, _ = stats.pearsonr(
        df["Pmax_anual"], df["P_gumbel_theoretical"])
    r2_gumbel_theo = corr_gumbel ** 2
    r2_gumbel_theo = r2_gumbel_theo.round(4)
    return r2_gumbel_theo


def dist_gumbel_finite(df, mean, std_dev, sigmaN, yn):
    df["KG_F"] = (df["y"] - yn)/sigmaN
    df["P_gumbel_finite"] = mean + std_dev * df["KG_F"]

    corr_gumbel_finite, _ = stats.pearsonr(
        df["Pmax_anual"], df["P_gumbel_finite"])
    r2_gumbel_finite = corr_gumbel_finite ** 2
    r2_gumbel_finite = r2_gumbel_finite.round(4)
    return r2_gumbel_finite


def dist_calculations(no_oulier_data, sigmaN, yn, sample_size):
    Pmax_anual = no_oulier_data["Pmax_anual"]

    mean = Pmax_anual.mean()
    std_dev = Pmax_anual.std()

    no_oulier_data["F"] = (no_oulier_data.index + 1) / (sample_size + 1)
    no_oulier_data["F"] = no_oulier_data["F"].round(4)
    no_oulier_data["one_minus_F"] = 1 - no_oulier_data["F"]
    no_oulier_data["KN"] = norm.ppf(1 - no_oulier_data["F"])
    no_oulier_data["P_log"] = np.log10(no_oulier_data["Pmax_anual"])
    meanw = no_oulier_data["P_log"].mean()
    std_devw = no_oulier_data["P_log"].std()

    # print(no_oulier_data)
    r2_normal = dist_normal(no_oulier_data, mean, std_dev)
    print("\nr2_normal", r2_normal)

    r2_log_normal = dist_log_normal(no_oulier_data)
    print("r2_log_normal", r2_log_normal)

    r2_pearson, g, alpha = dist_pearson(
        no_oulier_data, mean, std_dev)
    print("r2_pearson", r2_pearson)

    r2_log_pearson, gw, alphaw = dist_log_pearson(
        no_oulier_data, mean, std_dev)
    print("r2_log_pearson", r2_log_pearson)

    r2_gumbel_theo = dist_gumbel_theoretical(
        no_oulier_data, mean, std_dev)
    print("r2_gumbel_theo", r2_gumbel_theo)

    r2_gumbel_finite = dist_gumbel_finite(
        no_oulier_data, mean, std_dev, sigmaN, yn)
    print("r2_gumbel_finite", r2_gumbel_finite)

    distributions = {
        "r2_normal": r2_normal,
        "r2_log_normal": r2_log_normal,
        "r2_pearson": r2_pearson,
        "r2_log_pearson": r2_log_pearson,
        "r2_gumbel_theo": r2_gumbel_theo,
        "r2_gumbel_finite": r2_gumbel_finite
    }

    # max_dist = max(distributions, key=distributions.get)
    # max_value_r2 = distributions[max_dist]
    max_dist = "r2_log_normal"
    max_r2 = distributions["r2_log_normal"]

    dist_r2 = {"max_dist": max_dist,
               "max_value_r2": max_r2}
    print("\nmax_r2 ", max_r2)

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

    return params, dist_r2


def main(no_oulier_data, table_yn_sigman):
    sample_size = len(no_oulier_data)

    sigmaN, yn = yn_sigman_calculation(table_yn_sigman, sample_size)

    params, dist_r2 = dist_calculations(
        no_oulier_data, sigmaN, yn, sample_size)
    # print("\ndist_r2",dist_r2)

    return params, dist_r2, no_oulier_data
