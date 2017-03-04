from django.contrib import admin
from nested_inline.admin import NestedStackedInline, NestedTabularInline, NestedModelAdmin
from training import models
from .models import Workout, Excercise, Gpx


class RepsInline(NestedStackedInline):
    model = models.Reps
    extra = 1


class ExcerciseInline(NestedStackedInline):
    model = models.Excercise
    extra = 1
    inlines = [RepsInline]


class GpxInline(NestedStackedInline):
    model = models.Gpx
    extra = 1


@admin.register(models.Workout)
class WorkoutAdmin(NestedModelAdmin):
    inlines = [ExcerciseInline, GpxInline]

