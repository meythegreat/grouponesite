from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from .models import Genders, Users
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password

# Create your views here.

def gender_list(request):
    try:
        genders = Genders.objects.all()
        data = {
            'genders':genders
        }
        return render(request, 'gender/GendersList.html', data)
    except Exception as e:  
        return HttpResponse(f'An error occurred during loading of gender: {e}')

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

def user_list(request):
    try:
        userObj = Users.objects.select_related('gender')

        data = {
            'users': userObj
        }

        return render(request, 'user/userslist.html', data)
    except Exception as e:
        return HttpResponse(f'Error occurred during loading of user: {e}')

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

            if not password:
                messages.error(request, 'Password is required!')
                return redirect('/user/add')

            if password != confirmPassword:
                messages.error(request, 'Password and confirm password do not match!')
                return redirect('/user/add')

            Users.objects.create(
                full_name=fullName,
                gender=Genders.objects.get(pk=gender),
                birth_date=birthDate,
                address=address,
                contact_number=contactNumber,
                email=email,
                username=username,
                password=make_password(password)
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