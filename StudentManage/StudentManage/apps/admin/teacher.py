from django.shortcuts import render, redirect
from django.http import HttpResponse
from utils import sqlheper, pager, operationlogs
import json
import re
from operator import methodcaller


def teacher(request):
    """
    教师管理首页
    """
    # 检验用户是否登录
    tk = request.COOKIES.get('ticket')
    if not tk:
        return redirect('/sign/')
    # 获得url
    url = '/teacher/?'
    if request.GET.get('per_page'):
        url = '/teacher/?per_page=' + request.GET.get('per_page') + '&'
    # 展示教师信息
    if request.GET.get('sort') == "desc":
        # 倒排
        url = "/teacher/?sort=desc&"
        tlist = sqlheper.get_list(
            "select id,name,sex,teacher_number,telephone from teacher order by id DESC",
            [])
    else:
        # 正序
        tlist = sqlheper.get_list(
            "select id,name,sex,teacher_number,telephone from teacher",
            [])
    teacher_number = len(sqlheper.get_list("select * from teacher", []))
    all_count = teacher_number  # 教师表数据条数
    current_page = 1  # 默认当前页
    if request.GET.get('page'):
        current_page = int(request.GET.get('page'))  # 当前页码
    per_page = 10  # 默认每页数据条数
    if request.GET.get('per_page'):
        per_page = int(request.GET.get('per_page'))
    # 新建一个分页器
    page_info = pager.PageInfo(current_page, all_count, per_page, url)
    start, end = page_info.start(), page_info.end()
    teacher_list_obj = TeacherList(tlist, start, end)
    return render(request, 'teacher.html', {'teacher_list_obj': teacher_list_obj, 'per_page': per_page,
                                            'page_info': page_info,
                                            'url': request.get_full_path()
                                            })


def add_teacher(request):
    """
    添加教师
    """
    ret = {'status': True, 'message': None}
    try:
        name = request.POST.get('name')
        c = TeacherList()
        c.add_check(request.POST)  # 校验
        add_list = list(request.POST.values())  # 待添加的数据
        sqlheper.modify("insert into teacher(name,sex,telephone) values(%s,%s,%s)", add_list)
        tid = sqlheper.get_list("select id from teacher where name=%s order by id", [name, ])
        tid = tid[0].get('id')
        teacher_number = 't' + str(tid)
        sqlheper.modify("update teacher set teacher_number=%s where id=%s", [teacher_number, tid])
        operationlogs.operationlogs(request.COOKIES.get('name'), 'add', 'course')
    except Exception as e:
        # 添加失败返回错误信息
        ret['status'] = False
        ret['message'] = str(e)
    return HttpResponse(json.dumps(ret))


def del_teacher(request):
    """
    删除教师
    """
    teacher_id = request.POST.get('tid')
    sqlheper.modify('delete from teacher where id=%s', [teacher_id, ])
    return HttpResponse('ok')


def edit_teacher(request):
    """
    编辑教师信息
    """
    if request.method == "GET":
        nid = request.GET.get('nid')
        sql = "select * from teacher where id=%s"
        result = sqlheper.get_list(sql, [nid, ])
        return render(request, 'edit_teacher.html', {'result': result[0]})
    else:
        ret = {'status': True, 'message': None}
        try:
            c = TeacherList()
            c.edit_check(request.POST)
            edit_list = list(request.POST.values())
            sql = "update teacher set name=%s,birth_date=%s,telephone=%s,nation=%s,native_place=%s where id=%s"
            sqlheper.modify(sql, edit_list)
        except Exception as e:
            ret['status'] = False
            ret['message'] = str(e)
        return HttpResponse(json.dumps(ret))


def search_teacher(request):
    """
    查询教师信息
    """
    if request.method == 'POST':
        search = request.POST.get('search')
        search_list = sqlheper.get_list(
            "select teacher.id,teacher.name,sex,teacher_number,telephone from teacher where name like '%%%%%s%%%%'" % (
                search),
            [])
        teacher_list_obj = TeacherList(search_list)
        return render(request, 'teacher.html', {'teacher_list_obj': teacher_list_obj})


class TeacherList(object):
    # 对教师数据进行处理
    def __init__(self, teacher_list=[], start=0, end=10000):
        self.teacher_list = teacher_list
        self.teacher_list_page = self.teacher_list[start: end]
        self.all_count = len(teacher_list)

    def nid(self, value):
        pass

    def sex(self,value):
        if not value:
            raise ValueError('性别不能为空！')

    def name(self, value):
        if not value:
            raise ValueError('姓名不能为空!')
        if not re.match('[\u4E00-\u9FA5]+', value):
            raise ValueError('姓名格式错误!')

    def tel(self, value):
        if not re.match(r'^1[345678]\d{9}$', value):
            raise ValueError('手机号格式错误!')

    def nation(self, value):
        if not value:
            raise ValueError('民族不能为空!')
        if not re.match('[\u4E00-\u9FA5]+', value):
            raise ValueError('民族格式错误!')

    def birth(self, value):
        if not value:
            return
        if not re.match("^(((19|20)[0-9]{2})-(1[0-2]|[1-9])-(3[01]|[12][0-9]|[1-9]))$", value):
            raise ValueError('生日格式错误!')

    def native_place(self, value):
        if not re.match('[\u4E00-\u9FA5]+', value):
            raise ValueError('籍贯格式错误!')

    # 对添加的教师信息进行校验
    def add_check(self, dic):
        dic = dic.dict()
        for key, value in dic.items():
            methodcaller(key, value)(self)

    # 对编辑的教师信息进行校验
    def edit_check(self, dic):
        dic = dic.dict()
        for key, value in dic.items():
            methodcaller(key, value)(self)
