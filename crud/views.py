from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from .models import Genders, Users
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.template.loader import render_to_string

# Create your views here.

@login_required
def gender_list(request):
    try:
        genders = Genders.objects.all()
        data = {
            'genders':genders
        }
        return render(request, 'gender/GendersList.html', data)
    except Exception as e:  
        return HttpResponse(f'An error occurred during loading of gender: {e}')

@login_required
def add_gender(request):
    try:
        if request.method == 'POST':
            gender = request.POST.get('gender')

            Genders.objects.create(gender=gender)
            messages.success(request, 'Gender added successfully!')
            return render(request, 'gender/AddGender.html')
        else:
            return render(request, 'gender/AddGender.html')
    except Exception as e:
        return HttpResponse(f"An error occurred during adding of gender: {e}")  

def edit_gender(request, genderId):
    try:
        if request.method == 'POST':
            genderObj = Genders.objects.get(pk=genderId)

            gender = request.POST.get('gender')

            genderObj.gender = gender
            genderObj.save()

            messages.success(request, 'Gender updated successfully!')

            data = {
                'gender': genderObj
            }

            return render(request, 'gender/editgender.html', data)
        
        else:    
            genderObj = Genders.objects.get(pk=genderId)

            data = {
                'gender': genderObj
            }

            return render(request, 'gender/editgender.html', data)

    except Exception as e:
        return HttpResponse(f'Error occurred during edit gender: {e}')

def delete_gender(request, genderId):
    try:
        if request.method == 'POST':
            genderObj = Genders.objects.get(pk=genderId)
            genderObj.delete()

            messages.success(request, 'Gender deleted successfully!')
            return redirect('/gender/list')
        
        else: 
            genderObj = Genders.objects.get(pk=genderId)

            data = {
                'gender': genderObj
            }

        return render(request, 'gender/deletegender.html', data)
    except Exception as e:
        return HttpResponse(f'Error occurred during deleting of gender: {e}')

@login_required
def user_list(request):
    try:
        search_query = request.GET.get('search', '')
        userObj = Users.objects.select_related('gender').filter(
            full_name__icontains=search_query
        )

        paginator = Paginator(userObj, 10)  # 10 users per page
        page_number = request.GET.get('page')

        # Validate the page number
        try:
            page_number = int(page_number)
        except (TypeError, ValueError):
            page_number = 1

        # If page is less than 1, reset to 1
        if page_number < 1:
            page_number = 1

        # If page is greater than max, reset to max
        if page_number > paginator.num_pages:
            page_number = paginator.num_pages

        # Get the page object
        page_obj = paginator.get_page(page_number)

        data = {'page_obj': page_obj, 'search_query': search_query}
        return render(request, 'user/userslist.html', data)

    except Exception as e:
        return HttpResponse(f'Error occurred during loading of user: {e}')

@login_required
def add_user(request):
    try:
        if request.method == 'POST':
            fullName = request.POST.get('full_name')
            gender = request.POST.get('gender')
            birthDate = request.POST.get('birth_date')
            address = request.POST.get('address')
            contactNumber = request.POST.get('contact_number')
            email = request.POST.get('email')
            username = request.POST.get('username')
            password = request.POST.get('password')
            confirmPassword = request.POST.get('confirm_password')

            if password != confirmPassword:
                messages.error(request, 'Password and confirm password do not match!')
                return redirect('/user/add')

            if not password:
                messages.error(request, 'Password is required!')
                return redirect('/user/add')

            gender_obj = Genders.objects.get(pk=gender)

            Users.objects.create(
                full_name=fullName,
                gender=gender_obj,
                birth_date=birthDate,
                address=address,
                contact_number=contactNumber,
                email=email,
                username=username,
                password=make_password(password)  # Hash the password
            )

            messages.success(request, 'User added successfully!')
            return redirect('/user/add')

        else:
            genderObj = Genders.objects.all()
            data = {
                'genders': genderObj
            }
            return render(request, 'user/AddUser.html', data)

    except Exception as e:
        return HttpResponse(f'Error occurred during add user: {e}')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            messages.error(request, 'Both username and password are required.')
            return render(request, 'login.html')  # Only display after POST with missing fields

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')

        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'login.html')
        
    # For GET request: just render login page without adding any messages    
    return render(request, 'login.html')

def home(request):
    return render(request, 'home.html')

# @login_required
# def edit_user(request, id):
#     user = get_object_or_404(Users, id=id)
#     if request.method == 'POST':
#         user.full_name = request.POST.get('full_name')
#         user.email = request.POST.get('email')
#         user.save()
#         messages.success(request, 'User updated successfully!')
#         return redirect('user_list')
#     return render(request, 'user/EditUser.html', {'user': user})

# @login_required
# def delete_user(request, id):
#     user = get_object_or_404(Users, id=id)
#     user.delete()
#     messages.success(request, 'User deleted successfully!')
#     return redirect('user_list')