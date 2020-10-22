import pymysql
import json
import pandas as pd
from django.http import HttpResponse
import tkinter as tk
from tkinter import filedialog


def get_list(sql, args):
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root', password='pan86179939',
        database='student',
        charset='utf8'
    )
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute(sql, args)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


def get_list_value(sql, args):
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root', password='pan86179939',
        database='student',
        charset='utf8'
    )
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute(sql, args)
    result_d = cursor.fetchall()
    result = []
    for i in result_d:
        for key, value in i.items():
            result.append(value)
    cursor.close()
    conn.close()
    return result


def modify(sql, args):
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root', password='pan86179939',
        database='student',
        charset='utf8'
    )
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute(sql, args)
    conn.commit()
    cursor.close()
    conn.close()


def export(request):
    """
    导出为csv
    :param request:
    """
    ret = {'status': True, 'message': None}
    try:
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root', password='pan86179939',
            database='student',
            charset='utf8'
        )
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        table = request.POST.get('table')
        cursor.execute(f"select * from {table}")
        data = cursor.fetchall()
        # 得到所有数据的描述
        columnDes = cursor.description
        # 通过描述，得到列名称
        columnNames = [columnDes[i][0] for i in range(len(columnDes))]
        df = pd.DataFrame(data)
        # 修改df列名称为数据库里的列名称
        df.columns = columnNames
        df.to_csv(f'd:/{table}.csv', encoding='gbk')
        cursor.close()
        conn.close()
    except Exception as e:
        ret['status'] = False
        ret['message'] = str(e)
    return HttpResponse(json.dumps(ret))


def sel_path():
    root = tk.Tk()
    root.withdraw()

    folderpath = filedialog.askdirectory()  # 获得选择好的文件夹
    answer = filedialog.askopenfilename()

    print('filepath:', folderpath)