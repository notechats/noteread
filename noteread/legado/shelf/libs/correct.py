import json

from noteread.legado.shelf.base import BookSource, BookSourceCorrect


def check_contain_unusual(s):
    """包含汉字的返回TRUE"""
    if s is None:
        return False
    for c in s:
        if c in (' ', '\u011f'):
            return True
        # if (c < '\u4e00' or c > '\u9fa5') and c not in ('\u2603', ' ', '\u0e05'):
        #    return True
    return False


def check_contain_chinese(s):
    """包含汉字的返回TRUE"""
    if s is None:
        return False
    for c in s:
        if '\u4e00' <= c <= '\u9fa5':
            return True
    return False


class SourceDetail:
    def __init__(self, data):
        self.data = json.loads(data, encoding='utf-8')
        self.valid = True
        self.check()
        if self.valid:
            self.handle()
            # print(self.data)
            # print(self.data.get('bookSourceGroup', ''), self.data.get('bookSourceComment', ''))

    def check(self):
        if check_contain_unusual(self.data.get('bookSourceGroup')):
            self.valid = False
            return self.valid

    def handle(self):
        if 'bookSourceComment' in self.data.keys() and len(self.data['bookSourceComment']) > 10:
            self.data['bookSourceComment'] = '默认'


def correct_source(book: BookSource = None, book_correct: BookSourceCorrect = None):
    book = book or BookSource(lanzou_fid=4147049)
    book_correct = book_correct or BookSourceCorrect(lanzou_fid=4147049)

    for shelf in book.select_all():
        source = SourceDetail(data=shelf['jsons'])
        if not source.valid:
            continue
        book_correct.add_json(json.dumps(source.data),
                              md5=shelf['md5'],
                              cate1=shelf['cate1'],
                              cate2=shelf['cate2'],
                              cate3=shelf['cate3'])
