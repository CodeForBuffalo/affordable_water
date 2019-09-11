from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from .forms import ApplicationForm, DocumentForm, AccountForm
from django.views.generic.edit import FormView
from .models import Application

# Create your views here.
def home(request):
    context = {}
    if request.session.has_key('app_id'):
        context['app_id'] = request.session['app_id']
    return render(request, 'pathways/home.html', context)

def about(request):
    return render(request, 'pathways/about.html', {'title':'About'})

class ApplicationView(FormView):
    template_name = 'pathways/apply.html'
    form_class = ApplicationForm
    success_url = '/docs/'

    def form_valid(self, form):
        application = form.save(commit=False)
        app_id = application.id
        self.request.session['app_id'] = app_id
        return super().form_valid(form)

class AccountView(FormView):
    template_name = 'pathways/apply.html'
    form_class = AccountForm
    success_url = ''

    def form_valid(self, form):
        account = form.save()
        app_id = application.id
        self.request.session['app_id'] = app_id
        return super().form_valid(form)

class DocumentView(FormView):
    template_name = 'pathways/apply.html'
    form_class = AccountForm
    success_url = ''

    def form_valid(self, form):
        documents = form.save(commit=False)
        if self.request.session['app_id']:
            documents.application = self.request.session['app_id'] = app_id 
        return super().form_valid(form)

def apply(request):
    context = {}
    initial = {'app_id': request.session.get('app_id', None)}
    form = ApplicationForm(request.POST or None, initial=initial)
    if request.method == 'POST':
        if form.is_valid():
            application = form.save()
            app_id = application.id
            request.session['app_id'] = app_id
            messages.info(request, f'Test submit {app_id}')
            return redirect('/apply/address/')
    else:
        form = ApplicationForm()
    context['form'] = form
    return render(request, 'pathways/apply.html', context)

def address(request):
    context = {}
    initial = {'app_id': request.session.get('app_id', None)}
    form = AccountForm(request.POST or None, initial=initial)
    if request.method == 'POST':
        if form.is_valid():
            return redirect('/')