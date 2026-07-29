from django.contrib import admin
from .models import Agriculteur


@admin.register(Agriculteur)
class AgriculteurAdmin(admin.ModelAdmin):
    list_display = ('nom_prenom', 'localite', 'activite_principale', 'total_production_an')
    search_fields = ('nom_prenom', 'localite', 'principales_cultures')