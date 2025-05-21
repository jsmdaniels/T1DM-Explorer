import numpy as np
import pandas as pd
import seaborn as sns
import time 
import datetime 
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

from libs.CEG import clarke_error_grid

import os 
import time 
import datetime 


def get_record_time(df, unix_time= False):
    record_time = []

    df = df.reset_index()

    for i in range(len(df)):
        device_datetime = datetime.datetime.strptime(df["Time"][i], "%Y-%m-%d %H:%M:%S")

        device_time_min = time.mktime(device_datetime.timetuple())

        if(i==0):
            start_time = device_time_min

        if(unix_time == True):
            record_time.append((device_time_min - start_time)/60)
        else:
            record_time.append(device_datetime)

    return np.array(record_time)

def generate_5_min_intervals(day, type = 'sparse'):
    """
    Generates a DatetimeIndex representing 5-minute intervals for a given day.

    Args:
        day: The specific date for which to generate intervals.
        type: The type of intervals to generate. 'sparse' for sparse intervals, 'dense' for dense intervals.

    Returns:
        A pandas DatetimeIndex with 5-minute frequency, an array with timestamps.
    """
    record_time, _intervals_ = [], []
    start_of_day = pd.to_datetime(day)
    end_of_day = start_of_day + datetime.timedelta(days=1)
    # `freq='5min'` or `freq='5T'` creates intervals every 5 minutes.
    # `closed='left'` means the interval includes the start time but not the end time,
    # which is typical for time intervals.
    if type == 'sparse':
        _intervals_1 = pd.date_range(start=start_of_day, end=end_of_day, freq='30min', inclusive= 'left')
        _intervals_2 = pd.date_range(start=start_of_day + datetime.timedelta(minutes=5) , end=end_of_day, freq='30min', inclusive= 'left')
        
        for i in range(len(_intervals_1)):
            _intervals_.append(_intervals_1[i])
            _intervals_.append(_intervals_2[i])

        _intervals_.append(_intervals_1[-1] + pd.Timedelta(minutes=25, seconds=00))
        _intervals_.append(_intervals_2[-1] + pd.Timedelta(minutes=24, seconds=59))
    elif type == 'dense':
        _intervals_1 = pd.date_range(start=start_of_day, end=end_of_day, freq='5min', inclusive= 'left')
        for i in range(len(_intervals_1)):
            _intervals_.append(_intervals_1[i])
        _intervals_.append(_intervals_1[-1] + pd.Timedelta(minutes=4, seconds=59))
    else:
        raise ValueError("Invalid type. Use 'sparse' or 'dense'.")
    
    df = pd.DataFrame({"Time":_intervals_})
    time_intervals = pd.to_datetime(df['Time']).dt.time

    if type == 'sparse':
        for i in range(0, len(df), 2):
            device_datetime = df["Time"][i]
            record_time.append(device_datetime)
    else:
        for i in range(len(df) - 1):
            device_datetime = df["Time"][i]
            record_time.append(device_datetime)

    record_timestamps = np.array(record_time)
    
    return record_timestamps , time_intervals


def get_individual_plot(df, dataset, pID, start_day=0, end_day=1000):
    """
    Function to plot the individual data of a subject
    :param df: DataFrame containing the data
    :param dataset: Dataset name
    :param pID: ID of the subject to plot
    """
    df_ind = df.loc[df['pID'] == pID].reset_index(drop=True)
    
    start_date = pd.to_datetime(df_ind['Time'][0]) + datetime.timedelta(days=start_day)
    start_date = start_date.replace(hour=0, minute=0, second=0)
    end_date = pd.to_datetime(df_ind['Time'][0]) + datetime.timedelta(days=end_day)
    end_date = end_date.replace(hour=0, minute=0, second=0)

    duration = pd.to_datetime(df_ind['Time'])

    mask = duration.between(start_date, end_date)

    df_ind = df_ind[mask].reset_index(drop=True)

    timestamp = get_record_time(df_ind)

    sns.set_style("darkgrid")
    sns.set_context("notebook")
   
    fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True)
    ax1.plot(timestamp, df_ind['CGM'], label='CGM', color='green')
    ax1.scatter(timestamp, df_ind['BGM'], color='k',label = 'BGM', alpha=0.5, marker='o')
    ax2.scatter(timestamp, df_ind['CRB'].replace(0,np.nan), label='Carbohydrates', color='blue', marker='s')
    ax3 = ax2.twinx()
    if(dataset == 'OhioT1DM'):
        ax3.plot(timestamp, df_ind['INS'], label='Insulin', color='red')
    else:
        ax3.scatter(timestamp, df_ind['INS'].replace(0,np.nan), label='Insulin', color='red', marker='*')
        
    hh_mm = DateFormatter('%H')
    ax2.xaxis.set_major_formatter(hh_mm)
    ax1.set_title(f'Individual data for {pID}')
    ax1.set_ylabel('Glucose (CGM)')
    ax2.set_xlabel('Time (h)')
    ax2.set_ylabel('Carb (g)')
    ax3.set_ylabel('Insulin(U)')
    ax1.legend(loc='best')
    ax2.legend(loc='upper left')
    ax3.legend(loc='upper right')
    # ax2.tick_params(axis = 'x', rotation=90)
    ax1.grid()
    ax2.grid()
    return fig

def get_daily_glycaemic_variation(df, dataset, pID, type = 'sparse'):
    """
    Function to plot the daily glycaemic variation of a subject
    :param df: DataFrame containing the data
    :param dataset: Dataset name
    :param pID: ID of the subject to plot
    :param type: Type of intervals to generate. 'sparse' for sparse intervals, 'dense' for dense intervals.
    :return: A matplotlib.figure.Figure object
    """


    daily_glucose_mean, daily_glucose_std = [], []

    df_ind = df.loc[df['pID'] == pID]

    today = datetime.date.today() # You can use any date
    print(f"Generating 5-minute intervals for: {today}\n")
    timestamps, time_intervals  = generate_5_min_intervals(today, type)

    if type == 'dense':
        step = 1
    elif type == 'sparse':
        step = 2
    else:
        raise ValueError("Invalid type. Use 'sparse' or 'dense'.")

    for k in range(1, len(time_intervals), step):
        start_time = time_intervals[k-1]
        end_time = time_intervals[k]
        df_time = pd.to_datetime(df_ind['Time']).dt.time
        mask = (df_time >= start_time) & (df_time < end_time)

        daily_glucose_mean.append(df_ind.loc[mask, 'CGM'].mean())
        daily_glucose_std.append(df_ind.loc[mask, 'CGM'].std())
    
    bg_mean = np.array(daily_glucose_mean)
    bg_std = np.array(daily_glucose_std)

    sns.set_style("darkgrid")
    sns.set_context("notebook")
    fig, ax = plt.subplots(figsize=(15, 5))
    ax.plot(timestamps, bg_mean, label='Mean daily glucose', color='blue')
    ax.fill_between(timestamps, bg_mean - bg_std, bg_mean + bg_std, color='blue', alpha=0.2)
    hh_mm = DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(hh_mm)
    ax.set_title(f'Daily glycaemic variation for ID: {pID}')
    ax.set_ylabel('Glucose (CGM)')
    ax.set_xlabel('Time')
    ax.legend(loc='best')
    ax.grid()
    return fig
    

def get_group_daily_glycaemic_variation(df, profiles, category, type = 'sparse'):
    """
    Function to plot the daily glycaemic variation of a subject
    :param df: DataFrame containing the data
    :param profiles: DataFrame containing the profiles of the population
    :param dataset: Dataset name
    :param category: Category to group participants
    :param type: Type of intervals to generate. 'sparse' for sparse intervals, 'dense' for dense intervals.
    :return: A matplotlib.figure.Figure object
    """


    # dataset_path = './datasets/{}/raw/'.format(dataset)
    # pIDs = get_pIDs(dataset_path)
    # df = prepare_data(dataset_path, pIDs)

    today = datetime.date.today() # You can use any date
    print(f"Generating 5-minute intervals for: {today}\n")
    timestamps, time_intervals  = generate_5_min_intervals(today, type)

    if type == 'dense':
        step = 1
    elif type == 'sparse':
        step = 2
    else:
        raise ValueError("Invalid type. Use 'sparse' or 'dense'.")

    cat_array = profiles[category].unique()
    colours=['r','g','b','c','m','y','k','orange','purple','pink']
    sns.set_style("darkgrid")
    sns.set_context("notebook")

    fig, ax = plt.subplots(figsize=(15, 5))
    ax.set_title(f'Daily glycaemic variation stratified by {category}')
    ax.set_xlabel('Time')
    ax.set_ylabel('Value')

    for n,i in enumerate(cat_array):
        
        mask = profiles[category] == i
        inc = profiles.loc[mask, 'pID']
        pIDs = inc.unique()
        df_group = df.loc[df['pID'].isin(pIDs)]
        daily_glucose_mean, daily_glucose_std = [], []
        print(f"Generating plot for: {i}:{pIDs}\n")

        for k in range(1, len(time_intervals), step):
            start_time = time_intervals[k-1]
            end_time = time_intervals[k]
            df_time = pd.to_datetime(df_group['Time']).dt.time
            mask = (df_time >= start_time) & (df_time < end_time)

            daily_glucose_mean.append(df_group.loc[mask, 'CGM'].mean())
            daily_glucose_std.append(df_group.loc[mask, 'CGM'].std())

        bg_mean = np.array(daily_glucose_mean)
        bg_std = np.array(daily_glucose_std)
        ax.plot(timestamps, bg_mean, label= i, color=colours[n])
        ax.fill_between(timestamps, bg_mean - bg_std, bg_mean + bg_std, color=colours[n], alpha=0.2)
        
    hh_mm = DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(hh_mm)
    ax.legend(loc='best') 
    ax.grid()
    return fig
    

def compare_measures(df, pIDs, ax):

    df_CEG = df[df['pID'].isin(pIDs)]
    df_CEG = df_CEG[['BGM', 'CGM']].dropna()

    reference = df_CEG['CGM'].values
    finger_stick = df_CEG['BGM'].values
    title = " "

    ax, _zone_, zone_index = clarke_error_grid(finger_stick, reference, ax)
    zone = _zone_/(0.01*np.sum(_zone_))
    
    return ax, zone, zone_index

def get_glucose_risk(glucose, measure):

    bgi = ((np.log(glucose)**1.084)- 5.381)
    if measure == 'LBGI':
        r = min(0, bgi)
    else:
        r = max(0, bgi)
    risk = 22.77 *(r**2)

    return risk

def get_glycaemic_measures(df, measure, max_thresh = 180, min_thresh = 70):

    if measure == 'SD':
        glycaemic_measure = df['CGM'].std()
    elif measure == 'CV':
        glycaemic_measure = 100*(df['CGM'].std()/df['CGM'].mean())
    elif measure == 'CONGA24':
        temp = []
        for k in range (288, len(df)):
            conga = abs(df['CGM'][k] - df['CGM'][k-288])
            temp.append(conga)
        glycaemic_measure = np.nanstd(np.array(temp))
    elif measure == 'GMI':
        glycaemic_measure = 3.31 + (0.02392 * df['CGM'].mean())
    elif measure == 'j-index':
        glycaemic_measure = 0.001 * (df['CGM'].mean() + df['CGM'].std())**2
    elif measure == 'MODD':
        temp = []
        for k in range (288, len(df)):
            modd = abs(df['CGM'][k] - df['CGM'][k-288])
            temp.append(modd)
        glycaemic_measure = np.nanmean(np.array(temp))
    elif measure == 'eA1c':
        glycaemic_measure = (46.7 + df['CGM'].mean())/28.7
    elif measure == 'HBGI' or measure == 'LBGI':
        temp = []
        reference = df['CGM'].dropna().values
        for glucose_value in reference:
            r_i = get_glucose_risk(glucose_value, measure)
            if(r_i != 0):
                temp.append(r_i)
        glycaemic_measure = np.mean(np.array(temp))
    elif measure == 'ADDR':
        temp = []
        start_date = pd.to_datetime(df['Time'][df.index[0]])
        start_date = start_date.replace(hour=0, minute=0, second=0)
        end_date = pd.to_datetime(df['Time'][df.index[-1]])
        NoD = end_date - start_date

        for i in range(0, NoD.days + 1):
            start_of_day = start_date + datetime.timedelta(days = i)
            end_of_day = start_date + datetime.timedelta(days = i + 1)

            duration = pd.to_datetime(df['Time'])
            mask = duration.between(start_of_day, end_of_day)
            df_day = df[mask].reset_index(drop=True)

            reference = df_day['CGM'].dropna().values
            r_l, r_h = [], []
            for glucose_value in reference:
                hypo_risk = get_glucose_risk(glucose_value, 'LBGI')
                hyper_risk = get_glucose_risk(glucose_value, 'HBGI')

                r_l.append(hypo_risk)
                r_h.append(hyper_risk)

            if r_l and r_h:
                LR = max(r_l)
                HR = max(r_h)
                temp.append(LR + HR)

        glycaemic_measure = np.mean(np.array(temp))
    else:
        raise ValueError("Invalid type. Refer to README for valid measures.")


    return glycaemic_measure


def compare_glycaemic_measures(df, profiles, pIDs, measure, category, hue=None, start_day=0, end_day=1000):
    """
    Function to compare the glycaemic measures of a subject with the population
    :param profiles: DataFrame containing the profiles of the population
    :param df: DataFrame containing the data of the subjects 
    :param grouping: Category to group participants 
    """

    complete_gm = []

    for pID in pIDs:
        df_ind = df.loc[df['pID'] == pID].reset_index(drop=True)

        start_date = pd.to_datetime(df_ind['Time'][0]) + datetime.timedelta(days=start_day)
        start_date = start_date.replace(hour=0, minute=0, second=0)
        end_date = pd.to_datetime(df_ind['Time'][0]) + datetime.timedelta(days=end_day)
        end_date = end_date.replace(hour=0, minute=0, second=0)

        duration = pd.to_datetime(df_ind['Time'])

        mask = duration.between(start_date, end_date)
    
        df_slice = df_ind[mask].reset_index(drop=True)

        glycaemic_measure = get_glycaemic_measures(df_slice, measure)

        complete_gm.append(glycaemic_measure)

    profiles[measure] = complete_gm


    if(profiles[category].dtype == 'int64' or profiles[category].dtype == 'float64'):
        sns_plot = sns.lmplot(data=profiles, x=category , y=measure, hue=hue)
    else:
        sns_plot = sns.catplot(data=profiles, kind ='box', x=category, y=measure, hue=hue)

    return sns_plot
        