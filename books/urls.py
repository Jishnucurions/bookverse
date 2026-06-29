from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('api/subject/<str:subject>/', views.subject_books_api, name='subject_books_api'),
    path('search/', views.search_view, name='search'),
    path('book/<str:work_key>/', views.book_detail_view, name='book_detail'),
    path('save/', views.toggle_save_book, name='toggle_save_book'),
    path('status/<int:book_id>/', views.update_book_status, name='update_book_status'),
]
