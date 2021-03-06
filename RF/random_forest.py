# -*- coding: utf-8 -*-
"""Random_Forest.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1z2yVOyr2g4TIbkekJ-TI5zY5EfyqDoUY

# **Random Forest**: *Forecasting 30 days time step Closing Price given past 30 days data*
"""

import csv
import random
import math
import operator
import pandas_datareader as web
import numpy as np
import pandas as pd
import datetime
import pandas_datareader.data as web
import matplotlib as mpl
import matplotlib.pyplot as plt
from numpy import asarray
from pandas import DataFrame
from pandas import concat
from sklearn.metrics import mean_absolute_error
from sklearn.ensemble import RandomForestRegressor
from matplotlib import pyplot

"""1. **Importing of data**"""

stock = 'aapl'
country = 'us'

df = pd.read_csv(f'{stock}.{country}.txt', index_col=0)
df.drop('OpenInt', inplace=True, axis=1) # remove OpenInt column seems 
df.tail()

"""2. **Visulizing Data Set**"""

plt.title('Close price history of %s' % stock.upper())
plt.plot(df['Close'])
plt.xlabel('Date')
plt.ylabel('Close Price USD ($)')
plt.xticks([list(df.index.values)[0], list(df.index.values)[-1]])
plt.show()

"""3. **Feature Engineering**"""

def feature_engineering(data):
  df = DataFrame(data)

  #percentage change with respect to open
  df_new = df.loc[:,['Open','Close','Volume']]
  df_new['Relative High'] = (df['High']/ df['Open']) 
  df_new['Relative Low'] = (df['Low']/ df['Open'])
  df_new['Relative Close'] = (df['Close']/ df['Open'])

  return df_new

print("New Data Set: ")
print(new_df.shape)
new_df = feature_engineering(df)
new_df.tail()

"""4. **Spiting Data into Training and Test Set**"""

def split_data(data, ratio):
    num_of_data = data.shape[0]
    num_of_training = round(num_of_data * ratio)
    num_of_testing = num_of_data - num_of_training  


    return data[:-num_of_testing], data[-num_of_testing:]

train_set, test_set = split_data(new_df, 0.8)

print("Train Set:")
print(train_set.shape)

print("Test Set")
print(test_set.shape)

"""5. **Converting Time Series Data for Supervised Learning**"""

def convert_data(data, time_step_history, time_step_forecast):
    df_con = DataFrame()

    cols = []
    headers = ['Relative High', 'Relative Low', 'Relative Close', 'Volume']

    for i in range(0,time_step_history+1):
      for j in range(0, len(headers)):
          c = headers[j]
          # print(headers)
          header = f'{c}(t-{i})'
          df_con[header] = data[c].shift(i)
          cols.append(header)

    df_con['Close'] = data['Close']
    label = f'C(t+{time_step_forecast})'
    df_con[label] = data['Close'].shift(-time_step_forecast)/data['Close']

    cols.append(label)
    df_con.dropna(inplace=True)
    return df_con

time_step_history = 30
time_step_forecast = 30
df_converted_train = convert_data(train_set, time_step_history, time_step_forecast)
df_converted_test = convert_data(test_set, time_step_history, time_step_forecast)
print(f"converted train set shape: {df_converted_train.shape}")
print(f"converted test set shape: {df_converted_test.shape}")
print("converted train set: ")
df_converted_train.head()

"""5. **Training Random Forest Model**"""

def split_input_label(data, time_step_forecast):

    label = DataFrame()
    label['Close'] = data['Close']
    temp = f'C(t+{time_step_forecast})'
    label[temp] = data[temp]
    input = data.drop(['Close', temp], axis = 1)

    return input, label


def train_random_forest(input, label):
  train_x = asarray(input)
  train_y = asarray(label[f'C(t+{time_step_forecast})'])
  model = RandomForestRegressor(n_estimators=1000)
  rfm = model.fit(train_x,train_y)
  return rfm



input, label = split_input_label(df_converted_train, time_step_forecast)
print(f"input shape: {input.shape}")
print(f"label shape: {label.shape}")
print("input: ")
input.tail()

model = train_random_forest(input, label)

"""6. **Evaluation**"""

test_input , test_label = split_input_label(df_converted_test, time_step_forecast)  
train_predict = model.predict(asarray(input))
test_predict = model.predict(asarray(test_input))

mse_train = model.score(asarray(input), asarray(label['C(t+30)']))
mse_test = model.score(asarray(test_input), asarray(test_label['C(t+30)']))

#plot training
label['Prediction'] = train_predict 
label['Actual Close'] = label['Close'] * label['C(t+30)']
label['Predicted Close'] = label['Close'] * label['Prediction']
plt.title('Training Set')
plt.plot(label['Actual Close'], label='Actual')
plt.plot(label['Predicted Close'], label='Predicted', alpha=0.5)
plt.xlabel('Date')
plt.ylabel('Close Price USD ($)')
plt.xticks([list(label.index.values)[0], list(label.index.values)[-1]])
plt.legend()
plt.show()

print(f"Train score = {mse_train}")


#plot validation
test_label['Prediction'] = test_predict 
test_label['Actual Close'] = test_label['Close'] * test_label['C(t+30)']
test_label['Predicted Close'] = test_label['Close'] * test_label['Prediction']
plt.title('Test Set')
plt.plot(test_label['Actual Close'], label='Actual')
plt.plot(test_label['Predicted Close'], label='Predicted', alpha=0.5)
plt.xlabel('Date')
plt.ylabel('Close Price USD ($)')
plt.xticks([list(test_label.index.values)[0], list(test_label.index.values)[-1]])
plt.legend()
plt.show()

print(f"Test score = {mse_test}")