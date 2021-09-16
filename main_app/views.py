from django.shortcuts import render,redirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
# from django.http import HttpResponse
# removed HttpResponse due to refactor to render
from .models import Cat, Toy, Photo
from .forms import FeedingForm
import uuid
import boto3
import os
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin



def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')
    # render takes two arguments, the request object passed through, and the name of the file

@login_required
def cats_index(request):
    cats = Cat.objects.filter(user=request.user)

    return render(request, 'cats/index.html', {'cats': cats})
    # render takes two arguments, the request object passed through, and the name of the file
@login_required
def cat_detail(request, cat_id):
    try:
        cat = Cat.objects.get(id=cat_id)
        toys_cat_doesnt_have = Toy.objects.exclude(id__in = cat.toys.all().values_list('id'))

        feeding_form = FeedingForm()
        return render(request, 'cats/detail.html', {
            'cat': cat, 'feeding_form':feeding_form,
            # Add the toys to be displayed
            'toys': toys_cat_doesnt_have
        })
    except(Cat.DoesNotExist):
        return redirect('/cats')

class CatCreate(CreateView):
    model = Cat
    #fields = "__all__"
    fields = ['name', 'breed', 'description', 'age']
    
    # This inherited method is called when a
    # valid cat form is being submitted
    def form_valid(self, form):
    # Assign the logged in user (self.request.user)
        form.instance.user = self.request.user  # form.instance is the cat
        # Let the CreateView do its job as usual
        return super().form_valid(form)

class CatUpdate(LoginRequiredMixin, UpdateView):
    model = Cat
    fields = "__all__"

class CatDelete(LoginRequiredMixin, DeleteView):
    model = Cat
    fields = "__all__"
    success_url = '/cats'

@login_required
def add_feeding(request, cat_id):
    form = FeedingForm(request.POST)
    print(request)
    if form.is_valid():
        new_feeding = form.save(commit=False)
        new_feeding.cat_id = cat_id
        new_feeding.save()    
        
    return redirect('detail', cat_id=cat_id)

class ToyList(LoginRequiredMixin, ListView):
  model = Toy

class ToyDetail(LoginRequiredMixin, DetailView):
  model = Toy

class ToyCreate(LoginRequiredMixin, CreateView):
  model = Toy
  fields = '__all__'

class ToyUpdate(LoginRequiredMixin, UpdateView):
  model = Toy
  fields = ['name', 'color']

class ToyDelete(LoginRequiredMixin, DeleteView):
  model = Toy
  success_url = '/toys'

@login_required
def assoc_toy(request, cat_id, toy_id):
  # Note that you can pass a toy's id instead of the whole toy object
  Cat.objects.get(id=cat_id).toys.add(toy_id)
  return redirect('detail', cat_id=cat_id)

@login_required
def add_photo(request, cat_id):
    # photo-file will be the "name" attribute on the <input type="file">
    photo_file = request.FILES.get('photo-file', None)
    if photo_file:
        s3 = boto3.client('s3')
        # need a unique "key" for S3 / needs image file extension too
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
        # just in case something goes wrong
        try:
            bucket = os.environ['S3_BUCKET']
            s3.upload_fileobj(photo_file, bucket, key)
            # build the full url string
            url = f"{os.environ['S3_BASE_URL']}{bucket}/{key}"
            # we can assign to cat_id or cat (if you have a cat object)
            Photo.objects.create(url=url, cat_id=cat_id)
        except:
            print('An error occurred uploading file to S3')
    return redirect('detail', cat_id=cat_id)

def signup(request):
    error_message = ''
    if request.method == 'POST':
        # This is how to create a 'user' form object
        # that includes the data from the browser
        form = UserCreationForm(request.POST)
        if form.is_valid():
        # This will add the user to the database
            user = form.save()
        # This is how we log a user in via code
            login(request, user)
            return redirect('index')
        else:
            error_message = 'Invalid sign up - try again'
    # A bad POST or a GET request, so render signup.html with an empty form
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)