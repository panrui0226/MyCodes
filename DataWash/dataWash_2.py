# usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import dateManager


def load_data(file_name):
    df = pd.read_csv(file_name, index_col=0)
    df.reset_index(drop=True, inplace=True)
    return df


data_df = load_data('WTI_NEW_DATA.csv')
data_df['Date'] = dateManager.split_datetime(data_df['time'])[0]
data_df['Time'] = dateManager.split_datetime(data_df['time'])[1]
data_df['Hour'] = list(map(lambda x: x.hour, data_df['Time'].values))
data_df['Minute'] = list(map(lambda x: x.minute, data_df['Time'].values))
data_df['Second'] = list(map(lambda x: x.second, data_df['Time'].values))
data_df['Microsecond'] = list(map(lambda x: x.microsecond, data_df['Time'].values))

gropued = data_df['ask'].groupby([data_df['Date'], data_df['Hour'], data_df['Minute']])

data_df = data_df.loc[data_df['Second'] == 0]
data_df = data_df.loc[data_df['Microsecond'] == 0]
time_list = list(data_df['time'])

open_list = []
high_list = []
low_list = []
close_list_1 = []
close_list_2 = []

for name, group in gropued:
    high = max(group)
    low = min(group)
    open = list(group)[0]
    l1 = list(set(list(group)))
    try:
        close_1 = l1[-2]
    except:
        close_1 = l1[-1]
    close_2 = list(group)[-1]
    open_list.append(open)
    high_list.append(high)
    low_list.append(low)
    close_list_1.append(close_1)
    close_list_2.append(close_2)

new_data_df = pd.DataFrame()
new_data_df['time'] = time_list
new_data_df['open'] = open_list
new_data_df['high'] = high_list
new_data_df['low'] = low_list
new_data_df['close_1'] = close_list_1
new_data_df['close_2'] = close_list_2
new_data_df['Time'] = dateManager.split_datetime(new_data_df['time'])[1]

# new_data_df.loc[data_df['Time'] == '14:30:00']['close_2']


# a = new_data_df.loc[new_data_df['time'] == ]

# new_data_df['diff'] = new_data_df['close'] - new_data_df['open'].shift(-1)

print(new_data_df)

file = new_data_df.to_csv('WTI_1min.csv')