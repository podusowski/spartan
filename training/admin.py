from django.contrib import admin
from .models import Workout, Excercise, Gpx


class ExcerciseInline(admin.StackedInline):
    model = Excercise
    extra = 1


class GpxInline(admin.StackedInline):
    model = Gpx
    extra = 1


class TrainingSessionAdmin(admin.ModelAdmin):
    inlines = [ExcerciseInline, GpxInline]


admin.site.register(Workout, TrainingSessionAdmin)
