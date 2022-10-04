import secrets
from fastapi import FastAPI, Form
import os
import requests
from fastapi import FastAPI, File, UploadFile
import PyPDF2
from urllib.request import Request, urlopen
from PyPDF2 import PdfFileWriter, PdfFileReader
import io

app = FastAPI()


@app.post("/pdf_to_text/upload", tags=['PDF To Text'])
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
