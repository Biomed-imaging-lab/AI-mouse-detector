import pandas as pd
import numpy as np

class CSVCombiner:
    def __init__(self, path_to_static_data, path_to_behavior_data, shift):
        self.path_to_static_data = path_to_static_data
        self.path_to_behavior_data = path_to_behavior_data
        self.shift = shift

    def combine(self):
        df_static = pd.read_csv(f'{self.path_to_static_data}.csv')
        df_beh = pd.read_csv(f'{self.path_to_behavior_data}.csv')

        df_beh_shifted = pd.DataFrame(np.nan, index=range(self.shift), columns=df_beh.columns)
        df_beh_shifted = pd.concat([df_beh_shifted, df_beh], ignore_index=False)
        #df_beh_shifted.index = range(self.shift, self.shift + len(df_beh))
        df_beh_shifted.index = range(len(df_beh_shifted))

        result = pd.concat([df_static, df_beh_shifted], axis=1)
        #result.to_csv(f'{self.path_to_behavior_data[:len(self.path_to_behavior_data) - 4]}_data.csv', index=False)
        excel_file = f'{self.path_to_behavior_data[:len(self.path_to_behavior_data) - 4]}_data.xlsx'
        result.to_excel(excel_file, index=False)



