from flask import Flask, abort, request, jsonify, Response, send_from_directory
from flask_cors import CORS
from ImageAPIHandler import ImageData, LoadBingSearchPage, GetBingSearchImages, LoadImagesFromBrowser

import DocumentAPI
from DocumentAPI import CreateSVGDocument
from SelectionManager import DownloadImage, publicdir, CheckImage, DeleteImage, ClearSelections
from SelectionManager import GetCurrentSelection as gcs
from utils import GenerateRandomString
import json

import datetime

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}}, send_wildcard=True)


# Pre stuff..

ClearSelections("svg")
################################################################################################

@app.route('/')
def sendRoot():
    return "Only a RESTFUL API is supported"





# Routes for Bing Search

@app.route('/api/search/bing', methods=['GET'])
def LoadBingSearchResults():
    query = request.args.get('q',default="",type= str)
    nResults = LoadBingSearchPage(query)
    print(str(nResults)+" found for query = "+query)
    if nResults is not "-1":
        res = Response(status=200,response=str(nResults),content_type='text/plain')
    else:
        res = Response(status=500,response="Server Error. Please restart Server",content_type='text/plain')

    print(res)
    return res

@app.route('/api/search/bing/results', methods=['GET'])
def GetBingSearchResults():
    n = request.args.get('n',default=0,type= int)
    o = request.args.get('o', default=12, type=int)
    result = GetBingSearchImages(n,o)
    ret = None
    if result is not "500" and result is not "501" and result is not "-1":
        ret = Response(response=result, status=200, mimetype=r'application/json')
    else:
        ret = Response(status=500,response="Server Error. Please restart Server",content_type='text/plain')
    return ret

@app.route('/api/search/bing/loadfrombrowser', methods=['GET'])
def UpdateCacheFromBrowser():
    ret = None
    result = LoadImagesFromBrowser()
    if result is not "-1":
        ret = Response(response=result, status=200, mimetype=r'text/plain')
    else:
        ret = Response(status=500, response="Server Error. Please restart Server", content_type='text/plain')

    return ret

# Routes for /api/document/
@app.route('/api/document/create/A4',methods=['POST'])
def CreateDocumentA4():
    return CreateDocument(request.get_json(),"A4")

@app.route('/api/document/create/A3',methods=['POST'])
def CreateDocumentA3():
    return CreateDocument(request.get_json(),"A3")

def CreateDocument(requestdata,size):
    #requestdata = request.get_json()
    #print(requestdata)
    keys = requestdata.keys()
    imagelist = []

    # Load images from folder.
    # Request data is of form
    # 'selection/imagename.jpg'
    for key in keys:
        try:
            image = ImageData(key)
            source = requestdata[key]["src"].split('/')[1]
            image.src = source
            imagelist.append(image)
        except Exception as e:
            print(e)

    CreateSVGDocument(imagelist,size)


    return Response(response="Document Created", status=200, mimetype=r'text/plain')

@app.route('/api/addimage', methods=['POST'])
def AddImage():
    try:
        imagedata = request.get_json()
        print(imagedata)
        url = ""
        if imagedata["type"] == "SD":
            url = imagedata["sdurl"]
        else:
            url = imagedata["hdurl"]
        # Returns the full file path.
        fname = DownloadImage(url)

    except Exception as e:
        print(e)
        return Response(response="Internal Server Error", status=500, mimetype=r'text/plain')

    # Attach the
    return Response(response=publicdir+fname, status=200, mimetype=r'text/plain')

@app.route('/api/removeimage',methods=['GET'])
def RemoveImage():
    fname = request.args.get('q',default="",type=str)
    res = DeleteImage(fname)
    if res:
        return Response(response="OK", status=200, mimetype=r'text/plain')

    return Response(response="NOT FOUND", status=200, mimetype=r'text/plain')

@app.route('/api/checkimage',methods=['GET'])
def CheckImageFile():
    name = request.args.get('q', default="",type=str)
    res = CheckImage(name)
    if res:
        return Response(response="YES", status=200, mimetype=r'text/plain')

    return Response(response="NO", status=200, mimetype=r'text/plain')

@app.route('/api/currentselection', methods=['GET'])
def GetCurrentSelection():
    flist = gcs()
    jres = "{}" # Empty object
    res = {}
    if len(flist) > 0:
        count=1
        for f in flist:
            f = f.split('\\')
            f = f[len(f)-1]
            res[count] = publicdir+f
            count+=1
    res = json.dumps(res)
    print(res)
    return Response(response=res, status=200, mimetype=r'application/json')

# API Version 2.1.0



if __name__ == '__main__':
    app.run(host="127.0.0.1", port=7990)





