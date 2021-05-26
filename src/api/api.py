#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 07/05/2021

@author: diego.hahn
'''

import time
import json
import flask
from flask import Flask
#from flask_pymongo import PyMongo

import ssl
import pymongo
from bson import json_util

app = Flask(__name__)
app.config["DEBUG"] = True
#app.config["MONGO_URI"] = "mongodb://nightbuild:tmsa-d14m09@tracking-database-shard-00-00.bxybk.mongodb.net:27017,tracking-database-shard-00-01.bxybk.mongodb.net:27017,tracking-database-shard-00-02.bxybk.mongodb.net:27017/data?ssl=true&replicaSet=atlas-bhiss0-shard-0&authSource=admin&retryWrites=true&w=majority"

#mongo = PyMongo(app,ssl_cert_reqs=ssl.CERT_NONE)
#mongo = pymongo.MongoClient("mongodb://nightbuild:tmsa-d14m09@tracking-database-shard-00-00.bxybk.mongodb.net:27017,tracking-database-shard-00-01.bxybk.mongodb.net:27017,tracking-database-shard-00-02.bxybk.mongodb.net:27017/data?ssl=true&replicaSet=atlas-bhiss0-shard-0&authSource=admin&retryWrites=true&w=majority",ssl_cert_reqs=ssl.CERT_NONE)
mongo = pymongo.MongoClient("mongodb://127.0.0.1:27017/",ssl_cert_reqs=ssl.CERT_NONE)
#db = mongo.db
db = mongo["data"]

base = {
    'equipment':None,
    'serialNumber':None,
    'iop':None,
    'client':None,
    'step':None,
    'timestamp':None
}

# @app.errorhandler(404)
# def API_NotFoundError(error):
#     return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/', methods=['GET'])
def home():
    return "<h1>Hello World</h1>"

@app.route('/api/v1/track/serial/<int:serial_number>', methods=['GET'])
def API_FromTrackTableFindBySerial(serial_number):
    flask.abort(404)

@app.route('/api/v1/track/iop/<string:iop>', methods=['GET'])
def API_FromTrackTableFindByIOP(iop):
    flask.abort(404)

@app.route('/api/v1/track', methods=['GET'])
def API_FromTrackTableGetSteps():
    table = db['track'].aggregate([
        {"$sort" : {"timestamp":pymongo.DESCENDING}},
        {"$project" : { "_id" : 0 ,
                        "timestamp" : 1 ,
                        "step": 1 ,
                        "equipment": 1,
                        "client": 1,
                        "iop":  1,
                        "serialNumber": 1 } }
    ])
    response = flask.jsonify(json.loads(json_util.dumps([entry for entry in table])))
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route('/api/v1/track/last', methods=['GET'])
def API_FromTrackTableGetLastSteps():
    table = db['track'].aggregate([
        {"$sort" : {"timestamp":pymongo.DESCENDING}},
        {"$group"  : {  "_id" : "$serialNumber",
                        "timestamp" : { "$first": "$timestamp" } ,
                        "step": { "$first": "$step"} ,
                        "equipment": { "$first": "$equipment"},
                        "client": { "$first": "$client"},
                        "iop":  {"$first": "$iop"},
                        "serialNumber": {"$first": "$serialNumber"} } },
        {"$project" : { "_id" : 0 ,
                        "timestamp" : 1 ,
                        "step": 1 ,
                        "equipment": 1,
                        "client": 1,
                        "iop":  1,
                        "serialNumber": 1 } }
    ])
    response = flask.jsonify(json.loads(json_util.dumps([entry for entry in table])))
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route('/api/v1/track', methods=['POST'])
def API_InsertStepIntoTrackTable():
    try:
        if not flask.request.json:
            raise Exception

        # O json enviado deve ter pelo menos timestamp e serialNumber
        assert ('timestamp' in flask.request.json) and ('serialNumber' in flask.request.json)

        doc = db['track'].find_one({'serialNumber':flask.request.json['serialNumber']})
        if not doc :
            # Cria um documento do zero, pois não há esse serialNumber no db
            doc = {}

        # Cria um clone do documento base e insere com os valores da entrada no banco e do JSON que foi enviado pelo POST
        entry = base.copy()
        for key in base.keys():
            if key in doc: entry[key] = doc[key]
            if key in flask.request.json: entry[key] = flask.request.json[key]

        db['track'].insert_one(entry)

        return flask.jsonify(message="success")
    except:
        flask.abort(400)
        

if __name__ == "__main__":
    app.run()