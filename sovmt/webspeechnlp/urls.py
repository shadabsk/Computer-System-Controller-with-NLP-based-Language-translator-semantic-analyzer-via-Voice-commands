from django.urls import path
from webspeechnlp import views

urlpatterns = [
    path('',views.index,name='index'),
    path('vrdata',views.vrdata,name='vrdata'),
    path('vrdatatxt',views.vrdatatxt,name='vrdatatxt'),
]