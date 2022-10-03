from sys import prefix
from typing import Any
from fastapi import FastAPI, Form
import io
import os
import requests
import pandas as pd
from adtk.visualization import plot
from matplotlib import pyplot as plt
from adtk.detector import ThresholdAD, QuantileAD, InterQuartileRangeAD, PersistAD
from adtk.data import validate_series
from fastapi import FastAPI, File, UploadFile, APIRouter
import secrets 

app = FastAPI(
    title="API hoangks5",
    description="Description of my app.",
    version="1.0",
    docs_url='/docs',
    openapi_url='/openapi.json', # This line solved my issue, in my case it was a lambda function
    redoc_url='/redoc'
)


@app.post("/ThresholdAD/upload_file",tags=["Abnormal Detection Data Time Series"])
async def ThresholdAD_upload_file(in_file: UploadFile=File(...), upper_index: float = Form(title=50000), below_index: float = Form(10000)):
    """
    ThresholdAD compares each time series value with given thresholds.
    In the following example, we detect time points when Price is above 50000 USD or below 10000 USD.
    
    """
    data_upload = in_file.file.read()
    data_upload =  pd.read_csv(io.StringIO(data_upload.decode('utf-8')),index_col="Date", parse_dates=True, squeeze=True)
    s = validate_series(data_upload)
    
    # method thresholdAD
    threshold_ad = ThresholdAD(high=upper_index, low=below_index)
    anomalies = threshold_ad.detect(s)
    plot(s, anomaly=anomalies, ts_linewidth=1, ts_markersize=3, anomaly_markersize=5, anomaly_color='red', anomaly_tag="marker")
    
    # import ipfs
    name_file = secrets.token_hex(nbytes=16)+'.png'
    plt.savefig(name_file) 
    url = 'http://128.199.70.52:5001/api/v0/add'
    files = {'file': open(name_file,'rb')}
    response = requests.post(url, files=files)
    os.remove(name_file)
    return response.json()

@app.post("/ThresholdAD/ipfs_hash",tags=["Abnormal Detection Data Time Series"])
async def ThresholdAD_ipfs_hash(input_source_hash : str = Form(), upper_index: float = Form(), below_index: float = Form()):
    data_text = requests.get('https://gateway.ipfs.airight.io/ipfs/'+input_source_hash).content
    data_text =  pd.read_csv(io.StringIO(data_text.decode('utf-8')),index_col="Date", parse_dates=True, squeeze=True)
    s = validate_series(data_text)
    
    # method thresholdAD
    threshold_ad = ThresholdAD(high=upper_index, low=below_index)
    anomalies = threshold_ad.detect(s)
    plot(data_text, anomaly=anomalies, ts_linewidth=1, ts_markersize=3, anomaly_markersize=5, anomaly_color='red', anomaly_tag="marker")
    
    # import ipfs
    plt.savefig(input_source_hash+'.png')
    url = 'http://128.199.70.52:5001/api/v0/add'
    files = {'file': open('./'+input_source_hash+'.png','rb')}
    response = requests.post(url, files=files)
    os.remove(input_source_hash+'.png')
    return response.json()
    
    
@app.post("/QuantileAD/upload_file",tags=["Abnormal Detection Data Time Series"])
async def QuantileAD_upload_file(in_file: UploadFile=File(...), upper_index: float = Form(), below_index: float = Form()):
    data_upload = in_file.file.read()
    data_upload =  pd.read_csv(io.StringIO(data_upload.decode('utf-8')),index_col="Date", parse_dates=True, squeeze=True)
    s = validate_series(data_upload)
    # method QuantileAD
    
    quantile_ad = QuantileAD(high=upper_index, low=below_index)
    anomalies = quantile_ad.fit_detect(s)
    plot(s, anomaly=anomalies, ts_linewidth=1, ts_markersize=3, anomaly_markersize=5, anomaly_color='red', anomaly_tag="marker")
    
    # import ipfs
    name_file = secrets.token_hex(nbytes=16)+'.png'
    plt.savefig(name_file) 
    url = 'http://128.199.70.52:5001/api/v0/add'
    files = {'file': open(name_file,'rb')}
    response = requests.post(url, files=files)
    os.remove(name_file)
    return response.json()
    
@app.post("/QuantileAD/ipfs_hash",tags=["Abnormal Detection Data Time Series"])
async def QuantileAD_ipfs_hash(input_source_hash : str = Form("QmcF4nzdSzhtxxLa7i3yQ1F3MrU7riasDsRExk6AhCTRx7"), upper_index: float = Form(0.99), below_index: float = Form(0.01)):
    data_text = requests.get('https://gateway.ipfs.airight.io/ipfs/'+input_source_hash).content
    data_text =  pd.read_csv(io.StringIO(data_text.decode('utf-8')),index_col="Date", parse_dates=True, squeeze=True)
    s = validate_series(data_text)
    
    # method QuantileAD
    quantile_ad = QuantileAD(high=upper_index, low=below_index)
    anomalies = quantile_ad.fit_detect(s)
    plot(s, anomaly=anomalies, ts_linewidth=1, ts_markersize=3, anomaly_markersize=5, anomaly_color='red', anomaly_tag="marker")
    
    # import ipfs
    plt.savefig(input_source_hash+'.png')
    url = 'http://128.199.70.52:5001/api/v0/add'
    files = {'file': open('./'+input_source_hash+'.png','rb')}
    response = requests.post(url, files=files)
    os.remove(input_source_hash+'.png')
    return response.json()

@app.post("/InterQuartileRangeAD/upload_file",tags=["Abnormal Detection Data Time Series"])
async def InterQuartileRangeAD_upload_file(in_file: UploadFile=File(...), c: float = Form()):
    data_upload = in_file.file.read()
    data_upload =  pd.read_csv(io.StringIO(data_upload.decode('utf-8')),index_col="Date", parse_dates=True, squeeze=True)
    s = validate_series(data_upload)
    
    # method InterQuartileRangeAD
    iqr_ad = InterQuartileRangeAD(c=c)
    anomalies = iqr_ad.fit_detect(s)
    plot(s, anomaly=anomalies, ts_linewidth=1, ts_markersize=3, anomaly_markersize=5, anomaly_color='red', anomaly_tag="marker")
   
    # import ipfs
    name_file = secrets.token_hex(nbytes=16)+'.png'
    plt.savefig(name_file) 
    url = 'http://128.199.70.52:5001/api/v0/add'
    files = {'file': open(name_file,'rb')}
    response = requests.post(url, files=files)
    os.remove(name_file)
    return response.json()


@app.post("/InterQuartileRangeAD/ipfs_hash",tags=["Abnormal Detection Data Time Series"])
async def InterQuartileRangeAD_ipfs_hash(input_source_hash : str = Form(), c: float = Form()):
    data_text = requests.get('https://gateway.ipfs.airight.io/ipfs/'+input_source_hash).content
    data_text =  pd.read_csv(io.StringIO(data_text.decode('utf-8')),index_col="Date", parse_dates=True, squeeze=True)
    s = validate_series(data_text)
    
    # method InterQuartileRangeAD
    iqr_ad = InterQuartileRangeAD(c=c)
    anomalies = iqr_ad.fit_detect(s)
    plot(s, anomaly=anomalies, ts_linewidth=1, ts_markersize=3, anomaly_markersize=5, anomaly_color='red', anomaly_tag="marker")
   
    # import ipfs
    plt.savefig(input_source_hash+'.png')
    url = 'http://128.199.70.52:5001/api/v0/add'
    files = {'file': open('./'+input_source_hash+'.png','rb')}
    response = requests.post(url, files=files)
    os.remove(input_source_hash+'.png')
    return response.json()

@app.post("/PersistAD/upload_file",tags=["Abnormal Detection Data Time Series"])
async def PersistAD_upload_file(in_file: UploadFile=File(...), c: float = Form(), side: str = Form()):
    data_upload = in_file.file.read()
    data_upload =  pd.read_csv(io.StringIO(data_upload.decode('utf-8')),index_col="Date", parse_dates=True, squeeze=True)
    s = validate_series(data_upload)
    
    # method PersistAD
    persist_ad = PersistAD(c=c, side=side)
    anomalies = persist_ad.fit_detect(s)
    plot(s, anomaly=anomalies, ts_linewidth=1, ts_markersize=3, anomaly_color='red')
   
    # import ipfs
    name_file = secrets.token_hex(nbytes=16)+'.png'
    plt.savefig(name_file) 
    url = 'http://128.199.70.52:5001/api/v0/add'
    files = {'file': open(name_file,'rb')}
    response = requests.post(url, files=files)
    os.remove(name_file)
    return response.json()

@app.post("/PersistAD/ipfs_hash",tags=["Abnormal Detection Data Time Series"])
async def PersistAD_ipfs_hash(input_source_hash : str = Form(), c: float = Form(),side: str = Form()):
    data_text = requests.get('https://gateway.ipfs.airight.io/ipfs/'+input_source_hash).content
    data_text =  pd.read_csv(io.StringIO(data_text.decode('utf-8')),index_col="Date", parse_dates=True, squeeze=True)
    s = validate_series(data_text)
    
    # method PersistAD
    persist_ad = PersistAD(c=c, side=side)
    anomalies = persist_ad.fit_detect(s)
    plot(s, anomaly=anomalies, ts_linewidth=1, ts_markersize=3, anomaly_color='red')
   
    # import ipfs
    plt.savefig(input_source_hash+'.png')
    url = 'http://128.199.70.52:5001/api/v0/add'
    files = {'file': open('./'+input_source_hash+'.png','rb')}
    response = requests.post(url, files=files)
    os.remove(input_source_hash+'.png')
    return response.json()

