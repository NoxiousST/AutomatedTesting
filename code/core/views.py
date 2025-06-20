from django.shortcuts import render

from core.models import Course2


# Create your views here.
def course_list(request):
    courses = Course2.objects.all()
    return render(request, 'course_list.html', {'courses': courses})