from django.shortcuts import render, redirect
from django.contrib import messages
from utils import sqlheper
from pyecharts.charts import Bar
from pyecharts import options as opts
from pyecharts.globals import ThemeType


def sign(request):
    """
    登录函数
    """
    if request.method == "GET":
        return render(request, 'sign.html')
    else:
        name = request.POST.get('user_name')
        password = request.POST.get('password')
        exist_a = sqlheper.get_list("select password from user_admin where name=%s and password=%s", [name, password])
        if exist_a:
            obj = redirect('/top/')
            obj.set_cookie('ticket', '123')
            obj.set_cookie('name', name)
            obj.set_cookie('password', password)
        else:
            toast(request)
            return render(request, 'sign.html')
        return obj


def global_search(request):
    """
    全局搜索
    """
    search = request.GET.get('search')
    search_word = ["学生管理", "课程管理", "老师管理"]
    search_word_url = ["/student/", "/course/", "/teacher/"]
    for i, j in enumerate(search_word):
        if search in j:
            return redirect(search_word_url[i])


def check(request):
    """校验函数"""
    return render(request, 'check.html')


def show(request):
    return render(request, 'show.html')


def layout(request):
    return render(request, 'layout.html')


def toast(request):
    messages.error(request, "用户名或密码错误")


def top(request):
    stu_num = len(sqlheper.get_list('select * from student', []))
    cou_num = len(sqlheper.get_list('select * from course', []))
    tea_num = len(sqlheper.get_list('select * from teacher', []))
    log = sqlheper.get_list('select * from operationlogs', [])
    user_name = request.COOKIES.get('name')
    return render(request, 'home_page.html',
                  {'user_name': user_name, 'log': log, 'stu_num': stu_num, 'cou_num': cou_num, 'tea_num': tea_num, })


def top_stu(request):
    return render(request, 'top_stu.html')


def top_tea(request):
    return render(request, 'top_tea.html')


def log(request):
    log = sqlheper.get_list('select * from operationlogs order by id DESC', [])[:10]
    return render(request, 'log.html', {'log': log})


def admin_ana(request):
    """
    了解专业人数分布情况
    1.获取所有专业名称
    2.获取每个专业人数
    """
    major_list = sqlheper.get_list('select major_name from major', [])
    major = []
    for i in major_list:
        for key, value in i.items():
            major.append(value)
    major_num = []
    for i in major:
        num = len(sqlheper.get_list('select * from student where major_name=%s', [i]))
        major_num.append(num)
    bar = Bar(init_opts=opts.InitOpts(width='1200px', height='500px', theme=ThemeType.LIGHT))
    bar.set_global_opts(title_opts=opts.TitleOpts(title='不同专业人数分布情况'))
    bar.add_xaxis(major)
    bar.add_yaxis('人数', major_num, bar_max_width='40px')

    # 了解课程和成绩的相关性
    course_list = sqlheper.get_list('select course_number,course_name from course order by id', [])
    print(course_list)
    course_name, course_num = [], []
    for i in course_list:
        for key, value in i.items():
            if key == 'course_name':
                course_name.append(value)
            else:
                course_num.append(value)
    print(course_num)
    course_h, course_m, course_l = [], [], []

    for i in course_num:
        # 对每一门课程，分别计算高、中、低的成绩人数
        high, med, low = 0, 0, 0
        mark = sqlheper.get_list('select mark from stu_c where course_number=%s', [i, ])
        for j in mark:
            for key, value in j.items():
                # 遍历所有选择该课程的学生成绩
                value = int(value)
                if value > 85:
                    high += 1
                elif 60 < value <= 85:
                    med += 1
                elif value <= 60:
                    low += 1

        course_h.append(high)
        course_m.append(med)
        course_l.append(low)
    bar_c = Bar(init_opts=opts.InitOpts(width='1200px', height='500px', theme=ThemeType.LIGHT))
    bar_c.set_global_opts(title_opts=opts.TitleOpts(title='课程和成绩的相关性'))
    print(course_name)
    bar_c.add_xaxis(course_name)
    bar_c.add_yaxis('高分段', course_h)
    bar_c.add_yaxis('中分段', course_m)
    bar_c.add_yaxis('低分段', course_l)

    stu_num = len(sqlheper.get_list('select * from student', []))
    cou_num = len(sqlheper.get_list('select * from course', []))
    tea_num = len(sqlheper.get_list('select * from teacher', []))
    return render(request, 'admin_ana.html', {'bar': bar.render_embed(), 'bar_c': bar_c.render_embed(),
                                              'stu_num': stu_num, 'cou_num': cou_num, 'tea_num': tea_num, })
