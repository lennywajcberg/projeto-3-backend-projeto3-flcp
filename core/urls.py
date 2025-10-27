from django.contrib import admin
from django.urls import path
from api import views as v

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/symbols", v.symbols_view),
    path("api/quotes", v.quotes_view),
    path("api/favorites", v.favorites_collection_view),
    path("api/favorites/<str:symbol>", v.favorite_detail_view),
]
