from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('books', views.books, name='books'),
    path('update/<int:id>', views.update, name='update'),
    path('delete/<int:id>', views.delete, name='delete'),
    path('', views.your_view, name='home'),
    path('profits_chart/', views.profits_chart, name='profits_chart'),
    path('books/<str:status>/', views.filter_books, name='filter_books'),
]



