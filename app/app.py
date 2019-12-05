from flask import Flask, jsonify
from pymongo import MongoClient
from py2neo import Graph
import json

import os
MONGO_PORT = 27017
NEO4J_PORT = 7687
APP_PORT = 8080

if 'production' in os.environ:
    mongo_server_uri = "mongo:{}".format(MONGO_PORT)
    neo4j_server_uri = "bolt://neo4j"
else :
    mongo_server_uri = "localhost:{}".format(MONGO_PORT)
    neo4j_server_uri = "localhost:{}".format(NEO4J_PORT)


mongo_client = MongoClient(mongo_server_uri)
neo4j_graph = Graph(neo4j_server_uri, auth=("neo4j","secret"))
application = Flask('docker-node-mongo')


@application.route("/", methods=["GET"])
def accueil():

    return "running"

    
@application.route("/hearbeat", methods=["GET"])
def hearbeat():
    query ='MATCH (:Intersection)-[rel:EstSurRoute]->(:Intersection) return sum(rel.LongueurRoute) AS total_path_length'
    rep = neo4j_graph.run(query).data()
    total_path_length = round(rep[0]['total_path_length'],2)
    nb_restaurants = mongo_client['velo']['restaurants'].count_documents({})
    
    return jsonify ({
        "nb_restaurants":nb_restaurants,
         "total_path_length":total_path_length
         })

@application.route("/type", methods=["GET"])
def typeRestaurants():  
    print("ioiiii")
    type_restaurants = mongo_client['velo']['cat_restaurants'].find({},{"_id":0, "Nom":1})

    response =[item['Nom']for item in type_restaurants]
    return json.dumps(response, ensure_ascii=False,  indent="\t")
    
#x =json.dumps(rep, skipkeys=False,  check_circular=True, allow_nan=True, cls=None, indent=1, separators=None, default=None, sort_keys=False)

application.run('0.0.0', APP_PORT, debug=True)



