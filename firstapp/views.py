from django.shortcuts import HttpResponse, redirect, render
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Book

# transaction atomic

@login_required
@csrf_exempt
def home(request):  # http request
    # print(request.method)
    if request.method == "POST":
        data = request.POST
        # print(request.POST.getlist("cars"))  # get- for single value, getlist for multiple values  
        bid = data.get("book_id")
        name = data.get("book_name") # None
        qty = data.get("book_qty")
        price = data.get("book_price")
        author = data.get("book_author")
        is_pub = data.get("book_is_pub") # Yes, No
        # print(name, qty, price, author, is_pub)
        if is_pub == "Yes":
            is_pub = True
        else:
            is_pub = False
        if not bid:
            Book.objects.create(name=name, qty=qty, price=price, author=author, is_published=is_pub)
        else:
            book_obj = Book.objects.get(id=bid)
            book_obj.name = name
            book_obj.qty = qty
            book_obj.price = price
            book_obj.author = author
            book_obj.is_published = is_pub
            book_obj.save()
        # return redirect("home_page")
        return HttpResponse("Success")
    elif request.method == "GET":
        # print(request.GET) # get query params
        return render(request, "old_home.html", context={"person_name": "Mohini"})

@login_required
def show_books(request):
    return render(request, "show_books.html", {"books" : Book.objects.filter(is_active=True), "active": True})

@login_required
def update_book(request, id): # pk=1
    book_obj = Book.objects.get(id=id)
    return render(request, "home.html", context={"single_book": book_obj})

@login_required
def delete_book(request, pk): # hard delete
    Book.objects.get(id=pk).delete()
    return redirect("all_active_books")

@login_required
def soft_delete_book(request, pk):
    book_obj = Book.objects.get(id=pk)
    book_obj.is_active = False
    book_obj.save()
    return redirect("all_inactive_books")

@login_required
def show_inactive_books(request):
    return render(request, "show_books.html", {"books" : Book.objects.filter(is_active=False), "inactive": True})
    
# soft delete

@login_required
def restore_book(request, pk):
    book_obj = Book.objects.get(id=pk)
    book_obj.is_active = True
    book_obj.save()
    return redirect("all_active_books")



# 21-12-2022

from .forms import BookForm, AddressForm
# from django.contrib.auth.forms import UserCreationForm  


@login_required
def book_form(request):
    form = BookForm()
    if request.method == 'POST':
        print(request.POST)
        form = BookForm(data=request.POST)
        if form.is_valid():
            # print(form.cleaned_data.get("name"))
            form.save()  # database save
            return HttpResponse("Successfully Registered!!!")
    else:
        context = {'form': form}
        return render(request, "book_form.html",context=context)

# simpleisbetterthancomplex

def sibtc(request):
    return render(request, "sibtc.html", {"form": AddressForm()})




from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def index(request):
    # print("in index function")
    book_list = Book.objects.all()
    page = request.GET.get('page', 1)
    print(page)
    paginator = Paginator(book_list, 3)
    try:
        books = paginator.page(page)
    except PageNotAnInteger:
        books = paginator.page(1)
    except EmptyPage:
        books = paginator.page(paginator.num_pages)
    return render(request, 'index.html', {'books': books })


# from django.views import View 

# class NewView(View):  
#     def get(self, request):  
#         # View logic will place here  
#         return HttpResponse('get response')  

#     def post(self, request):
#         return HttpResponse("post response")

#     def put(self, request): # update
#         return HttpResponse("put response")

#     def patch(self, request): # partial info update
#         return HttpResponse("patch response")

#     def delete(self, request): # delete
#         return HttpResponse("delete response")



# CRUD
from django.views.generic.edit import CreateView

class BookCreate(CreateView):  # get/post handled
    model = Book  
    fields = '__all__'  
    success_url = "/cbv-create-book/"  # reverse_lazy('BookCreate')  


from django.views.generic.list import ListView  
  
class BookRetrieve(ListView):  
    model = Book 
    context_object_name = "all_books"
    # http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']
    # queryset = Book.objects.filter(is_active=1)

    # def get_queryset(self):
    #     print("in method")
    #     return Book.objects.filter(is_active=0)

from django.views.generic.detail import DetailView  
  
class BookDetail(DetailView):  
    model = Book  


from django.views.generic.edit import UpdateView  

class BookUpdate(UpdateView):  
    model = Book 
    fields = "__all__"
    success_url = "/cbv-create-book/"

from django.views.generic import TemplateView

class Template(TemplateView):
    template_name  = "home.html"  # {{name}}
    extra_context = {"name": "Aakash"}



from django.http import HttpResponse
import csv

def create_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="test.csv"'

    writer = csv.writer(response)
    writer.writerow(['name','qty', 'price', 'author', 'is_published', 'is_active'])

    books = Book.objects.all().values_list('name','qty', 'price', 'author', 'is_published', 'is_active')
    for book in books:
        writer.writerow(book)
    return response


# Assignement:- 9th   -- 
# book csv export
# excel -- active books sheet- active books, inactive sheet-inactive books, 
# raw queries - using objects.raw  (select * from books;) -- csv me dalna
# read text file and show its content on UI using view
# download sample csv file
# validations - duplicate book not allowed


def upload_csv(request): 
    file = request.FILES["csv_file"]    
    decoded_file = file.read().decode('utf-8').splitlines()
    expected_header_lst = ['name', "qty", "price", "author", "is_published"]
    expected_header_lst.sort()

    actual_header_lst = decoded_file[0].split(",")
    actual_header_lst.sort()
    # print(expected_header_lst, actual_header_lst)
    if expected_header_lst != actual_header_lst:
        return HttpResponse("Error...Headers are not equal..!")

    reader = csv.DictReader(decoded_file) # always use DictReader
    lst = []
    for element in reader:
        print(element)
        # is_pub = element.get("is_published")
        # if is_pub == "TRUE":
        #     is_pub = True
        # else:
        #     is_pub = False
        # lst.append(Book(name=element.get("name"), qty=element.get("qty"), price=element.get("price"), author=element.get("author"), is_published=is_pub))
    # print(reader)
    # Book.objects.bulk_create(lst)
    return HttpResponse("Success")

def func(request):
    return request

# print(func("abcd"))

# ['name,qty,price,is_published', 'Book101,20,61,ABC,TRUE', 'Book102,40,689,XYZ,FALSE', 'Book103,60,165,PQR,TRUE','Book104,80,165,JKL,FALSE', 'Book105,100,800,QWERTY,FALSE', 'Book106,120,1651,GHJ,TRUE', 'Book107,140,1515,RTYU,TRUE', 'Book108,25,35,RTYU,FALSE']

import requests
# GET_SINGLE_STUD_URL = "http://127.0.0.1:8000/api/get-student/{}/"
GET_ALL_STUDS = "http://127.0.0.1:8000/api/get-all-students/"
# CREATE_STUD = "http://127.0.0.1:8000/api/create-student/"


def get_all_student(request):
    # response = requests.get(GET_ALL_STUDS)
    response = requests.request("GET", GET_ALL_STUDS)
    python_dict = response.json()  # json to python dict
    return render(request, "student_data.html", {"data": python_dict})