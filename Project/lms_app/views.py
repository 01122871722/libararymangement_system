from django.shortcuts import render, redirect, get_object_or_404
import matplotlib.pyplot as plt
from .models import Category, Book
from .forms import BookForms, CategoryForm
import json
import io
import urllib
from io import BytesIO
import base64

def your_view(request):
    books = Book.objects.all()
    books_json = json.dumps([{
        "id": book.id,
        "categoryId": book.category.id,
        "status": book.status
    } for book in books])
    
    return render(request, 'base.html', {'books_json': books_json, 'books': books})

def filter_books(request, status):
    filtered_books = Book.objects.filter(status=status)
    return render(request, 'filtered_books.html', {'books': filtered_books, 'status': status})

def index(request):
    if request.method == 'POST' and 'add_category' in request.POST:
        formcat = CategoryForm(request.POST)
        if formcat.is_valid():
            formcat.save()
            return redirect('/')  # إعادة توجيه بعد حفظ التصنيف

    else:
        formcat = CategoryForm() 
    # حساب عدد الكتب لكل حالة
    total_books = Book.objects.all().count()
    available_books = Book.objects.filter(status='available').count()
    rental_books = Book.objects.filter(status='rental').count()
    sold_books = Book.objects.filter(status='sold').count()

    # النسب المئوية لكل حالة
    if total_books > 0:
        available_percent = (available_books / total_books) * 100
        rental_percent = (rental_books / total_books) * 100
        sold_percent = (sold_books / total_books) * 100
    else:
        available_percent = rental_percent = sold_percent = 0



    books = Book.objects.all()
    total_profit = 0
    rental_profit = 0
    sold_profit = 0
    for book in books:
        if book.status == 'sold':
            sold_profit += book.price
        elif book.status == 'rentel':
            rental_profit += book.total_rental
    for book in books:
        if book.rental_period is not None and book.rental_price_day is not None:
            book.total_rental = book.rental_period * book.rental_price_day
            redirect('/')
        else:
            book.total_rental = 0  
            redirect('/')# أو أي قيمة افتراضية أخرى

    total_profit = sold_profit + rental_profit
    labels = ['Sold Profit', 'Rental Profit']
    values = [sold_profit, rental_profit]

    fig, ax = plt.subplots()
    ax.bar(labels, values)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)

    form_book = BookForms()

    if request.method == 'POST':
        add_book = BookForms(request.POST, request.FILES)
        if add_book.is_valid():
            book = add_book.save(commit=False)
            book.total_rental = book.rental_period * book.rental_price_day
            book.save()

            return redirect('index')

    rental_books = Book.objects.filter(status='rental')
    rental_profit = sum(book.rental_price_day * book.rental_period for book in rental_books)
    sold_books = Book.objects.filter(status='sold')
    sold_profit=sum(book.price for book in sold_books )
    total_profit=rental_profit+sold_profit
    redirect('/')


    context = {
        'totals_profit': total_profit,
        'sold_profit': sold_profit,
        'rental_profit': rental_profit,
        'chart_uri': uri,
        'books': Book.objects.all(),
        'category': Category.objects.all(),
        'formcat': CategoryForm(),
        'form_book': form_book,
        'allbooks': Book.objects.filter(active=True).count(),
        'allbooks': total_books,
        'bookavailable': available_books,
        'bookrental': rental_books,
        'booksold': sold_books,
        'available_percent': available_percent,
        'rental_percent': rental_percent,
        'sold_percent': sold_percent,
    }

    return render(request, 'pages/index.html', context)

def books(request):
    if request.method == 'POST' and 'add_category' in request.POST:
        formcat = CategoryForm(request.POST)
        if formcat.is_valid():
            formcat.save()
            return redirect('index')  # إعادة توجيه بعد حفظ التصنيف

    else:
        formcat = CategoryForm()

    search = Book.objects.all()
    title = None
    if 'search_name' in request.GET:
        title = request.GET.get('search_name')
        if title:
            search = search.filter(title__icontains=title)

    context = {
        'books': search,
        'category': Category.objects.all(),
        'formcat': CategoryForm(),
    }
    return render(request, 'pages/books.html', context)

def update(request, id):
    book_id = get_object_or_404(Book, id=id)
    if request.method == 'POST':
        book_save = BookForms(request.POST, request.FILES, instance=book_id)
        if book_save.is_valid():
            book_save.save()
            return redirect('/')
    else:
        book_save = BookForms(instance=book_id)

    context = {
        'form': book_save,
    }
    return render(request, 'pages/update.html', context)

def delete(request, id):
    book_id = get_object_or_404(Book, id=id)
    if request.method == 'POST':
        book_id.delete()
        return redirect('/')

    return render(request, 'pages/delete.html')
def profits_chart(request):
    # مثال لرسم بياني بسيط للأرباح
    fig, ax = plt.subplots()
    
    # بيانات الأرباح (هذه مجرد بيانات افتراضية)
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    profits = [100, 120, 150, 170, 180, 200]
    
    ax.plot(months, profits, marker='o')
    ax.set_xlabel('Month')
    ax.set_ylabel('Profit')
    ax.set_title('Monthly Profits')
    
    # تحويل الرسم البياني إلى صورة
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    chart_uri = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()

    # تمرير الرسم البياني إلى القالب
    context = {'chart_uri': chart_uri}
    return render(request, 'index.html', context)


