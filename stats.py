import pandas as pd
import numpy as np
import pickle
import scipy.special as sc
from scipy.stats import norm
from scipy.stats import skew

df = pd.read_pickle("./csv/no_outliers_data.pkl")

N = len(df)

df["F"] = (df.index + 1) / (N + 1)
df["one_minus_F"] = 1 - df["F"] # 1 - [m / (N + 1)]

# Cálculos de distribuição

def dist_calculations(df):

    # Normal
    df["KN"] = norm.ppf(1 - df["F"])
    df["P_normal"] = df["Pmax_anual"].mean() + df["Pmax_anual"].std() * df["KN"]

    # Log-Normal
    df["P_log"] = np.log10(df["Pmax_anual"])
    df["WTr"] = df["P_log"].mean() + df["P_log"].std() * df["KN"]
    df["P_log_normal"] = np.power(10, df['WTr'])
    
    # Pearson
    G = skew(df['Pmax_anual'])
    alpha = 4/G**2

    df['YTR'] = np.where(alpha > 0, sc.gammaincinv(
        alpha, df['one_minus_F']), sc.gammaincinv(alpha, df['F']))
    df["KP"] = (G/2)*(df['YTR']-alpha)
    df["P_pearson"] = df["Pmax_anual"].mean() + df["Pmax_anual"].std() * df["KP"]
    
    # Log-Pearson
    Gw = skew(df['P_log'])
    alphaw = 4/Gw**2

    df["YTRw"] = np.where(alphaw > 0, sc.gammaincinv(
        alphaw, df['one_minus_F']), sc.gammaincinv(alphaw, df['F']))
    df["KL_P"] = (Gw/2)*(df['YTRw']-alphaw)
    df["WTr_LP"] = df["P_log"].mean() + df["P_log"].std() * df["KL_P"]

    df["P_log_pearson"] = np.power(10, df['WTr_LP'])
    
    df.to_csv('./csv/stats.csv', sep=',')

    output_file_path = "./csv/stats.pkl"
    save_data(df, output_file_path)

    return df


def save_data(data, file_path):
    with open(file_path, 'wb') as file:
        pickle.dump(data, file)


if __name__ == "__main__":
    dist_calculations(df)
