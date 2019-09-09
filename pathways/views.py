from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from .forms import ApplicationForm, DocumentUploadForm, AccountAddressForm

# Create your views here.
def home(request):
    context = {}
    if request.session.has_key('app_id'):
        context['app_id'] = request.session['app_id']
    return render(request, 'pathways/home.html', context)

def about(request):
    return render(request, 'pathways/about.html', {'title':'About'})

def apply(request):
    context = {}
    initial = {'app_id': request.session.get('app_id', None)}
    form = ApplicationForm(request.POST or None, initial=initial)
    if request.method == 'POST':
        if form.is_valid():
            # form.save()
            app_id = form.clean_phone_number()
            request.session['app_id'] = app_id
            messages.info(request, f'Test submit!')
            return redirect('/')
    else:
        form = ApplicationForm()
    context['form'] = form
    return render(request, 'pathways/apply.html', context)
