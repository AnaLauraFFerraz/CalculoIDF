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

    df.to_csv('./csv/stats.csv', sep=',')

    output_file_path = "./csv/stats.pkl"
    save_data(df, output_file_path)

    return df


def save_data(data, file_path):
    with open(file_path, 'wb') as file:
        pickle.dump(data, file)


if __name__ == "__main__":
    dist_calculations(df)
