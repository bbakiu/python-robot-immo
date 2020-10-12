import re
from datetime import datetime
from django.http import HttpResponse
from find_apartments.find_apartment import search_immobilienscout

def home(request):
    return HttpResponse("Hello, Django!")

def hello_there(request):
    return HttpResponse("HELLO")

def find_new_places(request):
    q = request.GET.get('q', None)
    if not q:
       return HttpResponse("No q")
    else:
        search_immobilienscout(q)
        return HttpResponse("SUCCESS")

def check_immoscout(request):
    q = request.GET.get('q', None)
    if not q:
       return HttpResponse("No q")
    else:
        search_immobilienscout(q)
        return HttpResponse("SUCCESS")