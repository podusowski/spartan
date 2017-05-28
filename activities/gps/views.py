from django import forms
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.shortcuts import *
from django.http import JsonResponse

from statistics.statistics import *
from . import gpx
from . import endomondo as endo


def workout(request, workout_id):
    workout = get_object_or_404(Workout, pk=workout_id, user=request.user)
    gpx = workout.gpx_set.get()

    return render(request, 'training/workout.html', {'workout': workout,
                                                     'statistics': Statistics(request.user),
                                                     'gpx': gpx})


def _make_form(form_type, request, initial=None):
    if request.method == "POST":
        return form_type(request.POST, request.FILES)
    else:
        return form_type(initial=initial)


class UploadGpxForm(forms.Form):
    gpxfile = forms.FileField(label='select a file', label_suffix='')


@login_required
def upload_gpx(request):
    if request.method == "POST":
        form = UploadGpxForm(request.POST, request.FILES)
        if form.is_valid():
            workout_id = gpx.upload_gpx(request)
            return redirect('workout', workout_id)
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
    key = endo.endomondo_key(request.user)

    form = _make_form(ConnectWithEndomondoForm, request)

    if form.is_bound and form.is_valid():
        try:
            endo.connect_to_endomondo(request.user, request.POST["email"], request.POST["password"])
            return redirect('endomondo')
        except:
            form.add_error(None, 'Endomondo has rejected your credentials')

    return render(request, 'training/endomondo.html', {'form': form, 'key': key})


@login_required
def synchronize_endomondo(request):
    endo.synchronize_endomondo(request.user)
    return redirect('endomondo')


@login_required
@never_cache
def synchronize_endomondo_ajax(request):
    count = endo.synchronize_endomondo(request.user, 10)
    return JsonResponse({"imported_count": count})


@login_required
def disconnect_endomondo(request):
    endo.disconnect_endomondo(request.user)
    return redirect('endomondo')


@login_required
def purge_endomondo(request):
    endo.purge_endomondo_workouts(request.user)
    return redirect('dashboard')


