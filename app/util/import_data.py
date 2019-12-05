from amazonS3_connection import Amazon_connection
from pymongo import MongoClient
from py2neo import Graph
import boto3
import json
import geojson

MONGO_PORT = 27017
NEO4J_PORT = 7687

mongo_client = MongoClient('{}:{}'.format('localhost', MONGO_PORT))
neo4j_graph = Graph('localhost:{}'.format(NEO4J_PORT), auth=("neo4j","secret"))

bucket_name = 'projet-glo7035'
restaurants_filename =  'restaurants.json'
bikelanes_filename = 'Pistes_cyclables.geojson'

conn = Amazon_connection()

json_resto = json.loads(conn.get_object(bucket_name, restaurants_filename))
mongo_client["velo"]["restaurants"].insert(json_resto)


##Import catégorie de restaurants

restaurants_filename =  'restaurantscategories.json'
json_catresto = json.loads(conn.get_object(bucket_name, restaurants_filename))
mongo_client["velo"]["cat_restaurants"].insert(json_catresto)

#Import piste cyclable
geojson_bikelanes = geojson.loads(conn.get_object(bucket_name, bikelanes_filename))


def formatCypherPointQuery(lat,long,nom,longRoad,lat1,long1):
    if longRoad is None:
        longRoad ="Na"
    if nom is None:
        nom="Na"
    requete = "MERGE (n1:Intersection{x:'"+str(lat)+"' ,y:'"+str(long)+"' })"
    requete += "MERGE (n2:Intersection{x:'"+str(lat1)+"' ,y:'"+str(long1)+"' })"
    requete += " MERGE (n1)-[pr:EstSurRoute{Nom:'"+nom+"',LongueurRoute:"+str(longRoad)+" }] ->(n2) RETURN n1"
    return requete

tab = geojson_bikelanes['features']
for feature in range(len(tab)):
    piste = tab[feature]
    pointsIntersect = piste.geometry.coordinates               
    roadName = piste.properties['NOMDESTINATIONSHERBROOKE']
    longRoad = piste.properties['Shape_Length']
    entiteFirst = pointsIntersect[0]
    entiteLast = pointsIntersect[len(pointsIntersect)-1]
    query = formatCypherPointQuery(entiteFirst[1],entiteFirst[0],roadName,longRoad,entiteLast[1],entiteLast[0])
    neo4j_graph.run(query)


