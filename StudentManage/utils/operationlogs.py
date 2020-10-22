from utils import sqlheper
import datetime
import json
from django.http import HttpResponse


def operationlogs(operator, operation, target_table, target_id=None, modify_value=None):
    """
    操作日志
    :param operator: 操作员
    :param operation: 操作
    :param target_table: 对象表
    :param target_id: 对象id
    :param modify_value: 修改值
    """
    time1 = datetime.datetime.now()
    time = datetime.datetime.strftime(time1, '%Y-%m-%d %H:%M:%S')
    if operation == 'edit' and modify_value not in ['开启选课', '关闭选课']:
        # 获取实际更新的数据
        # 获得修改前的数据
        old = sqlheper.get_list(f'select * from {target_table} where id={target_id}', [])[0]
        if target_table == 'student':
            old.pop('id')
            old.pop('student_id')
        elif target_table == 'course':
            old.pop('id')
            old.pop('course_number')
            old.pop('status')
        new = json.loads(modify_value)
        new.pop('nid')
        modify_value = {}
        for key, value in old.items():
            if new[key] != str(value):
                modify_value[key] = new[key]
    sqlheper.modify(
        'insert into operationlogs(operator, operation, target_table, target_id, modify_value,time) values(%s,%s,%s,%s,%s,%s)',
        [operator, operation, target_table, target_id, str(modify_value), time]
        )


def logger(func):
     def inner(*args, **kwargs):
         ret = {'status': True, 'message': None}
         try:
            func(*args, **kwargs)
         except Exception as e:
            ret['status'] = False
            ret['message'] = str(e)
         return HttpResponse(json.dumps(ret))