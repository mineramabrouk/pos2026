from django.urls import path
from . import views

urlpatterns = [
    path('', views.CatalogListView.as_view(), name='catalog_home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]
