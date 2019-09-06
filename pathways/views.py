from django.shortcuts import render
from django.http import HttpResponse
from .forms import ApplicationForm, DocumentUploadForm, AccountAddressForm

# Create your views here.
def home(request):
    return render(request, 'pathways/home.html')

def about(request):
    return render(request, 'pathways/about.html', {'title':'About'})

def apply(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            # form.save()
            app_id = form.cleaned_data.get('id')
            request.session['app_id'] = app_id
            return render(request, 'pathways/home.html')
    else:
        form = ApplicationForm()
    return render(request, 'pathways/apply.html', {'form':form})
