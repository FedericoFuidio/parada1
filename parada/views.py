import json
from django.shortcuts import render, redirect
from .models import Linea
from . import forms
import requests

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
        print("REALIZO REQUEST")
        req = requests.get('http://127.0.0.1:8000/api/get_lineas')
        print(req)
        print("TERMINO REQUEST")
        my_json = req.content.decode('utf8').replace("'", '"')

        # Load the JSON to a Python list & dump it back out as formatted JSON
        data = json.loads(my_json)
        print(data)

        lineas = Linea.objects.all().order_by('date')

    return render(request, 'parada/parada.html', {'lineas': lineas})
