from django.shortcuts import render, redirect
from django.http import HttpResponse
from utils import sqlheper, pager
from pyecharts.charts import Bar
from pyecharts import options as opts
from pyecharts.globals import ThemeType


def score_dis(request):
    """获取教师所教学生的成绩分布"""
    nid = 't1'
    # 获取教师所授课程编号
    course_number = sqlheper.get_list('select course_number from course where teacher_number=%s', [nid, ])
    cn = []
    for i in course_number:
        for key, value in i.items():
            cn.append(value)
    # 在学生选课表中查找选择该课程的学生的成绩
    student_mark = sqlheper.get_list('select mark from stu_c where course_number=%s', [cn, ])
    mark_a, mark_b, mark_c, mark_d, mark_f = [], [], [], [], []
    for i in student_mark:
        for key, values in i.items():
            values = int(values)
            if values >= 90:
                mark_a.append(values)
            elif 80 <= values < 90:
                mark_b.append(values)
            elif 70 <= values < 80:
                mark_c.append(values)
            elif 60 <= values < 70:
                mark_d.append(values)
            else:
                mark_f.append(values)
    mark = [len(mark_a), len(mark_b), len(mark_c), len(mark_d), len(mark_d)]
    bar = Bar(init_opts=opts.InitOpts(width='800px', height='500px', theme=ThemeType.LIGHT))
    bar.add_xaxis(['优秀', '良好', '中等', '及格', '不及格'])
    bar.add_yaxis('学生成绩', mark)
    return render(request, 'student_mark_ana.html', {'bar': bar.render_embed()})


