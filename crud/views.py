from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from .models import Genders

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

            Genders.objects.create(gender=gender).save()
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