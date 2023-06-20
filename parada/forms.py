from django import forms 
from . import models

class CreateLine(forms.ModelForm):
    class Meta:
        model = models.Linea
        fields = ['linea', 'empresa', 'ubicacion']