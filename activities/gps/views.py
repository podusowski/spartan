from django import forms
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.shortcuts import *
from django.http import JsonResponse

from . import gpx


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
    key = gpx.endomondo_key(request.user)

    form = _make_form(ConnectWithEndomondoForm, request)

    if form.is_bound and form.is_valid():
        gpx.connect_to_endomondo(request.user, request.POST["email"], request.POST["password"])
        return redirect('endomondo')

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


