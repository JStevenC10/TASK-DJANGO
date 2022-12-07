from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from .models import Task

from .forms import TaskForm
# Create your views here.

def index(request):
    return render(request, 'home.html')

def signin(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            form = AuthenticationForm()
            return render(request, 'signin.html', {'form': form, 'error':'username or password incorrect'})
        else:
            login(request, user)
            return redirect(to=tasks)
    else:
        form = AuthenticationForm()
        return render(request, 'signin.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect(to=tasks)
            except:
                return HttpResponse('username already exist')
        else:
            return HttpResponse('password do not match')

    else:
        form = UserCreationForm()
        return render(request, 'signup.html', {
            'form' : form
        })

@login_required
def tasks(request):
    all_tasks = Task.objects.filter(user=request.user)
    return render(request, 'tasks.html', {'task': all_tasks})

@login_required
def add_task(request):
    if request.method == 'POST':
        try:
            task_form = TaskForm(request.POST)
            new_task = task_form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect(to=tasks)
        except:
            task_form = TaskForm()
            return render(request, 'addTask.html', {'form':task_form, 'error' : 'data no valid'})
    else:
        task_form = TaskForm()
        return render(request, 'addTask.html', {'form':task_form})

@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        try:
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('/tasks/')
        except ValueError:
            return render(request, 'tdetail.html', {'task':task, 'form':form, 'error': 'error al actualizar'})
    else:
        form = TaskForm(instance=task)
        return render(request, 'tdetail.html', {'task':task, 'form':form})

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.date_complete = timezone.now()
    task.save()
    return redirect(to=tasks)

@login_required
def delete_task(request, task_id):
    task = Task.objects.get(id=task_id)
    task.delete()
    return redirect(to=tasks)

@login_required
def signout(request):
    logout(request)
    return redirect(to=index)
