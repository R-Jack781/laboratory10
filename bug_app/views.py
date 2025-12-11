# bug_app/views.py
from django.shortcuts import render
from .models import Programmer, Error, BugFix

def data_display(request):
    context = {
        'project_name': "Компанія з розробки та супроводу ПЗ",
        'student_info': "Романюк Євгеній Анатолійович, 23008бск",
        'programmers': Programmer.objects.all(),
        'errors': Error.objects.all(),
        'bug_fixes': BugFix.objects.all(),
    }
    return render(request, 'bug_app/index.html', context)