"""StudentManage URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import sys

from django.contrib import admin
from django.urls import path
from apps.admin import view, student, course, teacher
from apps.student import mark_ana
from apps.teacher import score_dis
from utils import sqlheper

urlpatterns = [
    path('sign/', view.sign),
    path('show/', view.show),
    path('layout/', view.layout),
    path('top/', view.top),
    path('top_stu/', view.top_stu),
    path('top_tea/', view.top_tea),
    path('check/', view.check),
    path('global_search/', view.global_search),
    path('mark_ana/', mark_ana.ana),
    path('score_dis/', score_dis.score_dis),
    path('log/', view.log),

    path('admin/', admin.site.urls),
    path('admin_ana/', view.admin_ana),
    path('course/', course.course),
    path('add_course/', course.add_course),
    path('del_course/', course.del_course),
    path('edit_course/', course.edit_course),
    path('search_course/', course.search_course),
    path('open_course/', course.open_course),
    path('close_course/', course.close_course),


    path('student/', student.student),
    path('add_student/', student.add_student),
    path('del_student/', student.del_student),
    path('edit_student/', student.edit_student),
    path('search_student/', student.search_student),
    path('export/', sqlheper.export),

    path('teacher/', teacher.teacher),
    path('add_teacher/', teacher.add_teacher),
    path('del_teacher/', teacher.del_teacher),
    path('edit_teacher/', teacher.edit_teacher),
    path('search_teacher/', teacher.search_teacher),
]
