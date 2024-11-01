from django.shortcuts import render

# Create your views here.

def index(request):

    context = {
        'exchanges': ['mexc', 'binance']
    }
    return render(request, 'pnds/index.html', context)
