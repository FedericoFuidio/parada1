import json
from django.shortcuts import render, redirect
from .models import Linea
from . import forms
import requests

parada_actual = "Av. Italia y Bolivia"

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
    print("REALIZO REQUEST")
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
                lineas.append(l['fields']['linea'])
                break

    print(lineas)

    return lineas

def get_horarios(lineas):
    print("REALIZO REQUEST")
    req = requests.get('http://127.0.0.1:8000/api/get_mensajes')
    print(req)
    print("TERMINO REQUEST")
    my_json = req.content.decode('utf8').replace("'", '"')

    # Load the JSON to a Python list & dump it back out as formatted JSON
    data = json.loads(my_json)
    # print(data)
    all_mensajes = json.loads(data)

    mensajes = list(filter(lambda k: k['fields']['linea'] in lineas, all_mensajes))

    for i in mensajes:
        print(i['fields'])

    lineas_horarios = []
    for m in mensajes:
        update(lineas_horarios,m)
        
    # print("lineas_horarios", lineas_horarios)

    return lineas_horarios

def update(lineas_horarios, mensaje):
    
    linea = mensaje['fields']['linea']
    timestamp = mensaje['fields']['date']
    next_time = mensaje['fields']['tiempo_proxima_parada']
    
    if len(lineas_horarios) == 0:
        lineas_horarios.append({
               'linea': linea,
               'last_update_time': timestamp,
               'next_time': next_time
            })
    else:
        l_exists = False
        for l in lineas_horarios:
            
            if l['linea'] == linea and timestamp > l['last_update_time']:
                l['next_time'] = next_time
                l['last_update_time'] = timestamp
                l_exists = True
                    # estimated_time = 0
			        # start_count = false
			        # for p_item in l.recorrido.paradas_list: # recorrer en sentido contrario al omnibus
				    #     if start_count:
					#         estimated_time += p_item[1]
				    #     if p_item[0] == response["prox_parada"]:
					#         start_count = true
					#         estimated_time += tiempo_prox_parada
 
        if not l_exists:
            lineas_horarios.append({
                 'linea': linea,
                 'last_update_time': timestamp,
                 'next_time': next_time,
                 })



        
        
    
    
