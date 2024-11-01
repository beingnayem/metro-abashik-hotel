from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('signin')
    else:
        return render(request, 'dashboard/dashboard.html')