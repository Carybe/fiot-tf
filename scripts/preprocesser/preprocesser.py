#!/usr/bin/env python

import pandas as pd
import numpy as np
import sys

#dataset_input_path = "../../datasets/new/br/sp.csv"
#dataset_output_path = "./sp_prep"

args=sys.argv
if len(args) != 3:
	print("This script takes an input csv file and an output preprocessed output file as arguments (in order)")
	exit(1)

dataset_input_path = args[1]
dataset_output_path = args[2]

df = pd.read_csv(dataset_input_path, delimiter=';')

########################################################################################
# FIRST DATA CLEAN
########################################################################################
df_old = df.copy(deep=True)
df = df.dropna()

# General data restriction
# Any numerical data that equals 0.0 is probably a
# default value for missing data at the server

df = df[df['Time'] > 0]

df = df[df['Temperature'] > -100]

df = df[df['Dew Point'] > -100]

df = df[df['Humidity'] >= 0]

# Purged at `.dropna()`
# df = df[df['Wind']]

df = df[df['Wind Speed'] >= 0]

df = df[df['Wind Gust'] >= 0]

df = df[df['Pressure'] >= 10]

df = df[df['Precip.'] >= 0]

# Purged at `.dropna()`
# df = df[df['Condition']]

## WU restrictions (it sets 0ºC for data it doesn't have):
df = df.loc[(df['Temperature'] <= -0.0001) | (df['Temperature'] >= 0.0001)]
df = df.loc[(df['Dew Point']   <= -0.0001) | (df['Dew Point'] >=   0.0001)]

dropped_data_ratio = 1 - df['Condition'].count() / df_old['Condition'].count()
print("In the first data clean, %.2f%% of the datapoints were dropped" %(dropped_data_ratio * 100))

########################################################################################
# DATA GROUP AND ENHANCE
########################################################################################

# Translate from Epoch
df['TimeAgg'] = pd.to_datetime(df['Time'],unit='s')

# "has_rain" definition:

# If it has precipitation -> it has rain
def yprecipitations(preciptation):
  return preciptation > 0

# If it has "Drizzle", "Rain", "Shower" or "Storm" in its Condition -> it has rain
def yconditions(condition):
  import re
  if re.match(".*(Drizzle|Rain|Shower|Storm).*", condition):
    return 1
  else:
    return 0

# Checks whether the dataframe has at least 1% of precipitation field filled
if df[df["Precip."] > 0]['Precip.'].count() / df['Condition'].count() > 0.01:
  target_field = 'Precip.'
  threshold_func = yprecipitations
  print("Using Preciptation feature for has_rain definition")

# Otherwise, we need to inspect the conditions
else:
  target_field = 'Condition'
  threshold_func = yconditions
  print("Using Condition feature for has_rain definition")

labelfunc = np.vectorize(threshold_func)
rain_class = labelfunc(df[[target_field]])
df[['has_rain']] = rain_class

rain_ratio = df[df['has_rain'] == True]['has_rain'].count() / df['has_rain'].count()
print('It rains %.2f%% of the time in the original dataset' %(100*rain_ratio))

# Set time as index
df.set_index('TimeAgg',inplace=True, drop=True)

# Resample data in 6h slots
df6hp = df[['Temperature',
            'Humidity',
            'Pressure',
            'Precip.',
            'has_rain']].resample('6h').agg({'min',
                                             'max',
                                             'mean',
                                             lambda x: x.quantile(0.7),
                                             lambda y: y.quantile(0.9),
                                             lambda z: z.quantile(0.3),
                                             lambda o: o.quantile(0.1),
                                             lambda a: (a > a.shift()).sum(),
                                             lambda b: (b < b.shift()).sum(),
                                             lambda c: (c == c.shift()).sum()})
# MIN, MAX, MEAN, 70PERCENTILE, 90PERCENTILE, 30PERCENTILE, 10PERCENTILE, RISE, FALL, STEADY

df6hp.columns = ["_".join(x) for x in df6hp.columns.ravel()]
# Selecting has_rain_max as target variable
df6hp['has_rain'] = df6hp['has_rain_max']
df6hp.dtypes

# Data enhancing
# For each feature and "lambda" feature, group the last 8 measurements,
# by shifting its data: Feature_steady_(N) = Feature_steady_(N-1).shift()

for feature in ['Pressure', 'Temperature', 'Humidity', 'Precip.']:
  df6hp['%s_steady_1' % (feature)] = df6hp['%s_mean' % (feature)].shift()
  df6hp['%s_min_steady_1' % (feature)] = df6hp['%s_min' % (feature)].shift()
  df6hp['%s_max_steady_1' % (feature)] = df6hp['%s_max' % (feature)].shift()
  for i in range(7):
    df6hp['%s_steady_%d' % (feature, i+2)] = df6hp['%s_steady_%d' % (feature, i+1)].shift()
    df6hp['%s_min_steady_%d' % (feature, i+2)] = df6hp['%s_min_steady_%d' % (feature, i+1)].shift()
    df6hp['%s_max_steady_%d' % (feature, i+2)] = df6hp['%s_max_steady_%d' % (feature, i+1)].shift()
  for j in range(7):
    df6hp['%s_<lambda_%d>_1' % (feature, j)] = df6hp['%s_<lambda_%d>' % (feature, j)].shift()
    for i in range(7):
      df6hp['%s_<lambda_%d>_%d' % (feature, j, i+2)] = df6hp['%s_<lambda_%d>_%d' % (feature, j, i+1)].shift()


########################################################################################
# SECOND DATA CLEAN
########################################################################################
df6hp_old = df6hp.copy(deep=True)

# 2nd Data clean, removing NaNs generated from grouping shifted columns
df6hp = df6hp.dropna()

# This column was dropped at df6hp definition
# df6hp = df6hp.drop(columns=['TimeAgg'])

# Features that have not been grouped are removed
non_agg_feat_list = list()
for feature in ['Pressure', 'Temperature', 'Humidity', 'Precip.','has_rain']:
  non_agg_feat_list.append("%s_mean" % (feature))
  non_agg_feat_list.append("%s_min" % (feature))
  non_agg_feat_list.append("%s_max" % (feature))
  for i in range(7):
    non_agg_feat_list.append("%s_<lambda_%d>" % (feature, i))
df6hp.drop(columns=non_agg_feat_list, inplace=True)

dropped_data_ratio = 1 - df6hp['has_rain'].count() / df6hp_old['has_rain'].count()
print("In the second data clean, %.2f%% of the datapoints were dropped" %(dropped_data_ratio * 100))

rain_ratio = df6hp[df6hp['has_rain'] == True]['has_rain'].count() / df6hp['has_rain'].count()
print('It rains %.2f%% of the time in cleaned/preprocessed dataset' %(100*rain_ratio))

# Export the enhaced dataset
df6hp.to_csv(dataset_output_path)
