# Library 
import pandas as pd
import numpy as np
import statsmodels.tsa.stattools as ts
pd.options.mode.chained_assignment = None 


def find_pairs(df):
  corr_matrix = df.corr()
  sol = (corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(np.bool))
                    .stack()
                    .sort_values(ascending=False))
  df3 = pd.DataFrame(sol)[pd.DataFrame(sol)[0] > 0.3]
  df3 = df3.reset_index()
  df3.rename(columns = {0: "correlation"}, inplace=True)
  df3 = df3.loc[df3.groupby(['level_0'])['correlation'].idxmax()]
  df3 = df3.loc[df3.groupby(['level_1'])['correlation'].idxmax()]
  df3 = df3.sort_values(by = 'correlation', ascending=False)
  df3 = df3.reset_index(drop = True)
  return df3

def create_pairs_dataframe(df, pair1, pair2):
  pairs = df[[pair1,pair2]]
  return pairs

def calculate_spread_zscore(pair_data, pair1, pair2):
  pair_data['returns'] = np.log(pair_data[pair1]/pair_data[pair2])
  pair_data['mean'] = pair_data['returns'].rolling(window=100,center=False).mean()
  # print ("Creating the spread/zscore column:")
  pair_data['zscore'] = (pair_data['returns'] - pair_data['mean'])/pair_data['returns'].rolling(window=100,center=False).std()

  return pair_data

def signal_generate(pair_data, z_entry_threshold,   #z_enter_threshold for entering a position
                    z_exit_threshold):   #z_exit_threshold for exiting a position

    pair_data['longs'] = (pair_data['zscore'] <= -z_entry_threshold)*1.0   #Long or short decision
    pair_data['shorts'] = (pair_data['zscore'] >= z_entry_threshold)*1.0
    pair_data['exits'] = ((np.abs(pair_data['zscore']) >= z_exit_threshold ) )*1.0

    # print ("Calculating when to be in the market (long and short)")
    for i in pair_data.index[1:]:
      if pair_data['exits'][i] == 1.0 or ((np.abs(pair_data['zscore'][i]-pair_data['zscore'][i-1]) > 1) and (np.abs(pair_data['zscore'][i] + pair_data['zscore'][i-1])<1)):
        pair_data['exits'][i] = 1
        pair_data['longs'][i] = 0
        pair_data['shorts'][i] = 0

    return pair_data

def stonks(pair_data, pair1, pair2):

  pair_data[str(pair1)] = 0.0
  pair_data[str(pair2)] = 0.0
  for i in pair_data.index[1:]:
    if pair_data['longs'][i] == 0.0 and pair_data['shorts'][i] == 0.0 and pair_data['exits'][i] == 0.0:
      pair_data[str(pair1)][i] = pair_data[str(pair1)][i-1]
      pair_data[str(pair2)][i] = pair_data[str(pair2)][i-1]
    if pair_data['longs'][i] == 1.0:
      pair_data[str(pair1)][i] = pair_data[str(pair1)][i-1] + 300
      pair_data[str(pair2)][i] = pair_data[str(pair2)][i-1] - 300
    if pair_data['shorts'][i] == 1.0:
      pair_data[str(pair1)][i] = pair_data[str(pair1)][i-1] - 300
      pair_data[str(pair2)][i] = pair_data[str(pair2)][i-1] + 300
    if pair_data['exits'][i] == 1.0:
      pair_data[str(pair1)][i] = 0
      pair_data[str(pair2)][i] = 0

  return pair_data

def final_data(final_dataframe, pair_data, pair1, pair2):
  final_dataframe['number of shares'][pair1] = pair_data[ str(pair1)].tail(1) + final_dataframe['number of shares'][pair1]
  final_dataframe['number of shares'][pair2] = pair_data[str(pair2)].tail(1) + final_dataframe['number of shares'][pair2]

  return final_dataframe