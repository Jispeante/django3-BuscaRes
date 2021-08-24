from django.shortcuts import render
from django.http import HttpResponse

from .googlemapsclient import GoogleMapsClient

from statistics import mean

import json

#Global variables
best_places = []
best_place_name = ""
address = ""
API_Key = ""


def get_keys(path):
    with open(path) as f:
        return json.load(f)

def select_best(self):
    best_place = ["_ERROR_", 0, 0, "_ERROR_"] ## Name, rating, user_ratings_total, vicinity
    for item in self:
        if {'rating','user_ratings_total','vicinity'} <= item.keys():
        #if ('rating' in item.keys() & 'user_ratings_total' in item.keys() & 'vicinity' in item.keys()):
            if (calculate_ranking(item['rating'],item['user_ratings_total'])) >= (calculate_ranking(best_place[1],best_place[2])):
                best_place[0] = item['name']
                best_place[1] = item['rating']
                best_place[2] = item['user_ratings_total']
                best_place[3] = item['vicinity']
    return [best_place[0],str(best_place[3])]

def calculate_ranking(rating=0,total=0):
    m = 1000 # Minimum votes to consider the place as good
    C = places_mean(best_places) # mean vote of whole list
    WR = ((total/(total+m))*rating)+((m/(total+m))*C)
    return WR

def places_mean(best_places):
    data = []
    for item in best_places:
        #print(item['name'])
        if 'rating' in item.keys():
            #print(item['rating'])
            data.append(item['rating'])
    #print(data)
    return (mean(data))

def bar_pos(name=""):
    for index, item in enumerate(best_places):
        if item['name']==name:
            return index
    return 1000
    

#### VIEWS
def home(request):
    global best_places
    global best_place_name
    global address
    
    best_places = []
    best_place_name = ""
    address = ""
    return render(request, 'BuscaRes/home.html')
    
def error(request, message='¡Ups! No hemos encontrado nada cerca de esa dirección'):
    return render(request, 'BuscaRes/error.html', {'message': message})
    
def results(request):
    global best_places
    global best_place_name
    global address
    global API_Key
    
    #Crear lista global de sitios, si esta vacio llenarla, si esta llena quitar el sitio que ya mostramos
    #places = client.search("Restaurante Bar", radius=200)
    # COMPROBAR 'status': 'ZERO_RESULTS'
    # best_places es la lista de sitios, si ya fue creada eliminamos el mostrado
    
    #address = ""
    print("DEBUG BEST PLACE NAME:"+best_place_name)
    if best_places:
        if bar_pos(best_place_name)==1000:
            print("ERROR IN PLACE LIST")
            return error(request)
        else:
            best_places.remove(best_places[bar_pos(best_place_name)])
            best_place = ' '.join([str(elem) for elem in select_best(best_places)])
            best_place= "Restaurante "+best_place
            best_places_list = select_best(best_places)
            if best_places_list[0]=='_ERROR_':
                return error(request, '¡Ups! No hemos encontrado ningún restaurante recomendable más cerca de esa dirección')
            best_place_name = best_places_list[0]
             
    #First time running
    else:
        keys = get_keys("BuscaRes/.secret/secret.json")
        API_Key = keys['API_Key']
        address = request.GET.get('address')
        print("API KEY: ",API_Key)
        client = GoogleMapsClient(api_key=API_Key, address_or_postal_code=address)
        
        places = client.search(radius=150)
        print("PLACES STATUS: ",places['status'])
        if places['status']=='ZERO_RESULTS':
                print("PLACES STATUS: ",places['status'])
                #return render(request, 'BuscaRes/error.html', {'address': address})
                return error(request)
        best_places = places['results']
        
        #DEBUG LOG
        file = open("sample.txt", "w", encoding="utf-8")
        file.write("%s = %s\n" %("best_places", best_places))
        file.close()
        #END DEBUG LOG
        
        best_places_list = select_best(best_places)
        if best_places_list[0]=='_ERROR_':
                return error(request, '¡Ups! No hemos encontrado ningún restaurante recomendable más cerca de esa dirección')
        best_place = ' '.join([str(elem) for elem in select_best(best_places)])
        best_place= "Restaurante "+best_place
        best_place_name = best_places_list[0]
    
    #Esto es DEBUG
    print("DEBUG")
    print("####################")
    #best_place = "Restaurante "+places['results'][0]['name']+" "+places['results'][0]['vicinity']
    for item in best_places:
        if {'rating','user_ratings_total','vicinity'} <= item.keys():
            print(item['name'])
            print(item['rating'])
            print(item['user_ratings_total'])
            print(calculate_ranking(item['rating'],item['user_ratings_total']))
            print("\n")
    print("BEST PLACE:",best_place)
    print("\n")
    print("####################")
    #Fin de DEBUG
    
    
    #print("DEBUG Places:"+places)
    destination = "https://www.google.com/maps/embed/v1/place?key="+API_Key+"&q="+best_place
    
    print("DEBUG Destination:"+destination)
    print("DEBUG BEST PLACE NAME:"+best_place_name)
    print(" ")
    return render(request, 'BuscaRes/results.html', {'address': address,'destination': destination})
