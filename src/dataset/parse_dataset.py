import pickle
import random
from torch.utils.data import DataLoader, Dataset
import datetime as dt
import pandas as pd
import numpy as np
import torch

import os 
import time 

from src.dataset.dataset_replaceBG import get_REPLACE_pIDs, read_REPLACE_df, get_REPLACE_record_time, prepare_REPLACE_data,get_REPLACE_profiles
from src.dataset.dataset_OhioT1DM import get_OHIO_pIDs, read_OHIO_df, get_OHIO_record_time, prepare_OHIO_data, get_OHIO_profiles
# from src.dataset.dataset_OpenAPS import get_OpenAPS_pIDs, read_OpenAPS_df, get_OpenAPS_record_time, prepare_OpenAPS_data
# from src.dataset.dataset_Tidepool import get_Tidepool_pIDs, read_Tidepool_df, get_Tidepool_record_time, prepare_Tidepool_data

def get_pIDs(path):
    """
    Get the patient IDs from the given path.
    Args: path (str): Path to the dataset directory.
    Returns: pIDs (list): List of patient IDs.
    """
    dataset_name = path.split("/")[-3]
    # proj_dir = os.getcwd()
    # dataset_path = '/datasets/{}/raw/'.format(dataset_name)
    # path = proj_dir.replace(os.sep, '/') + dataset_path

    if dataset_name == "OhioT1DM":
        pIDs = get_OHIO_pIDs(path)
    elif dataset_name == "Replace_BG":
        pIDs = get_REPLACE_pIDs(path)
    else:
        pIDs = []
        raise ValueError("Unknown dataset name: {}".format(dataset_name))
    return pIDs

def read_df(path, pID, allBGM = False):
    """
    Get the patient IDs from the given path.
    Args: path (str): Path to the dataset directory.
          pID (int): Patient ID.
          allBGM (bool): If True, include all BGM data. Default is False.
    Returns: pIDs (Dataframe): List of patient IDs.
    """
    dataset_name = path.split("/")[-3]

    if dataset_name == "OhioT1DM":
        df_complete = read_OHIO_df(path, pID)
    elif dataset_name == "Replace_BG":
        df_complete = read_REPLACE_df(path, pID, allBGM)
    else:
        df_complete = []
        raise ValueError("Unknown dataset name: {}".format(dataset_name))
    
    return df_complete

def get_record_time(df_, dataset_name, unix_time= False):
    """
    Get the record time from the given dataframe.
    Args: df_ (Dataframe): Dataframe containing the data.
          unix_time (bool): If True, return time in unix format. Default is False.
    Returns: record_time (list): List of record times.
    """

    if dataset_name == "OhioT1DM":
        record_time = get_OHIO_record_time(df_, unix_time)
    elif dataset_name == "Replace_BG":
        record_time = get_REPLACE_record_time(df_, unix_time)
    else:
        record_time = []
        raise ValueError("Unknown dataset name: {}".format(dataset_name))
    
    return record_time

def get_profiles(path):
    """
    Get the profiles from the given path.
    Args: path (str): Path to the dataset directory.
    Returns: profiles (list): List of profiles.
    """
    dataset_name = path.split("/")[-3]
    # proj_dir = os.getcwd()
    # dataset_path = '/datasets/{}/raw/'.format(dataset_name)
    # path = proj_dir.replace(os.sep, '/') + dataset_path

    pIDs = get_pIDs(path)
    if dataset_name == "OhioT1DM":
        profiles = get_OHIO_profiles(path, pIDs)
    elif dataset_name == "Replace_BG":
        profiles = get_REPLACE_profiles(path, pIDs)
    else:
        profiles = []
        raise ValueError("Unknown dataset name: {}".format(dataset_name))

    return profiles

def get_preprocessed_time(timestamps):
    """
    Get the processed time from the given timestamps.
    Args: timestamps (list): List of timestamps.
    Returns: processed_time (list): List of processed times.
    """
    deviceTime = []
    for i in range(len(timestamps)):
        temp_hr = timestamps[i].hour + timestamps[i].minute / 60
        deviceTime.append(temp_hr)
        processed_time = np.array(deviceTime)

    return processed_time


def prepare_data(file_path, pIDs, viz = False):
    """
    Prepare the data for the given patient IDs.
    Args: file_path (str): Path to the dataset directory.
          pIDs (list): List of patient IDs.
    Returns: data (list): List of prepared data for each patient ID.
    """
    dataset_name = file_path.split("/")[-3]
    # proj_dir = os.getcwd()
    # dataset_path = '/datasets/{}/raw/'.format(dataset_name)
    # file_path = proj_dir.replace(os.sep, '/') + dataset_path

    if dataset_name == "OhioT1DM":
        data = prepare_OHIO_data(file_path, pIDs, viz)
    elif dataset_name == "Replace_BG":
        data = prepare_REPLACE_data(file_path, pIDs, viz)
    else:
        data = []
        raise ValueError("Unknown dataset name: {}".format(dataset_name))
    
    return data