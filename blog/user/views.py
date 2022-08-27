from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def test_cors(request):
    return render(request,'cors_test.html')


def test_cors_server(request):
    return HttpResponse('cors successful')