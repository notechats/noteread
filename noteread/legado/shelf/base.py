import os
from datetime import datetime

from notedrive.tables import SqliteTable
from notetool.secret import get_md5_str, read_secret


class BookSource(SqliteTable):
    def __init__(self, table_name='book_base_source', db_path=None, *args, **kwargs):
        if db_path is None:
            db_path = read_secret(cate1="local", cate2="path", cate3="noteread", cate4="db_path")
        if db_path is None:
            db_path = os.path.abspath(os.path.dirname(__file__)) + '/db/read.accdb'
        super(BookSource, self).__init__(db_path=db_path, table_name=table_name, *args, **kwargs)
        self.columns = ['md5', 'jsons', 'cate1', 'cate2', 'cate3']
        self.create()

    def create(self):
        self.execute("""
            create table if not exists {} (               
              md5           VARCHAR(35) primary key 
              ,jsons        VARCHAR(10000)
              ,cate1        varchar(10)    DEFAULT ''
              ,cate2        varchar(150)   DEFAULT ''
              ,cate3        varchar(150)   DEFAULT ''
              )
            """.format(self.table_name))

    def add_json(self, json_str, cate1="", cate2="", cate3=""):
        md5 = get_md5_str(json_str)
        properties = {
            "md5": md5,
            "jsons": json_str,
            "cate1": cate1,
            "cate2": cate2,
            "cate3": cate3,
        }
        self.insert(properties=properties)


class BookSourceCorrect(BookSource):
    def __init__(self, table_name='book_correct_source', *args, **kwargs):
        super(BookSourceCorrect, self).__init__(table_name=table_name, *args, **kwargs)
        self.columns = ['md5', 'jsons', 'cate1', 'cate2', 'cate3', 'gmt_modified']

    def create(self):
        self.execute("""
            create table if not exists {} (               
              md5           VARCHAR(35)    primary key 
              ,jsons        VARCHAR(10000)
              ,gmt_modified varchar(25)    DEFAULT ''
              ,cate1        varchar(10)    DEFAULT ''
              ,cate2        varchar(150)   DEFAULT ''
              ,cate3        varchar(150)   DEFAULT ''
              )
            """.format(self.table_name))

    def add_json(self, json_str, md5=None, cate1="", cate2="", cate3=""):
        properties = {
            "md5": md5 or get_md5_str(json_str),
            "jsons": json_str,
            "cate1": cate1,
            "cate2": cate2,
            "cate3": cate3,
            "gmt_modified": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        self.insert(properties=properties)
