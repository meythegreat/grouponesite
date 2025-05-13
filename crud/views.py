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