from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    """
    Renders a placeholder page for the simulator.
    """
    return render(request, 'simulator/simulator.html')
