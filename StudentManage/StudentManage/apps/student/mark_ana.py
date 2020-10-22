import pyecharts
from django.shortcuts import render
from utils import sqlheper
from pyecharts.charts import Bar
from pyecharts import options as opts
from pyecharts.globals import ThemeType


def ana(request):
    # 获取学生所有科目成绩，绘制柱状图
    nid = '2017322001'
    course = []
    mark = []
    course_list = sqlheper.get_list('select course.course_name,mark from stu_c left join course on stu_c.course_number=course.course_number where student_id=%s', [nid, ])
    for i in course_list:
        for key, values in i.items():
            if key == 'course_name':
                course.append(values)
            else:
                mark.append(values)
    print(course, mark)
    bar = Bar(init_opts=opts.InitOpts(width='800px', height='500px', theme=ThemeType.LIGHT))
    bar.add_xaxis(course)
    bar.add_yaxis('学生成绩', mark)
    return render(request, 'student_mark_ana.html', {'bar': bar.render_embed()})
