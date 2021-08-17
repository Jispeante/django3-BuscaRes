from django.shortcuts import render
from django.http import HttpResponse

from .googlemapsclient import GoogleMapsClient

best_places = []
best_place_name = ""
address = ""

def select_best(self):
    best_place = ["_ERROR_", 0, 0, "_ERROR_"] ## Name, rating, user_ratings_total, vicinity
    for item in self:
        if (item['rating'] >= best_place[1]) and (item['user_ratings_total'] >= best_place[2]):
            best_place[0] = item['name']
            best_place[1] = item['rating']
            best_place[2] = item['user_ratings_total']
            best_place[3] = item['vicinity']
    #return best_place[0]+" "+str(best_place[3])
    return [best_place[0],str(best_place[3])]

def bar_pos(name=""):
    for index, item in enumerate(best_places):
        if item['name']==name:
            return index
    return 1000
    

#### VIEWS
def home(request):
    return render(request, 'BuscaRes/home.html')
    
def results(request):
    global best_places
    global best_place_name
    global address
    
    
    #address = request.GET.get('address')
    #client = GoogleMapsClient(api_key="AIzaSyBwB7F_SNik-a8y9w-G97a-OJML_g-DSVU", address_or_postal_code=address)
        
    
    #Crear lista global de sitios, si esta vacio llenarla, si esta llena quitar el sitio que ya mostramos
    #places = client.search("Restaurante Bar", radius=200)
    # COMPROBAR 'status': 'ZERO_RESULTS'
    # best_places es la lista de sitios, si ya fue creada eliminamos el mostrado
    
    print("DEBUG BEST PLACE NAME:"+best_place_name)
    if best_places:
        if bar_pos(best_place_name)==1000:
            print("ERROR IN PLACE LIST")
        else:
            best_places.remove(best_places[bar_pos(best_place_name)])
            best_place = ' '.join([str(elem) for elem in select_best(best_places)])
            best_place= "Restaurante "+best_place
            best_places_list = select_best(best_places)
            best_place_name = best_places_list[0]
             
    
    else:
        address = request.GET.get('address')
        client = GoogleMapsClient(api_key="AIzaSyBwB7F_SNik-a8y9w-G97a-OJML_g-DSVU", address_or_postal_code=address)
        places = client.search("Restaurante Bar", radius=200)
        best_places = places['results']
        best_places_list = select_best(best_places)
        best_place = ' '.join([str(elem) for elem in select_best(best_places)])
        best_place= "Restaurante "+best_place
        best_place_name = best_places_list[0]
    
    #Esto es DEBUG
    print("DEBUG")
    print("####################")
    #best_place = "Restaurante "+places['results'][0]['name']+" "+places['results'][0]['vicinity']
    for item in best_places:
        print(item['name'])
        print(item['rating'])
        print(item['user_ratings_total'])
        print("\n")
    #Fin de DEBUG
    
    
    #print("DEBUG Places:"+places)
    destination = "https://www.google.com/maps/embed/v1/place?key=AIzaSyBwB7F_SNik-a8y9w-G97a-OJML_g-DSVU&q="+best_place
    #destination = "https://www.google.com/maps/embed/v1/place?key=AIzaSyBwB7F_SNik-a8y9w-G97a-OJML_g-DSVU&q="+address
    print("DEBUG Destination:"+destination)
    print("DEBUG BEST PLACE NAME:"+best_place_name)
    print(" ")
    return render(request, 'BuscaRes/results.html', {'address': address,'destination': destination})
