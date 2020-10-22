class PageInfo(object):
    def __init__(self, current_page, all_count, per_page, url):
        """
        :param current_page: 当前页
        :param all_count: 总数据条数
        :param per_page: 每页显示数据条数
        """
        self.per_page = per_page
        try:
            self.current_page = current_page
        except Exception as e:
            self.current_page = 1
        a, b = divmod(all_count, per_page)
        if b:
            a = a + 1
        self.all_pager = a
        self.show_page = 11  # 网页显示的页数，可以自行修改
        self.url = url

    def start(self):
        return self.current_page*self.per_page-self.per_page

    def end(self):
        return self.current_page * self.per_page

    # 返回一个字符串给前端，用以显示分页
    def pager(self):
        half = int((self.show_page - 1)/2)
        # 页数超过网页要显示的页数
        if self.all_pager > self.show_page:
            begin = self.current_page - half
            stop = self.current_page + half + 1
            if begin < 1:
                begin = 1
                stop = self.show_page + 1
            if stop > self.all_pager:
                begin = self.all_pager - self.show_page + 1
                stop = self.all_pager + 1
        # 页数小于网页要显示的页数
        else:
            begin = 1
            stop = self.all_pager + 1
        result = []
        if self.current_page <= 1:
            prev = '<li><a href="#">上一页</a></li>'
        else:
            prev = '<li><a href="' + self.url + 'page=%s">上一页</a></li>' % (self.current_page-1)
        result.append(prev)
        for i in range(begin, stop):
            # 选中页特殊标记
            if i == self.current_page:
                a = '<li class="active"><a href="' + self.url + 'page=%s">%s</a></li>' % (i, i,)
            else:
                a = '<li><a href="' + self.url + 'page=%s">%s</a></li>' % (i, i,)
            result.append(a)
        if self.current_page >= self.all_pager:
            nex = '<li><a href="#">下一页</a></li>'
        else:
            nex = '<li><a href="' + self.url + 'page=%s">下一页</a></li>' % (self.current_page+1)
            result.append(nex)
        # 将列表转换成字符串
        return ''.join(result)
