from django.contrib import admin
from .models import TrainingSession, Excercise


class ExcerciseInline(admin.StackedInline):
    model = Excercise
    extra = 1


class TrainingSessionAdmin(admin.ModelAdmin):
    inlines = [ExcerciseInline]


admin.site.register(TrainingSession, TrainingSessionAdmin)
