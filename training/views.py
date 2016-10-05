import os
import logging

from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.shortcuts import *
from django.http import HttpResponse, JsonResponse
from django.utils import timezone

from .models import *
from .statistics import *
from . import gpx


def index(request):
    if request.user.is_authenticated():
        return redirect('dashboard')
    else:
        return render(request, 'training/index.html', {'users_count': User.objects.all().count()})


@login_required
def dashboard(request):
    return render(request, 'training/dashboard.html', {'statistics': Statistics(request.user)})


@login_required
def statistics(request):
    return render(request, 'training/statistics.html', {'statistics': Statistics(request.user)})


@login_required
def start_workout(request):
    workout = Workout.objects.create(user=request.user)
    return redirect('workout', workout.id)


@login_required
def finish_workout(request, training_session_id):
    workout = Workout.objects.get(pk=training_session_id)
    workout.finish()
    workout.save()

    try:
        current_excercise = workout.excercise_set.order_by('-pk')[0]
        current_excercise.time_finished = timezone.now()
        current_excercise.save()
    except:
        pass

    return redirect('workout', workout.id)


@login_required
def workout(request, training_session_id):
    workout = get_object_or_404(Workout, pk=training_session_id, user=request.user)

    gpx = None
    try:
        gpx = workout.gpx_set.get()
    except:
        pass

    return render(request, 'training/workout.html', {'workout': workout,
                                                     'statistics': Statistics(request.user),
                                                     'gpx': gpx})


@login_required
def add_excercise(request, training_session_id):
    workout = Workout.objects.get(pk=training_session_id, user=request.user)

    try:
        current_excercise = workout.excercise_set.order_by('-pk')[0]
        current_excercise.time_finished = timezone.now()
        current_excercise.save()
    except:
        pass

    excercise = workout.excercise_set.create(name=request.POST['name'])
    try:
        workout.start()
    except:
        pass
    workout.save()

    excercise.time_started = timezone.now()
    excercise.save()

    return redirect('workout', training_session_id)


@login_required
def add_reps(request, excercise_id):
    s = Excercise.objects.get(pk=excercise_id, workout__user=request.user)
    s.reps_set.create(reps=request.POST['reps'])

    s.time_updated = timezone.now()
    s.save()
    return redirect('workout', s.workout.id)


@login_required
def delete_workout(request, workout_id):
    workout = Workout.objects.get(pk=workout_id, user=request.user)
    workout.delete()
    return redirect('dashboard')


from django import forms

class UploadGpxForm(forms.Form):
    gpxfile = forms.FileField(label='Select a file')


@login_required
def upload_gpx(request):
    if request.method == "POST":
        form = UploadGpxForm(request.POST, request.FILES)
        if form.is_valid():
            gpx.upload_gpx(request)
            return redirect('dashboard')
        else:
            return render(request, 'training/upload_gpx.html', {'form': form})
    else:
        form = UploadGpxForm()
        return render(request, 'training/upload_gpx.html', {'form': form})


class ConnectWithEndomondoForm(forms.Form):
    email = forms.CharField(label='e-mail')
    password = forms.CharField(label='password', widget=forms.PasswordInput())


@login_required
def endomondo(request):
    if request.method == "POST":
        gpx.connect_to_endomondo(request.user, request.POST["email"], request.POST["password"])
        return redirect('endomondo')
    else:
        key = gpx.endomondo_key(request.user)
        form = ConnectWithEndomondoForm()
        return render(request, 'training/endomondo.html', {'form': form, 'key': key})


@login_required
def synchronize_endomondo(request):
    gpx.synchronize_endomondo(request.user)
    return redirect('endomondo')


@login_required
@never_cache
def synchronize_endomondo_ajax(request):
    count = gpx.synchronize_endomondo(request.user, 10)
    return JsonResponse({"imported_count": count})


@login_required
def disconnect_endomondo(request):
    gpx.disconnect_endomondo(request.user)
    return redirect('endomondo')


@login_required
def purge_endomondo(request):
    gpx.purge_endomondo_workouts(request.user)
    return redirect('dashboard')
