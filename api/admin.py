from django.contrib import admin
from .models import Favorite

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("client_id", "symbol", "created_at")
    search_fields = ("client_id", "symbol")
