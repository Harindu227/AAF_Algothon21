from functions import *


def getMyPosition(df):
  df = pd.DataFrame(df).T
  df3 = find_pairs(df)
  final_dataframe = pd.DataFrame(index=np.arange(100), columns=np.arange(1))
  final_dataframe.rename(columns = {0: 'number of shares'}, inplace=True)
  final_dataframe['number of shares'] = 0

  for i in df3.index[0:]:
    pair1 = df3['level_0'][i]
    pair2 = df3['level_1'][i]
    pair_data = create_pairs_dataframe(df, pair1, pair2)
    pair_data = calculate_spread_zscore(pair_data, pair1, pair2)
    pair_data = signal_generate(pair_data, z_entry_threshold=0.8, z_exit_threshold=3.5)
    pair_data = stonks(pair_data, pair1, pair2)
    final_dataframe = final_data(final_dataframe, pair_data, pair1, pair2)
  
  position_array = final_dataframe['number of shares'].to_numpy()
  return position_array