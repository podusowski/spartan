from django.contrib import admin
from statistics import models


@admin.register(models.Goal)
class GoalAdmin(admin.ModelAdmin):
    pass
