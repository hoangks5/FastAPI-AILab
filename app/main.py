import secrets
import os
import requests
from fastapi import FastAPI, File, UploadFile, Form
import PyPDF2
from urllib.request import Request, urlopen
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO

app = FastAPI()


@app.post("/pdf_to_text/upload", tags=['PDF To Text'])
async def pdf_to_text_upload(in_file: UploadFile = File(description='Upload file PDF', default='None')):
    pdfFile = in_file.file
    writer = PdfFileWriter()
    pdfReader = PyPDF2.PdfFileReader(pdfFile)
    for pageNum in range(pdfReader.getNumPages()):
        currentPage = pdfReader.getPage(pageNum)
        writer.addPage(currentPage)
    fileNamePdf = secrets.token_hex(16)+'.pdf'
    outputStream = open(fileNamePdf, "wb")
    writer.write(fileNamePdf)
    outputStream.close()
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(fileNamePdf, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)
    text = retstr.getvalue()
    fileNamePdf = secrets.token_hex(16)+'.pdf'
    outputStream = open(fileNamePdf, "wb")
    writer.write(fileNamePdf)
    outputStream.close()
    fileName = secrets.token_hex(16)+'.txt'
    f = open(fileName, 'w')
    f.write(text)
    f.close()
    url = 'http://128.199.70.52:5001/api/v0/add'
    files = {'file': open(fileName, 'rb')}
    response = requests.post(url, files=files)
    os.remove(fileName)
    os.remove(fileNamePdf)
    return response.json()


@app.post("/pdf_to_text/ipfs_hash", tags=['PDF To Text'])
async def pdf_to_textd_ipfs_hash(input_source_hash: str = Form(description='ipfs hash')):
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
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(fileNamePdf, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)
    text = retstr.getvalue()
    fp.close()
    device.close()
    retstr.close()
    fileName = secrets.token_hex(16)+'.txt'
    f = open(fileName, 'w')
    f.write(text)
    f.close()
    url = 'http://128.199.70.52:5001/api/v0/add'
    files = {'file': open(fileName, 'rb')}
    response = requests.post(url, files=files)
    os.remove(fileName)
    os.remove(fileNamePdf)
    return response.json()
