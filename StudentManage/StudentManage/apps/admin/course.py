from django.shortcuts import render, redirect
from django.http import HttpResponse
from utils import sqlheper, pager, operationlogs
import json
import re
from operator import methodcaller


def course(request):
    """
    课程管理首页
    """
    # 检验用户是否登录
    tk = request.COOKIES.get('ticket')
    if not tk:
        return redirect('/sign/')
    # 获得url
    url = '/course/?'
    if request.GET.get('per_page'):
        url = '/course/?per_page=' + request.GET.get('per_page') + '&'
    # 展示课程信息
    if request.GET.get('sort') == "desc":
        # 倒排
        url = "/course/?sort=desc&"
        clist = sqlheper.get_list(
            "select course.id,course_name,teacher.name,credit,status from course left join teacher on course.teacher_number=teacher.teacher_number order by course.id DESC",
            [])
    else:
        # 正序
        clist = sqlheper.get_list(
            "select course.id,course_name,teacher.name,credit,status from course left join teacher on course.teacher_number=teacher.teacher_number order by course.id",
            [])
    course_number = len(sqlheper.get_list("select * from course", []))
    all_count = course_number  # 课程表数据条数
    current_page = 1  # 默认当前页
    if request.GET.get('page'):
        current_page = int(request.GET.get('page'))  # 当前页码
    per_page = 10  # 默认每页数据条数
    if request.GET.get('per_page'):
        per_page = int(request.GET.get('per_page'))
    # 新建一个分页器
    page_info = pager.PageInfo(current_page, all_count, per_page, url)
    # 将学生表切片，只展示当前页所需学生信息
    start, end = page_info.start(), page_info.end()
    course_list_obj = CourseList(clist, start, end)
    return render(request, 'course.html', {'course_list_obj': course_list_obj, 'per_page': per_page,
                                           'page_info': page_info,
                                           'teacher_list': json.dumps(course_list_obj.teacher_list),
                                           'url': request.get_full_path()
                                           })


def add_course(request):
    """
    添加课程
    """
    ret = {'status': True, 'message': None}
    try:
        cname = request.POST.get('course_name')
        c = CourseList()
        c.add_check(request.POST)  # 校验
        add_list = list(request.POST.values())  # 待添加的数据
        sqlheper.modify("insert into course(course_name,teacher_number,credit) values(%s,%s,%s)", add_list)
        cid = sqlheper.get_list("select id from course where course_name=%s order by id", [cname, ])
        cid = cid[0].get('id')
        course_number = 'c' + str(cid)
        sqlheper.modify("update course set course_number=%s where id=%s", [course_number, cid])
        operationlogs.operationlogs(request.COOKIES.get('name'), 'add', 'course')
    except Exception as e:
        # 添加失败返回错误信息
        ret['status'] = False
        ret['message'] = str(e)
    return HttpResponse(json.dumps(ret))


def del_course(request):
    """
    删除课程
    """
    course_id = request.POST.get('cid')
    sqlheper.modify('delete from course where id=%s', [course_id, ])
    operationlogs.operationlogs(request.COOKIES.get('name'), 'del', 'course', course_id)
    return HttpResponse('ok')


def edit_course(request):
    """
    编辑课程信息
    """
    nid = request.GET.get('nid')
    if request.method == "GET":
        c = CourseList()
        sql = "select * from course where id=%s"
        result = sqlheper.get_list(sql, [nid, ])
        return render(request, 'edit_course.html', {'result': result[0], 'teacher_list': c.teacher_list})
    else:
        ret = {'status': True, 'message': None}
        try:
            c = CourseList()
            c.edit_check(request.POST)
            edit_list = list(request.POST.values())
            sql = "update course set course_name=%s,credit=%s,teacher_number=%s where id=%s"
            operationlogs.operationlogs(request.COOKIES.get('name'), 'edit', 'course', edit_list[-1],
                                        json.dumps(request.POST))
            sqlheper.modify(sql, edit_list)
        except Exception as e:
            ret['status'] = False
            ret['message'] = str(e)
            print(e.__traceback__.tb_lineno)
        return HttpResponse(json.dumps(ret))


def search_course(request):
    """
    查询课程信息
    """
    if request.method == 'POST':
        search = request.POST.get('search')
        search_list = sqlheper.get_list(
            "select course.id,course_name,teacher.name,credit,status from course left join teacher on course.teacher_number=teacher.teacher_number where course_name like '%%%%%s%%%%'" % (
                search),
            [])
        course_list_obj = CourseList(search_list)
        return render(request, 'course.html', {'course_list_obj': course_list_obj})


def open_course(request):
    """
    开启选课
    """
    ret = {'status': True, 'message': '开启成功'}
    open_list = request.POST.get('check_val')
    open_list = json.loads(open_list)
    try:
        for i in open_list:
            sql = "update course set status=%s where id=%s"
            operationlogs.operationlogs(request.COOKIES.get('name'), 'edit', 'course', i['id'],
                                        '开启选课')
            sqlheper.modify(sql, ['可选', i['id']])
    except Exception as e:
        ret['status'] = False
        ret['message'] = str(e)
    return HttpResponse(json.dumps(ret))


def close_course(request):
    """
    关闭选课
    """
    ret = {'status': True, 'message': '关闭成功'}
    open_list = request.POST.get('check_val')
    open_list = json.loads(open_list)
    try:
        for i in open_list:
            sql = "update course set status=%s where id=%s"
            operationlogs.operationlogs(request.COOKIES.get('name'), 'edit', 'course', i['id'],
                                        '关闭选课')
            sqlheper.modify(sql, ['不可选', i['id']])
    except Exception as e:
        ret['status'] = False
        ret['message'] = str(e)
    return HttpResponse(json.dumps(ret))


class CourseList(object):
    # 对课程数据进行处理
    def __init__(self, course_list=[], start=0, end=10000):
        self.course_list = course_list
        self.course_list_page = self.course_list[start: end]
        self.teacher_list = sqlheper.get_list("select id,name,teacher_number from teacher", [])
        self.all_count = len(course_list)

    def nid(self, value):
        pass

    def course_name(self, value):
        if not value:
            raise ValueError('课程名不能为空!')

    def teacher_number(self, value):
        # tea_list = sqlheper.get_list('select id from teacher', [])
        # for i in tea_list:
        #     for k, v in i.items():
        #         if value == v:
        #             return 0
        # raise ValueError('教师不存在!')
        pass

    def credit(self, value):
        if not value:
            raise ValueError('学分不能为空!')
        if not value.isdigit():
            raise ValueError('学分格式错误!')

    # 对添加的课程信息进行校验
    def add_check(self, dic):
        dic = dic.dict()
        for key, value in dic.items():
            methodcaller(key, value)(self)

    # 对编辑的课程信息进行校验
    def edit_check(self, dic):
        dic = dic.dict()
        for key, value in dic.items():
            methodcaller(key, value)(self)
