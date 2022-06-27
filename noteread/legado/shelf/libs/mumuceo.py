import json
import time

import requests
from bs4 import BeautifulSoup
from noteread.legado.shelf.base import BookSource
from tqdm import tqdm

APPS = ["yuedu", "yiciyuan", "haikuo"]

SHU_YUAN = "shuyuan"
RSS_YUAN = "rssyuan"
TU_YUAN = "tuyuan"
YING_SHI = "yingshi"
SHI_JIE = "shijie"


def _mumuceo_post(url, data):
    cookies = {
        'PHPSESSID': 'kpdm15hmllfncivlvvqi1e4kq8',
        'Hm_lvt_cd7f08c81646ae0a1ee6c3d93b9956d5': '1631932124,1631959496,1633659120',
        'Hm_lpvt_cd7f08c81646ae0a1ee6c3d93b9956d5': '1633683013',
    }

    headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Mobile Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'http://yck.mumuceo.com',
        'Referer': 'http://yck.mumuceo.com/yuedu/rssyuan/index.html',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    response = requests.post(url, headers=headers, cookies=cookies, data=data, verify=False)
    return response


def _mumuceo_data_list(app=APPS[0], source=SHU_YUAN, page=1, limit=100):
    data = {
        'page': page,
        'limit': limit
    }
    response = _mumuceo_post(url=f'http://yck.mumuceo.com/{app}/{source}/index.html', data=data)
    try:
        return json.loads(response.text)
    except Exception as e:
        print(f'{e}\t{response.text}')
        return []


def _mumuceo_detail(app=APPS[0], source=SHU_YUAN, _id='10'):
    params = {
        'id': _id
    }
    response = _mumuceo_post(f'http://yck.mumuceo.com/{app}/{source}/yuan.html', data=params)

    soup = BeautifulSoup(response.text, features="lxml")
    res = soup.find_all(class_='layui-code')
    if len(res) > 0:
        return json.loads(res[0].text)
    else:
        return {}


def load_from_mumuceo(app=APPS[0],
                      source=SHU_YUAN,
                      page=100,
                      cate1='1',
                      book: BookSource = None):
    for _page in tqdm(range(1, 100)):
        df = _mumuceo_data_list(app=app, source=source, page=_page, limit=page)
        size = len(df['data'])
        if size == 0:
            break
        for d in df['data']:
            try:
                d2 = _mumuceo_detail(app=app, source=source, _id=d['id'])
                d2 = json.dumps(d2)
                book.add_json(d2, cate1=cate1)
                time.sleep(0.1)
            except Exception as e:
                print(e)
