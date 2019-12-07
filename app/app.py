from flask import Flask, jsonify
from pymongo import MongoClient
from py2neo import Graph,Node,Relationship
import json
from flask import request
import random

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
        "total_path_length": total_path_length
    })


@application.route("/type", methods=["GET"])
def typeRestaurants():
    print("ioiiii")
    type_restaurants = mongo_client['velo']['cat_restaurants'].find({}, {"_id": 0, "Nom": 1})

    response = [item['Nom'] for item in type_restaurants]
    return json.dumps(response, ensure_ascii=False, indent="\t")


@application.route("/starting-point", methods=["GET"])
def startingpoint():
     req_data = request.json
     list_typeresto = req_data['type']
     max_lengh= req_data['maximum_length']
     cat_restaurants = mongo_client['velo']['cat_restaurants'].find({"Nom": {"$in": list_typeresto}}, {"ID": 1, "Nom": 1} )
     match_typeresto =[str(int(item['ID']))for item in cat_restaurants]
     max_lengh+= max_lengh*0.1
     type_restaurants = mongo_client['velo']['restaurants'].find({"Categories": {"$in": match_typeresto}}, {"Nom": 1, "Latitude": 1, "Longitude": 1})
     response = [[item['Latitude'],item['Longitude']] for item in type_restaurants]

     nombreRandom= random.randint(1, len(response))
     resto_depart =response[nombreRandom]
     query = "MATCH (b:Intersection) WITH b, distance(point(b), point({{latitude:{0}, longitude:{1}}})) AS dist RETURN b.x AS lat,b.y AS lon, dist ORDER BY dist".format(
     resto_depart[0], resto_depart[1])
     return {
         "starting_point": {"type": "Point", "coordinates": resto_depart}
     }
     #result = neo4j_graph.run(query).data()
    #if result.records[0].dist <= max_lengh:
    #return {
     #     "starting_point": {"type":"Point", "coordinates":[result.records[0].lat, result.records[0].lon]}
     #}



application.run('0.0.0', APP_PORT, debug=True)