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
import PyPDF2
from urllib.request import Request, urlopen
from PyPDF2 import PdfFileWriter, PdfFileReader

app = FastAPI(
    title="API for AI Market",
    description="",
    version="1.0",
    docs_url='/ailab/docs',
    openapi_url='/openapi.json', # This line solved my issue, in my case it was a lambda function
    redoc_url='/ailab/redoc'
)

@app.post("/ThresholdAD/upload_file",tags=["Abnormal Detection Data Time Series"])
async def ThresholdAD_upload_file(in_file: UploadFile=File(description="Upload file .csv"), high_value: float = Form(50000), low_value: float = Form(10000)):
    """
    ThresholdAD compares each time series value with given thresholds.
    In the following example, we detect time points when Price is above 50000 USD or below 10000 USD.
    
    """
    data_upload = in_file.file.read()
    data_upload =  pd.read_csv(io.StringIO(data_upload.decode('utf-8')),index_col="Date", parse_dates=True, squeeze=True)
    s = validate_series(data_upload)
    
    # method thresholdAD
    threshold_ad = ThresholdAD(high=high_value, low=low_value)
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
async def ThresholdAD_ipfs_hash(input_source_hash : str = Form('QmcF4nzdSzhtxxLa7i3yQ1F3MrU7riasDsRExk6AhCTRx7'), high_value: float = Form(50000), low_value: float = Form(10000)):
    """
    ThresholdAD compares each time series value with given thresholds.
    In the following example, we detect time points when Price is above 50000 USD or below 10000 USD.
    
    """
    data_text = requests.get('https://gateway.ipfs.airight.io/ipfs/'+input_source_hash).content
    data_text =  pd.read_csv(io.StringIO(data_text.decode('utf-8')),index_col="Date", parse_dates=True, squeeze=True)
    s = validate_series(data_text)
    
    # method thresholdAD
    threshold_ad = ThresholdAD(high=high_value, low=low_value)
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
async def QuantileAD_upload_file(in_file: UploadFile=File(description='Upload file .csv'), high_value: float = Form(0.99), low_value: float = Form(0.01)):
    """
    QuantileAD compares each time series value with historical quantiles.

In the following example, we detect time points when Price is above 99% percentile or below 1% percentile.
    
    """
    data_upload = in_file.file.read()
    data_upload =  pd.read_csv(io.StringIO(data_upload.decode('utf-8')),index_col="Date", parse_dates=True, squeeze=True)
    s = validate_series(data_upload)
    # method QuantileAD
    
    quantile_ad = QuantileAD(high=high_value, low=low_value)
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
async def QuantileAD_ipfs_hash(input_source_hash : str = Form("QmcF4nzdSzhtxxLa7i3yQ1F3MrU7riasDsRExk6AhCTRx7"), high_value: float = Form(0.99), low_value: float = Form(0.01)):
    """
    QuantileAD compares each time series value with historical quantiles.

In the following example, we detect time points when Price is above 99% percentile or below 1% percentile.
    
    """
    data_text = requests.get('https://gateway.ipfs.airight.io/ipfs/'+input_source_hash).content
    data_text =  pd.read_csv(io.StringIO(data_text.decode('utf-8')),index_col="Date", parse_dates=True, squeeze=True)
    s = validate_series(data_text)
    
    # method QuantileAD
    quantile_ad = QuantileAD(high=high_value, low=low_value)
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
async def InterQuartileRangeAD_upload_file(in_file: UploadFile=File(...), c: float = Form(0.5,description="""c (float, or 2-tuple (float, float), optional) – Factor used to determine the bound of normal range (betweeen Q1-c*IQR and Q3+c*IQR). If a tuple (c1, c2), the factors are for lower and upper bound respectively.
                                                                                          
    Default: 3.0.""")):
    """
    InterQuartileRangeAD is another widely used detector based on simple historical statistics is based on interquartile range (IQR). When a value is out of the range defined by [𝑄1−𝑐×𝐼𝑄𝑅, 𝑄3+𝑐×𝐼𝑄𝑅] where 𝐼𝑄𝑅=𝑄3−𝑄1 is the difference between 25% and 75% quantiles.

This detector is usually preferred to QuantileAD in the case where only a tiny portion or even none of training data is anomalous.
    """
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
async def InterQuartileRangeAD_ipfs_hash(input_source_hash : str = Form('QmcF4nzdSzhtxxLa7i3yQ1F3MrU7riasDsRExk6AhCTRx7'), c: float = Form(0.5,description="""c (float, or 2-tuple (float, float), optional) – Factor used to determine the bound of normal range (betweeen Q1-c*IQR and Q3+c*IQR). If a tuple (c1, c2), the factors are for lower and upper bound respectively.
                                                                                          
    Default: 3.0.""")):
    """
    InterQuartileRangeAD is another widely used detector based on simple historical statistics is based on interquartile range (IQR). When a value is out of the range defined by [𝑄1−𝑐×𝐼𝑄𝑅, 𝑄3+𝑐×𝐼𝑄𝑅] where 𝐼𝑄𝑅=𝑄3−𝑄1 is the difference between 25% and 75% quantiles.

This detector is usually preferred to QuantileAD in the case where only a tiny portion or even none of training data is anomalous.
    """
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
async def PersistAD_upload_file(in_file: UploadFile=File(...), c: float = Form(3.0,description="""c (float, optional) – Factor used to determine the bound of normal range based on historical interquartile range.
                                                                               
    Default: 3.0."""), side: str = Form('both',description="""If “both”, to detect anomalous positive and negative changes;

If “positive”, to only detect anomalous positive changes;

If “negative”, to only detect anomalous negative changes.


    Default: “both”.""")):
    """
    PersistAD compares each time series value with its previous values. Internally, it is implemented as a pipenet with transformer DoubleRollingAggregate.

In the following example, we detect anomalous positive changes of price.

By default, PersistAD only check one previous value, which is good at capturing additive anomaly in short-term scale, but not in long-term scale because it is too near-sighted.

In the following example, it fails to capture meaningful drops of price in a longer time scale.
"""
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
async def PersistAD_ipfs_hash(input_source_hash : str = Form('QmcF4nzdSzhtxxLa7i3yQ1F3MrU7riasDsRExk6AhCTRx7'), c: float = Form(3.0,description="""c (float, optional) – Factor used to determine the bound of normal range based on historical interquartile range.
                                                                               
    Default: 3.0."""), side: str = Form('both',description="""If “both”, to detect anomalous positive and negative changes;

If “positive”, to only detect anomalous positive changes;

If “negative”, to only detect anomalous negative changes.


    Default: “both”.""")):
    """
    PersistAD compares each time series value with its previous values. Internally, it is implemented as a pipenet with transformer DoubleRollingAggregate.

In the following example, we detect anomalous positive changes of price.

By default, PersistAD only check one previous value, which is good at capturing additive anomaly in short-term scale, but not in long-term scale because it is too near-sighted.

In the following example, it fails to capture meaningful drops of price in a longer time scale.
"""
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

@app.post("/speech_to_text/upload_file",tags=["Speech To Text"])
async def speech_to_text_upload_file(in_file: UploadFile = File(description='Upload file .wav (PCM 16 bit)') ):
    data_text = in_file.file
    import speech_recognition as sr
    r = sr.Recognizer()
    harvard = sr.AudioFile(data_text)
    with harvard as source:
        audio = r.record(source)
    text = r.recognize_google(audio,language="vi-VI")
    return {'data':text}

@app.post("/pdf_to_text/upload_file", tags=['PDF To Text'])
async def pdf_to_text(in_file: UploadFile = File(description='Upload file PDF')):
    pdfFile = in_file.file
    pdfReader = PyPDF2.PdfFileReader(pdfFile)
    pageObj = ""
    for page in pdfReader.pages:
        pageObj += page.extractText() + "\n"
    fileName = secrets.token_hex(16)+'.txt'
    f = open(fileName, 'w')
    f.write(pageObj)
    f.close()
    url = 'http://128.199.70.52:5001/api/v0/add'
    files = {'file': open(fileName, 'rb')}
    response = requests.post(url, files=files)
    os.remove(fileName)
    return response.json()


@app.post("/pdf_to_text/ipfs_hash", tags=['PDF To Text'])
async def pdf_to_text(input_source_hash: str = Form(description='ipfs hash')):
    url = "https://gateway.ipfs.airight.io/ipfs/"+input_source_hash
    writer = PdfFileWriter()
    remoteFile = urlopen(Request(url)).read()
    memoryFile = io.BytesIO(remoteFile)
    pdfFile = PdfFileReader(memoryFile)
    for pageNum in range(pdfFile.getNumPages()):
        currentPage = pdfFile.getPage(pageNum)
        writer.addPage(currentPage)
    fileNamePdf = secrets.token_hex(16)+'.pdf'
    outputStream = open(fileNamePdf, "wb")
    writer.write(fileNamePdf)
    outputStream.close()
    pdfFile = open(fileNamePdf, 'rb')
    pdfreader = PyPDF2.PdfFileReader(pdfFile)
    pageObj = ""
    for page in pdfreader.pages:
        pageObj += page.extractText() + "\n"
    fileName = secrets.token_hex(16)+'.txt'
    f = open(fileName, 'w')
    f.write(pageObj)
    f.close()
    url = 'http://128.199.70.52:5001/api/v0/add'
    files = {'file': open(fileName, 'rb')}
    response = requests.post(url, files=files)
    os.remove(fileName)
    os.remove(fileNamePdf)
    return response.json()