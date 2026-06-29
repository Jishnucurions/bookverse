from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.core.cache import cache
from .models import SavedBook
from .utils import search_books, get_book_details, get_books_by_subject

@login_required
def home_view(request):
    shelf_preview = SavedBook.objects.filter(user=request.user).order_by('-date_added')[:4]
    
    context = {
        'shelf_preview': shelf_preview,
    }
    return render(request, 'books/home.html', context)

@login_required
def subject_books_api(request, subject):
    limit = 6
    cache_key = f"subject_api_{subject}_{limit}"
    data = cache.get(cache_key)
    
    if data is None:
        data = get_books_by_subject(subject, limit=limit)
        # Cache for 1 hour
        cache.set(cache_key, data, 3600)
        
    return JsonResponse({'books': data})

@login_required
def search_view(request):
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        results = search_books(query)
    
    context = {
        'query': query,
        'results': results
    }
    return render(request, 'books/search.html', context)

@login_required
def book_detail_view(request, work_key):
    book = get_book_details(work_key)
    if not book:
        messages.error(request, "Could not fetch details for this book from Open Library.")
        return redirect('home')
        
    saved_book = SavedBook.objects.filter(user=request.user, work_key=work_key).first()
    
    context = {
        'book': book,
        'saved_book': saved_book,
    }
    return render(request, 'books/detail.html', context)

@login_required
@require_POST
def toggle_save_book(request):
    work_key = request.POST.get('work_key')
    title = request.POST.get('title')
    author_name = request.POST.get('author_name')
    cover_id = request.POST.get('cover_id') or None
    
    saved_book = SavedBook.objects.filter(user=request.user, work_key=work_key).first()
    
    if saved_book:
        saved_book.delete()
        messages.info(request, f"Removed '{title}' from your reading list.")
    else:
        SavedBook.objects.create(
            user=request.user,
            work_key=work_key,
            title=title,
            author_name=author_name,
            cover_id=cover_id,
            status='to_read'
        )
        messages.success(request, f"Added '{title}' to your reading list.")
        
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'home'
    return redirect(next_url)

@login_required
@require_POST
def update_book_status(request, book_id):
    saved_book = get_object_or_404(SavedBook, id=book_id, user=request.user)
    status = request.POST.get('status')
    
    if status in dict(SavedBook.STATUS_CHOICES):
        saved_book.status = status
        saved_book.save()
        messages.success(request, f"Updated status of '{saved_book.title}' to {saved_book.get_status_display()}.")
    else:
        messages.error(request, "Invalid reading status selected.")
        
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'profile_settings'
    return redirect(next_url)
