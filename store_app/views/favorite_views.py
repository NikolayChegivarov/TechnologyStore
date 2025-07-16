# Избраное
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def favorites_view(request):
    return render(request, 'favorites.html')
