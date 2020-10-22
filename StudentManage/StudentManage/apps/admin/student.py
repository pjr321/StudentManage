import string
from string import digits
from django.shortcuts import render, redirect
from django.http import HttpResponse
from utils import sqlheper, pager, operationlogs
import json
import re
from operator import methodcaller


def student(request):
    """
    学生管理首页
    """
    # 检验用户是否登录
    tk = request.COOKIES.get('ticket')
    if not tk:
        return redirect('/sign/')
    # 获得url
    url = '/student/?'
    if request.GET.get('per_page'):
        url = '/student/?per_page=' + request.GET.get('per_page') + '&'
    # 展示学生信息
    if request.GET.get('sort') == "desc":
        # 倒排
        url = "/student/?sort=desc&"
        slist = sqlheper.get_list(
            "select student.id,name,student_id,sex,telephone,major_name,class.title from student left join class on class.id=class_id order by student.id DESC",
            [])
    else:
        slist = sqlheper.get_list(
            "select student.id,name,student_id,sex,telephone,major_name,class.title from student left join class on class.id=class_id order by student.id",
            [])
    student_number = len(sqlheper.get_list("select * from student", []))
    all_count = student_number  # 学生表数据条数
    current_page = 1
    if request.GET.get('page'):
        current_page = int(request.GET.get('page'))  # 当前页码
    per_page = 10  # 默认每页数据条数
    if request.GET.get('per_page'):
        per_page = int(request.GET.get('per_page'))
    # 新建一个分页器
    page_info = pager.PageInfo(current_page, all_count, per_page, url)
    # 将学生表切片，只展示当前页所需学生信息
    start, end = page_info.start(), page_info.end()
    student_list_obj = StudentList(slist, start, end)
    major = sqlheper.get_list('select major_name from major', [])
    return render(request, 'student.html', {'student_list_obj': student_list_obj, 'per_page': per_page,
                                            'page_info': page_info,
                                            'class_list': json.dumps(student_list_obj.class_list),
                                            'major': major, 'url': request.get_full_path()
                                            })


def add_student(request):
    """
    添加学生
    """
    ret = {'status': True, 'message': None}
    try:
        name = request.POST.get('name')
        s = StudentList()
        s.add_check(request.POST)  # 校验
        print(request.POST)
        add_list = list(request.POST.values())  # 待添加的数据
        sqlheper.modify("insert into student(name,sex,major_name,class_id) values(%s,%s,%s,%s)", add_list)
        # 自动生成学号
        sid = sqlheper.get_list("select id from student where name=%s order by id DESC", [name, ])
        sid = sid[0].get('id')
        year = ['2017', '2018', '2019', '2020']  # 年份
        job = ['320', '321', '322']  # 工号
        student_id = str(sid).zfill(3)  # 序号，三位数
        student_id = year[-1] + job[2] + student_id

        sqlheper.modify("update student set student_id=%s where id=%s", [student_id, sid])
        operationlogs.operationlogs(request.COOKIES.get('name'), 'add', 'student')
    except Exception as e:
        # 添加失败返回错误信息
        ret['status'] = False
        ret['message'] = str(e)
    return HttpResponse(json.dumps(ret))


def del_student(request):
    """
    删除学生
    """
    student_id = request.POST.get('sid')
    sqlheper.modify('delete from student where id=%s', [student_id, ])
    operationlogs.operationlogs(request.COOKIES.get('name'), 'del', 'student', student_id)
    return HttpResponse('ok')


def edit_student(request):
    """
    编辑学生信息
    """
    if request.method == "GET":
        nid = request.GET.get('nid')
        sql = "select * from student where id=%s"
        result = sqlheper.get_list(sql, [nid, ])
        class_list = sqlheper.get_list("select id,title from class", [])
        major = sqlheper.get_list('select major_name from major', [])
        return render(request, 'edit_student.html', {'result': result[0], 'class_list': class_list, 'major': major})
    else:
        ret = {'status': True, 'message': None}
        try:
            s = StudentList()
            s.edit_check(request.POST)
            stu_dict = list(request.POST.values())
            sql = "update student set name=%s,sex=%s,nation=%s,native_place=%s,birth_date=%s,telephone=%s,major_name=%s,class_id=%s where id=%s"
            operationlogs.operationlogs(request.COOKIES.get('name'), 'edit', 'student', stu_dict[-1],
                                        json.dumps(request.POST))
            sqlheper.modify(sql, stu_dict)

        except Exception as e:
            ret['status'] = False
            ret['message'] = str(e)
        return HttpResponse(json.dumps(ret))


def search_student(request):
    """
    查询学生信息
    """
    if request.method == 'POST':
        search = request.POST.get('search')
        # 校验输入信息为学号或是姓名
        if re.match(r'^\d+', search):
            # 学号
            search_list = sqlheper.get_list(
                "select student.id,name,student_id,sex,telephone,class.title from student left join class on class.id=class_id where student_id like '%%%%%s%%%%'" % (
                    search),
                [])
        elif re.match('[\u4E00-\u9FA5]+', search):
            # 姓名
            search_list = sqlheper.get_list(
                "select student.id,name,student_id,sex,telephone,class.title from student left join class on class.id=class_id where name like '%%%%%s%%%%'" % (
                    search),
                [])
        student_list_obj = StudentList(search_list)
        return render(request, 'student.html', {'student_list_obj': student_list_obj})


def export(request):
    ret = {'status': True, 'message': None}
    try:
        sqlheper.export('select * from student', [])
    except Exception as e:
        ret['status'] = False
        ret['message'] = str(e)
    return HttpResponse(json.dumps(ret))


class StudentList(object):
    # 对学生数据进行处理
    def __init__(self, student_list=None, start=0, end=10000):
        if student_list is None:
            student_list = []
        self.student_list = student_list
        self.student_list_page = self.student_list[start: end]
        self.class_list = sqlheper.get_list("select id,title from class", [])
        self.all_count = len(student_list)

    def nid(self, value):
        pass

    def sex(self, value):
        if value not in ['男', '女']:
            raise ValueError('性别格式有误!')

    def name(self, value):
        if not value:
            raise ValueError('姓名不能为空!')
        if not re.match('[\u4E00-\u9FA5]+', value):
            raise ValueError('姓名格式错误!')

    def nation(self, value):
        if not re.match('[\u4E00-\u9FA5]+', value):
            raise ValueError('民族格式错误!')

    def birth_date(self, value):
        if not re.match("^(((19|20)[0-9]{2})-(1[0-2]|[1-9])-(3[01]|[12][0-9]|[1-9]))$", value):
            raise ValueError('生日格式错误!')

    def native_place(self, value):
        if not re.match('[\u4E00-\u9FA5]+', value):
            raise ValueError('籍贯格式错误!')

    def telephone(self, value):
        if not re.match(r'^1[345678]\d{9}$', value):
            raise ValueError('手机号格式错误!')

    def class_id(self, value):
        if not value:
            raise ValueError('请选择班级!')

    def major_name(self, value):
        if not value:
            raise ValueError('请选择专业!')

    def major_class(self, m, c):
        """
        校验班级与专业是否匹配
        """
        class_name = sqlheper.get_list_value('select title from class where id=%s', [c, ])[0]
        class_name = class_name.replace('班', '')
        # 去除其中的数字
        class_type = class_name.rstrip(string.digits)
        print(m, class_type)
        if class_type not in m:
            raise ValueError('请选择专业对应的班级!')

    def add_check(self, dic):
        dic = dic.dict()
        major = ''
        class_id = ''
        for key, value in dic.items():
            if key == 'major_name':
                major = value
            elif key == 'class_id':
                class_id = value
            methodcaller(key, value)(self)
        self.major_class(major, class_id)

    def edit_check(self, dic):
        dic = dic.dict()
        major = ''
        class_id = ''
        for key, value in dic.items():
            if key == 'major_name':
                major = value
            elif key == 'class_id':
                class_id = value
            methodcaller(key, value)(self)
        self.major_class(major, class_id)
