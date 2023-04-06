import numpy as np
import scipy.special as sc
from scipy.stats import norm, stats, skew


def dist_normal(df, Pmax_anual, mean, std_dev):
    df["KN"] = norm.ppf(1 - df["F"])
    df["P_normal"] = mean + std_dev * df["KN"]

    corr_normal, p_value = stats.pearsonr(Pmax_anual, df["P_normal"])
    r2_normal = corr_normal ** 2
    return r2_normal


def dist_log_normal(df, Pmax_anual):
    df["P_log"] = np.log10(Pmax_anual)
    meanw = df["P_log"].mean()
    std_devw = df["P_log"].std()

    df["WTr"] = meanw + std_devw * df["KN"]
    df["P_log_normal"] = np.power(10, df['WTr'])

    corr_log_normal, p_value = stats.pearsonr(Pmax_anual, df["P_log_normal"])
    r2_log_normal = corr_log_normal ** 2
    return r2_log_normal, meanw, std_devw


def dist_pearson(df, Pmax_anual, mean, std_dev):
    Gn = skew(Pmax_anual)
    alpha = 4/Gn**2

    df['YTR'] = np.where(alpha > 0, sc.gammaincinv(
        alpha, df['one_minus_F']), sc.gammaincinv(alpha, df['F']))
    df["KP"] = (Gn/2)*(df['YTR']-alpha)
    df["P_pearson"] = mean + std_dev * df["KP"]

    corr_pearson, p_value = stats.pearsonr(Pmax_anual, df["P_pearson"])
    r2_pearson = corr_pearson ** 2
    return r2_pearson, Gn, alpha


def dist_log_pearson(df, Pmax_anual, meanw, std_devw):
    Gw = skew(df['P_log'])
    alphaw = 4/Gw**2

    df["YTRw"] = np.where(alphaw > 0, sc.gammaincinv(
        alphaw, df['one_minus_F']), sc.gammaincinv(alphaw, df['F']))

    df["KL_P"] = (Gw/2)*(df['YTRw']-alphaw)
    df["WTr_LP"] = meanw + std_devw * df["KL_P"]
    df["P_log_pearson"] = np.power(10, df['WTr_LP'])

    corr_log_pearson, p_value = stats.pearsonr(Pmax_anual, df["P_log_pearson"])
    r2_log_pearson = corr_log_pearson ** 2
    return r2_log_pearson, Gw, alphaw


def dist_gumbel_theoretical(df, Pmax_anual, mean, std_dev):
    df["y"] = df["one_minus_F"].apply(lambda x: -np.log(-np.log(x)))
    df["KG_T"] = 0.7797 * df["y"] - 0.45
    df["P_gumbel_theoretical"] = mean + std_dev * df["KG_T"]

    corr_gumbel, p_value = stats.pearsonr(
        Pmax_anual, df["P_gumbel_theoretical"])
    r2_gumbel_theo = corr_gumbel ** 2
    return r2_gumbel_theo


def dist_gumbel_finite(df, Pmax_anual, mean, std_dev, sigmaN, yn):
    df["KG_F"] = (df["y"] - yn)/sigmaN
    df["P_gumbel_finite"] = mean + std_dev * df["KG_F"]

    corr_gumbel_finite, p_value = stats.pearsonr(
        Pmax_anual, df["P_gumbel_finite"])
    r2_gumbel_finite = corr_gumbel_finite ** 2
    return r2_gumbel_finite


def yn_sigman_calculation(df, sample_size):
    sigmaN = df.loc[df['Size'] == sample_size, 'sigmaN'].values[0]
    yn = df.loc[df['Size'] == sample_size, 'YN'].values[0]

    return sigmaN, yn


def dist_calculations(df, table_yn_sigman):
    Pmax_anual = df["Pmax_anual"]

    sample_size = len(df)
    mean = Pmax_anual.mean()
    std_dev = Pmax_anual.std()

    df["F"] = (df.index + 1) / (sample_size + 1)
    df["one_minus_F"] = 1 - df["F"]

    sigmaN, yn = yn_sigman_calculation(table_yn_sigman, sample_size)

    r2_normal = dist_normal(df, Pmax_anual, mean, std_dev)
    r2_log_normal, meanw, std_devw = dist_log_normal(df, Pmax_anual)

    r2_pearson, Gn, alpha = dist_pearson(df, Pmax_anual, mean, std_dev)

    r2_log_pearson, Gw, alphaw = dist_log_pearson(
        df, Pmax_anual, mean, std_dev)

    r2_gumbel_theo = dist_gumbel_theoretical(df, Pmax_anual, mean, std_dev)
    r2_gumbel_finite = dist_gumbel_finite(
        df, Pmax_anual, mean, std_dev, sigmaN, yn)

    distributions = {
        "r2_normal": r2_normal,
        "r2_log_normal": r2_log_normal,
        "r2_pearson": r2_pearson,
        "r2_log_pearson": r2_log_pearson,
        "r2_gumbel_theo": r2_gumbel_theo,
        "r2_gumbel_finite": r2_gumbel_finite
    }

    max_key = max(distributions, key=distributions.get)
    max_value_r2 = distributions[max_key]

    params = {
        "mean": mean,
        "std_dev": std_dev,
        "G": Gn,
        "alpha": alpha,
        "meanw": meanw,
        "stdw": std_devw,
        "Gw": Gw,
        "alphaw": alphaw,
        "sigman": sigmaN,
        "yn": yn
    }

    return df, params, max_value_r2


def main(df, table_yn_sigman):
    df, params, max_value_r2 = dist_calculations(df, table_yn_sigman)

    return df, params, max_value_r2


# if __name__ == "__main__":
#     main()
