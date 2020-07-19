from flask import Flask, Response, json, jsonify, request, url_for
from PIL import Image
import cv2
import datetime
import PIL.ImageOps
from SHARP import SHARP



app = Flask(__name__)


@app.errorhandler(404)
def not_found(error=None):

    message = {
        'status': 404,
        'message': 'OCR API: '+request.url+' is configured for MachineName "SHARP"',
    }
    js = json.dumps(message)
    response = Response(js, status=404, mimetype='application/json')
    return response


@app.route('/')
def welcome():
    return ('Welcome')


@app.route('/CenturyLink', methods=['POST'])
def welcomeCTL():
    return ('CenturyLink')


@app.route('/response')
def responses():
    return 'List of '+url_for('responses')


@app.route('/CenturyLink/Mahyco/OCR/<MachineName>', methods=['POST'])
def data(MachineName):
    if (MachineName == "SHARP"):
        #data = request.get_json()
        #image = request.files()
        file = request.files['image']
        img = Image.open(file.stream)
        img.save('intermediate.png', quality=100)
        weight = str(SHARP("intermediate.png"))
        message = {
            # 'MachineName': data['MachineName'],
            # "PoNumber": data['PoNumber'],
            # "BagNumber": data['BagNumber'],
            "Weight": weight,
            "Date": datetime.datetime.now(),
            'url': request.url,
            # "size": [img.width, img.height]
        }
        js = json.dumps(message)
        response = Response(js, status=200, mimetype='application/json')
        response.headers['Link'] = request.url
        return response
    elif (MachineName != "SHARP"):
        return not_found()
