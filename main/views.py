from django.shortcuts import render, redirect
from django.http import HttpResponse


def homepage(request):
    return render(request, "boodlesite/templates/index.html")    


