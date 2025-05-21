import pickle
import random
from torch.utils.data import DataLoader, Dataset
import pandas as pd
import numpy as np
import torch

import os 
import time 
import datetime 

def get_REPLACE_pIDs(path):

    _df_bgm_ = pd.read_csv(path + "HDeviceBGM.txt", sep="|")
    # _df_cgm_ = pd.read_csv(path + "HDeviceCGM.csv", sep="|")
    _df_ins_ = pd.read_csv(path + "HDeviceBolus.txt", sep="|")
    _df_carb_ = pd.read_csv(path + "HDeviceWizard.txt", sep="|")

    a = set(_df_bgm_["PtID"].to_numpy())
    b = set(_df_ins_["PtID"].to_numpy())
    c = set(_df_carb_["PtId"].to_numpy())

    ab = a - b
    ac = a - c
    bc = ab.union(ac)

    pIDs = a.difference(bc)

    return np.array(list(pIDs))



def get_REPLACE_record_time(df_, unix_time= False):
    record_time = []

    df = df_.reset_index()
    _pstart_date_ = "01/01/2016" #dummy date

    for i in range(len(df)):
        numDays = df["DeviceDtTmDaysFromEnroll"][i]
        deviceTime = df["DeviceTm"][i]

        pstart_date = datetime.datetime.strptime(_pstart_date_+"T"+deviceTime, "%d/%m/%YT%H:%M:%S")
        device_datetime = pstart_date + datetime.timedelta(days = int(numDays))

        device_time_min = time.mktime(device_datetime.timetuple())

        if(i==0):
            start_time = device_time_min

        if(unix_time == True):
            record_time.append((device_time_min - start_time)/60)
        else:
            record_time.append(device_datetime)

    return np.array(record_time)

def get_REPLACE_preprocessed_time(timestamps):
    
    deviceTime = []

    for m in range(len(timestamps)):
        temp_hr = pd.Timestamp(timestamps[m]).hour + pd.Timestamp(timestamps[m]).minute/60
        deviceTime.append(temp_hr)

    return np.array(deviceTime)

def read_REPLACE_df(path, pID, allBGM = False):

    _df_bgm_ = pd.read_csv(path + "HDeviceBGM.txt", sep="|")
    _df_cgm_ = pd.read_csv(path + "HDeviceCGM.csv", sep="|")
    _df_ins_ = pd.read_csv(path + "HDeviceBolus.txt", sep="|")
    _df_carb_ = pd.read_csv(path + "HDeviceWizard.txt", sep="|")

    df_bgm_  = _df_bgm_.loc[_df_bgm_["PtID"] == pID]
    df_cgm_  = _df_cgm_.loc[_df_cgm_["PtID"] == pID] 
    df_ins_  = _df_ins_.loc[_df_ins_["PtID"] == pID]
    df_carb_ = _df_carb_.loc[_df_carb_["PtId"] == pID] 

    df_bgm_ = df_bgm_.drop(df_bgm_[df_bgm_.DeviceDtTmDaysFromEnroll < 0].index)
    df_bgm_ = df_bgm_.drop(df_bgm_[df_bgm_.RecordType == 'Ketone'].index)
    if(allBGM == False):
        df_bgm_ = df_bgm_.drop(df_bgm_[df_bgm_.GlucoseValue > 400].index)
    df_bgm  = df_bgm_.sort_values(by=['DeviceDtTmDaysFromEnroll', 'DeviceTm'])

    df_cgm_  = df_cgm_.drop(df_cgm_[df_cgm_.DeviceDtTmDaysFromEnroll < 0].index)
    df_cgm_  = df_cgm_.loc[df_cgm_["RecordType"] == 'CGM'] 
    df_cgm   = df_cgm_.sort_values(by=['DeviceDtTmDaysFromEnroll', 'DeviceTm'])

    df_ins_  = df_ins_.drop(df_ins_[df_ins_.DeviceDtTmDaysFromEnroll < 0].index)
    df_ins   = df_ins_.sort_values(by=['DeviceDtTmDaysFromEnroll', 'DeviceTm'])

    df_carb_  = df_carb_.drop(df_carb_[df_carb_.DeviceDtTmDaysFromEnroll < 0].index)
    df_carb   = df_carb_.sort_values(by=['DeviceDtTmDaysFromEnroll', 'DeviceTm'])

    valueCGM = df_cgm["GlucoseValue"].values
    DeviceTimeCGM  = get_REPLACE_record_time(df_cgm, unix_time=False)

    valueBGM = df_bgm["GlucoseValue"].values
    DeviceTimeBGM   = get_REPLACE_record_time(df_bgm, unix_time=False)

    valueCRB = df_carb["CarbInput"].values
    DeviceTimeCRB  = get_REPLACE_record_time(df_carb, unix_time=False)

    valueINS = df_ins["Normal"].values
    DeviceTimeINS  = get_REPLACE_record_time(df_ins, unix_time=False)

    timeMS = pd.date_range(start=DeviceTimeCGM[0], end=DeviceTimeCGM[-1] + datetime.timedelta(minutes=3), freq='5min')
    timeMS_timestamps = pd.to_datetime(timeMS)
    deviceTime = []
    for m in range(len(timeMS_timestamps)):
        temp_hr = pd.Timestamp(timeMS[m]).hour + pd.Timestamp(timeMS[m]).minute/60
        deviceTime.append(temp_hr)

    pID_vals = [pID]*len(timeMS)

    CGM_vals = [np.nan]*len(timeMS)
    for i in range(len(DeviceTimeCGM)):
        time_UB = DeviceTimeCGM[i] + datetime.timedelta(minutes=3)
        time_LB = DeviceTimeCGM[i] - datetime.timedelta(minutes=3)
        k = np.where((timeMS < time_UB) & (timeMS > time_LB))[0]
        if(len(k) > 0):
            CGM_vals[k[0]] = valueCGM[i]

    BGM_vals = [np.nan]*len(timeMS)
    for i in range(len(DeviceTimeBGM)):
        time_UB = DeviceTimeBGM[i] + datetime.timedelta(minutes=3)
        time_LB = DeviceTimeBGM[i] - datetime.timedelta(minutes=3)
        k = np.where((timeMS < time_UB) & (timeMS > time_LB))[0]
        if(len(k) > 0):
            BGM_vals[k[0]] = valueBGM[i]

    CRB_vals = [0]*len(timeMS)
    for i in range(len(DeviceTimeCRB)):
        time_UB = DeviceTimeCRB[i] + datetime.timedelta(minutes=3)
        time_LB = DeviceTimeCRB[i] - datetime.timedelta(minutes=3)
        k = np.where((timeMS < time_UB) & (timeMS > time_LB))[0]
        if(len(k) > 0):
            CRB_vals[k[0]] = valueCRB[i]

    INS_vals = [0]*len(timeMS)
    for i in range(len(DeviceTimeINS)):
        time_UB = DeviceTimeINS[i] + datetime.timedelta(minutes=3)
        time_LB = DeviceTimeINS[i] - datetime.timedelta(minutes=3)
        k = np.where((timeMS < time_UB) & (timeMS > time_LB))[0]
        if(len(k) > 0):
            INS_vals[k[0]] = valueINS[i]
    
    df_complete = pd.DataFrame({"Time": timeMS_timestamps, "pID": pID_vals, "CGM": CGM_vals, "BGM": BGM_vals, "CRB": CRB_vals, "INS": INS_vals})

    return df_complete


def prepare_REPLACE_data(file_path, pIDs, viz = False):

    maxBG  = 400
    maxINS = 35
    maxCRB = 400

    _df_bgm_ = pd.read_csv(file_path + "HDeviceBGM.txt", sep="|")
    _df_cgm_ = pd.read_csv(file_path + "HDeviceCGM.csv", sep="|")
    _df_ins_ = pd.read_csv(file_path + "HDeviceBolus.txt", sep="|")
    _df_carb_ = pd.read_csv(file_path + "HDeviceWizard.txt", sep="|")

    _df_bgm_ = _df_bgm_.drop(_df_bgm_[_df_bgm_.DeviceDtTmDaysFromEnroll < 0].index)
    _df_bgm_ = _df_bgm_.drop(_df_bgm_[_df_bgm_.RecordType == 'Ketone'].index)
    _df_bgm_ = _df_bgm_.drop(_df_bgm_[_df_bgm_.GlucoseValue > maxBG].index)
    df_bgm_  = _df_bgm_.sort_values(by=["PtID", 'DeviceDtTmDaysFromEnroll', 'DeviceTm'])

    _df_cgm_  = _df_cgm_.drop(_df_cgm_[_df_cgm_.DeviceDtTmDaysFromEnroll < 0].index)
    _df_cgm_  = _df_cgm_.loc[_df_cgm_["RecordType"] == 'CGM'] 
    df_cgm_   = _df_cgm_.sort_values(by=["PtID", 'DeviceDtTmDaysFromEnroll', 'DeviceTm'])

    _df_ins_  = _df_ins_.drop(_df_ins_[_df_ins_.DeviceDtTmDaysFromEnroll < 0].index)
    _df_ins_  = _df_ins_.dropna(subset=["Normal"])
    df_ins_   = _df_ins_.sort_values(by=["PtID", 'DeviceDtTmDaysFromEnroll', 'DeviceTm'])

    _df_carb_  = _df_carb_.drop(_df_carb_[_df_carb_.DeviceDtTmDaysFromEnroll < 0].index)
    _df_carb_ = _df_carb_.dropna(subset=["CarbInput"])
    df_carb_   = _df_carb_.sort_values(by=["PtId", 'DeviceDtTmDaysFromEnroll', 'DeviceTm'])

    for pID in pIDs:
        
        df_bgm  = df_bgm_.loc[df_bgm_["PtID"] == pID]
        df_cgm  = df_cgm_.loc[df_cgm_["PtID"] == pID] 
        df_ins  = df_ins_.loc[df_ins_["PtID"] == pID]
        df_carb = df_carb_.loc[df_carb_["PtId"] == pID] 


        valueCGM = df_cgm["GlucoseValue"].values
        DeviceTimeCGM  = get_REPLACE_record_time(df_cgm, unix_time=False)

        valueBGM = df_bgm["GlucoseValue"].values
        DeviceTimeBGM   = get_REPLACE_record_time(df_bgm, unix_time=False)

        valueCRB = df_carb["CarbInput"].values
        DeviceTimeCRB  = get_REPLACE_record_time(df_carb, unix_time=False)

        valueINS = df_ins["Normal"].values
        DeviceTimeINS  = get_REPLACE_record_time(df_ins, unix_time=False)

        timeMS = pd.date_range(start=DeviceTimeCGM[0], end=DeviceTimeCGM[-1] + datetime.timedelta(minutes=3), freq='5min')
        timeMS_timestamps = pd.to_datetime(timeMS)
        deviceTime = []
        for m in range(len(timeMS_timestamps)):
            temp_hr = pd.Timestamp(timeMS[m]).hour + pd.Timestamp(timeMS[m]).minute/60
            deviceTime.append(temp_hr)

        pID_vals = [pID]*len(timeMS)

        CGM_vals = [np.nan]*len(timeMS)
        for i in range(len(DeviceTimeCGM)):
            time_UB = DeviceTimeCGM[i] + datetime.timedelta(minutes=3)
            time_LB = DeviceTimeCGM[i] - datetime.timedelta(minutes=3)
            k = np.where((timeMS < time_UB) & (timeMS > time_LB))[0]
            if(len(k) > 0):
                CGM_vals[k[0]] = valueCGM[i]
    
        BGM_vals = [np.nan]*len(timeMS)
        for i in range(len(DeviceTimeBGM)):
            time_UB = DeviceTimeBGM[i] + datetime.timedelta(minutes=3)
            time_LB = DeviceTimeBGM[i] - datetime.timedelta(minutes=3)
            k = np.where((timeMS < time_UB) & (timeMS > time_LB))[0]
            if(len(k) > 0):
                BGM_vals[k[0]] = valueBGM[i]

        CRB_vals = [0]*len(timeMS)
        for i in range(len(DeviceTimeCRB)):
            time_UB = DeviceTimeCRB[i] + datetime.timedelta(minutes=3)
            time_LB = DeviceTimeCRB[i] - datetime.timedelta(minutes=3)
            k = np.where((timeMS < time_UB) & (timeMS > time_LB))[0]
            if(len(k) > 0):
                CRB_vals[k[0]] = valueCRB[i]

        INS_vals = [0]*len(timeMS)
        for i in range(len(DeviceTimeINS)):
            time_UB = DeviceTimeINS[i] + datetime.timedelta(minutes=3)
            time_LB = DeviceTimeINS[i] - datetime.timedelta(minutes=3)
            k = np.where((timeMS < time_UB) & (timeMS > time_LB))[0]
            if(len(k) > 0):
                INS_vals[k[0]] = valueINS[i]
        
        df = pd.DataFrame({"Time": timeMS_timestamps, "pID": pID_vals, "CGM": CGM_vals, "BGM": BGM_vals, "CRB": CRB_vals, "INS": INS_vals})
        
        if(pID==pIDs[0]):
            df_complete_ = df
        else:
            frames = [df_complete_, df]
            df_complete_ = pd.concat(frames)

    df_complete = df_complete_.reset_index()
    df_complete = df_complete.drop('index', axis=1) 

    if(viz == False):
        df_complete['CGM'] = df_complete['CGM']/maxBG
        df_complete['BGM'] = df_complete['BGM']/maxBG
        df_complete['CRB'] = df_complete['CRB']/maxCRB
        df_complete['INS'] = df_complete['INS']/maxINS

    return df_complete

    
def get_REPLACE_profiles(file_path, pIDs):
    df_screen = pd.read_csv(file_path + "HScreening.txt", sep="|")
    df_roster = pd.read_csv(file_path + "HPtRoster.txt", sep="|")

    bmi, gender, ages, trtArray, age_range, bmi_catArray  =  [], [], [], [], [], []
    for pID in pIDs:

        df_screen_  = df_screen.loc[df_screen["PtID"] == pID]
        gender.append(df_screen_["Gender"].values[0])

        df_roster_  = df_roster.loc[df_roster["PtID"] == pID]
        age = df_roster_["AgeAsOfEnrollDt"].values[0]
        if(age >= 0 and age < 20):
            age_range.append("(0-20)")
        elif(age >= 20 and age < 40):
            age_range.append("(20-40)")
        elif(age >= 40 and age < 60):
            age_range.append("(40-60)")
        elif(age >= 60):
            age_range.append("(60+)")
        else:
            print("Error in age range")

        ages.append(age)

        trt_label = df_roster_["TrtGroup"].values[0]

        if(trt_label == "CGM Only"):
            trtArray.append("Non-adjunctive")
        else:
            trtArray.append("Adjunctive")

        weight = df_screen_["Weight"].values[0]
        height = df_screen_["Height"].values[0]/100 # cm to m
        _bmi_ = weight/(height**2)
        bmi.append(_bmi_)
        if(_bmi_ >= 0 and _bmi_ < 18.5):
            bmi_catArray.append("Underweight")
        elif(_bmi_ >= 18.5 and _bmi_ < 25):
            bmi_catArray.append("Healthy")
        elif(_bmi_ >= 25 and _bmi_ < 30):
            bmi_catArray.append("Overweight")
        elif(_bmi_ >= 30):
            bmi_catArray.append("Obese")
        else:
            print("Error in age range")
        

    
    df_profile = pd.DataFrame({"pID": pIDs, "BMI": bmi,  "Age": ages,  "Gender":gender, "Age Range":age_range, "Treatment": trtArray, "BMI Category": bmi_catArray})
    
    return df_profile



