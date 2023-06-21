import json
from django.shortcuts import render, redirect
from .models import Linea
from . import forms
import requests

parada_actual = "parada2"

tiempo_promedio_entre_paradas = 3

# Create your views here.
def parada(request):

    if(request.method == 'POST'):
        # Agregamos una linea
        form = forms.CreateLine(request.POST)
        if(form.is_valid()):
            #save line to db and send to Aplication
            form.save()
        return redirect('/')

    else:
        lineas = get_lineas()
        lineas_horarios = get_horarios(lineas)

        return render(request, 'parada/parada.html', {'parada_actual':parada_actual, 'lineas_horarios': lineas_horarios})
    

def get_lineas():
    print("REALIZO REQUEST get_lineas")
    req = requests.get('http://127.0.0.1:8000/api/get_lineas')
    print(req)
    print("TERMINO REQUEST")
    my_json = req.content.decode('utf8').replace("'", '"')

    # Load the JSON to a Python list & dump it back out as formatted JSON
    data = json.loads(my_json)
    # print(data)
    all_lineas = json.loads(data)
    
    lineas = []
    
    for l in all_lineas:         # filtrar por recorrido con la parada actual
        for k in l['fields']['recorrido'].keys():
            parada = l['fields']['recorrido'][k]
            if parada == parada_actual:
                lineas.append({
                    'linea': l['fields']['linea'],
                    'recorrido': l['fields']['recorrido']
                    })
                break

    return lineas

def list_lineas(lineas):
    lista = []
    for l in lineas:
        lista.append(l['linea'])

    # print('lista de lineas: ', lista)

    return lista


def get_lineas2():  #para probar api IM
    print("REALIZO REQUEST lineas2")
    req = requests.get('https://api.montevideo.gub.uy/api/transportepublico/buses/linevariants')
    print(req)
    print("TERMINO REQUEST")
    my_json = req.content.decode('utf8').replace("'", '"')

    # Load the JSON to a Python list & dump it back out as formatted JSON
    # data = json.loads(my_json)
    # # print(data)
    # lineas = json.loads(data)
    
    return my_json


def get_horarios(lineas):
    print("REALIZO REQUEST mensajes")
    req = requests.get('http://127.0.0.1:8000/api/get_mensajes')
    print(req)
    print("TERMINO REQUEST")
    my_json = req.content.decode('utf8').replace("'", '"')

    # Load the JSON to a Python list & dump it back out as formatted JSON
    data = json.loads(my_json)
    # print(data)
    all_mensajes = json.loads(data)
    
    lista_lineas = list_lineas(lineas)
    mensajes = list(filter(lambda k: k['fields']['linea'] in lista_lineas, all_mensajes))
    
    # print('MENSAJES:')
    # for i in mensajes:
    #     print(i['fields'])

    lineas_horarios = update(lineas, mensajes)
        
    # print("lineas_horarios", lineas_horarios)

    return lineas_horarios

def update(lineas, mensajes):
    
    lineas_horarios = []

    for m in mensajes:
        linea_name = m['fields']['linea']
        timestamp = m['fields']['date']
        next_time = m['fields']['tiempo_proxima_parada']
        prox_parada = m['fields']['proxima_parada']

        linea = None
        for l in lineas:
            if l['linea'] == linea_name:
                linea = l
                break

        if linea == None:
            continue
        # else:
        #     print("linea es: ", linea)

        if not check_parada(prox_parada,linea): # omnibus que ya paso por la parada
            # print('YA PASO')
            continue
        
        if len(lineas_horarios) == 0:
            lineas_horarios.append({
                'linea': linea_name,
                'last_update_time': timestamp,
                'next_time': estimated_time(next_time, prox_parada, linea)
                })
        else:
            linea_exists = False
            for lh in lineas_horarios:
                if lh['linea'] == linea['linea']:
                    if timestamp > lh['last_update_time']:
                        lh['next_time'] = estimated_time(next_time, prox_parada, linea)
                        lh['last_update_time'] = timestamp
                    linea_exists = True
                    break

            if not linea_exists:
                lineas_horarios.append({
                    'linea': linea_name,
                    'last_update_time': timestamp,
                    'next_time': estimated_time(next_time, prox_parada, linea)
                    })
                
    return lineas_horarios
    

def estimated_time(next_time, prox_parada, linea):
    
    if prox_parada == parada_actual:
        return next_time

    time = 0
    start_count = False
    for k in linea['recorrido'].keys():
        parada = linea['recorrido'][k]

        if start_count:
            time += tiempo_promedio_entre_paradas
            if parada == parada_actual:
                return time
        
        if not start_count:
            if parada == prox_parada:
                time += next_time
                start_count = True

    return time
        

                        # estimated_time = 0
                        # start_count = false
                        # for p_item in l.recorrido.paradas_list: # recorrer en sentido contrario al omnibus
                        #     if start_count:
                        #         estimated_time += p_item[1]
                        #     if p_item[0] == response["prox_parada"]:
                        #         start_count = true
                        #         estimated_time += tiempo_prox_parada



def check_parada(prox_parada, linea):

    if prox_parada == parada_actual:
        return True
    
    search_actual = False
    for k in linea['recorrido'].keys():
        parada = linea['recorrido'][k]
        
        if not search_actual:
            if parada == prox_parada:
                search_actual = True
        if search_actual:
            if parada == parada_actual:
                return True
    # print('prox_parada!!: ', prox_parada)
    return False



        
        
    
    
