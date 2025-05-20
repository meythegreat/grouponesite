from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Genders, Users
from django.db.models import Q
from django.http import HttpResponse

import re 

# Gender Views
@login_required
def gender_list(request):
    genders = Genders.objects.all()
    return render(request, 'gender/GendersList.html', {'genders': genders})

@login_required
def add_gender(request):
    if request.method == 'POST':
        gender_name = request.POST.get('gender')
        if gender_name:
            Genders.objects.create(gender=gender_name)
            messages.success(request, 'Gender added successfully!')
            return redirect('gender_list')
    return render(request, 'gender/AddGender.html')

# User Views
@login_required
def user_list(request):
    search_query = request.GET.get('search', '').strip()

    if search_query:
        users = Users.objects.select_related('gender').filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(contact_number__icontains=search_query) |
            Q(gender__gender__iexact=search_query)  # Case-sensitive for gender
        )
    else:
        users = Users.objects.select_related('gender').all()

    # Pagination
    paginator = Paginator(users, 10)  # 10 users per page
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'user/UsersList.html', {'page_obj': page_obj, 'search_query': search_query, 'total_users': users.count()})

@login_required
def add_user(request):
    try:
        genders = Genders.objects.all()

        if request.method == 'POST':
            fullName = request.POST.get('full_name')
            gender_id = request.POST.get('gender')
            birthDate = request.POST.get('birth_date')
            address = request.POST.get('address')
            contactNumber = request.POST.get('contact_number')
            email = request.POST.get('email')
            username = request.POST.get('username')
            password = request.POST.get('password')
            confirmPassword = request.POST.get('confirm_password')

            # Validation
            if not all([fullName, gender_id, birthDate, address, contactNumber, username, password]):
                messages.error(request, 'All fields except Email are required.')
                return render(request, 'user/AddUser.html', {'genders': genders})

            if password != confirmPassword:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'user/AddUser.html', {'genders': genders})

            if Users.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
                return render(request, 'user/AddUser.html', {'genders': genders})

            gender = Genders.objects.get(gender_id=gender_id)
            Users.objects.create(
                full_name=fullName,
                gender=gender,
                birth_date=birthDate,
                address=address,
                contact_number=contactNumber,
                email=email,
                username=username,
                password=make_password(password)
            )

            messages.success(request, 'User added successfully!')
            return redirect('/user/list')

        return render(request, 'user/AddUser.html', {'genders': genders})

    except Exception as e:
        return HttpResponse(f'Error occurred during adding of user: {e}')

@login_required
def edit_user(request, userId):
    try:
        user = Users.objects.get(user_id=userId)
        genders = Genders.objects.all()  # ✅ fetch all gender options

        if request.method == 'POST':
            fullName = request.POST.get('full_name')
            email = request.POST.get('email')
            username = request.POST.get('username')
            gender_id = request.POST.get('gender')

            # Check for username uniqueness
            if Users.objects.exclude(user_id=userId).filter(username=username).exists():
                messages.error(request, 'Username is already taken.')
                return redirect(f'/user/edit/{userId}/')

            user.full_name = fullName
            user.email = email
            user.username = username
            user.gender = Genders.objects.get(gender_id=gender_id)
            user.save()

            messages.success(request, 'User updated successfully!')
            return redirect('/user/list')

        return render(request, 'user/EditUser.html', {
            'user': user,
            'genders': genders
        })

    except Users.DoesNotExist:
        messages.error(request, 'User does not exist.')
        return redirect('/user/list')

    except Exception as e:
        return HttpResponse(f'Error occurred during user edit: {e}')

@login_required
def edit_gender(request, genderId):
    gender = get_object_or_404(Genders, pk=genderId)
    if request.method == 'POST':
        gender_name = request.POST.get('gender')
        if gender_name:
            gender.gender = gender_name
            gender.save()
            messages.success(request, 'Gender updated successfully!')
            return redirect('gender_list')
    return render(request, 'gender/EditGender.html', {'gender': gender})

@login_required
def delete_gender(request, genderId):
    gender = get_object_or_404(Genders, pk=genderId)
    if request.method == 'POST':
        gender.delete()
        messages.success(request, 'Gender deleted successfully!')
        return redirect('gender_list')
    return render(request, 'gender/DeleteGender.html', {'gender': gender})

@login_required
def delete_user(request, userId):
    try:
        user = Users.objects.get(user_id=userId)

        if request.method == 'POST':
            user.delete()
            messages.success(request, 'User deleted successfully!')
            return redirect('/user/list')

        return render(request, 'user/deleteuser.html', {'user': user})

    except Users.DoesNotExist:
        messages.error(request, 'User does not exist.')
        return redirect('/user/list')

    except Exception as e:
        return HttpResponse(f'Error occurred during user deletion: {e}')

@login_required
def change_password(request, userId):
    user = get_object_or_404(Users, user_id=userId)  # Corrected to user_id

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        elif len(new_password) < 8 or not re.search(r"[A-Za-z]", new_password) or not re.search(r"[0-9]", new_password):
            messages.error(request, 'Password must be at least 8 characters and contain letters and numbers.')
        else:
            user.password = make_password(new_password)
            user.save()
            messages.success(request, 'Password changed successfully.')
            return redirect('user_list')

    return render(request, 'user/ChangePassword.html', {'user': user})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def signup_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        gender = Genders.objects.get(gender_id=request.POST.get('gender'))
        Users.objects.create(
            full_name=full_name,
            gender=gender,
            username=request.POST.get('username'),
            password=make_password(request.POST.get('password'))
        )
        messages.success(request, 'Signup successful! You can now login.')
        return redirect('login')

    genders = Genders.objects.all()
    return render(request, 'user/Signup.html', {'genders': genders})

# Home View
@login_required
def home(request):
    return render(request, 'home.html')