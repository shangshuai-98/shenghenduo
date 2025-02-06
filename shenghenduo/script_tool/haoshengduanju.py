import pymysql, time, re, jieba, random
import pandas as pd
import numpy as np
import requests
import json, hashlib, base64
from database import connect_mysql
import http.client


def upImage(filePath):
    url = "https://test.haomachina.cn/addons/alioss/index/upload"
    payload = {}
    files = [
        ('file', (filePath, open(filePath, 'rb'), 'image/png'))
    ]
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    print(response.text)
    time.sleep(random.uniform(0.5, 2))
    result = json.loads(response.text)
    if result.get('code') == 1:
        imageUrl = result.get('data').get('url').replace('\/', '/')
        print(imageUrl)
        return imageUrl



md5_her = 'julijuwaiAndroidjulijuwai@2023/07$gogogo'
def md5_encryption(data):
    md5 = hashlib.md5()  # 创建一个md5对象
    md5.update(data.encode('utf-8'))  # 使用utf-8编码数据
    return md5.hexdigest()  # 返回加密后的十六进制字符串



def get_list(page):
    # wp base64编码
    wp = '{"title":"","pageSize":20,"page":'+str(page)+',"wp":"","platformFilter":0,"supplyFilter":0,"publishFilter":0,"category":1,"subCategoryFilter":0,"sortFilter":0,"costTypeFilter":0}'
    wp = base64.b64encode(wp.encode('utf-8')).decode('utf-8')
    print(wp)
    # md5加密
    baseparam = 'julijuwaiandroid149officialandroid10001.4.9' + wp.lower()
    one_md5 = md5_encryption(baseparam)
    at = md5_encryption(md5_her + one_md5)
    print(at)
    url = f"/api/v1/episode/list?subCategoryFilter=0&supplyFilter=&wp={wp}&category=1&title=&platformFilter=0&sortFilter=0&_at={at}&versionName=1.4.9&_atype=Android&_app=julijuwai&_av=149&_channel=official&_platform=android"

    conn = http.client.HTTPSConnection("api.lebuybuy.cn")
    payload = ''
    headers = {
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Accept': '*/*',
        'Host': 'api.lebuybuy.cn',
        'Connection': 'keep-alive',
        'Cookie': 'aliyungf_tc=8bd14494a726688fa79cb012e9c6975cc1732609d0699ba0cbbb663d72860078'
    }
    conn.request("GET",
                 url,
                 payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))
    return json.loads(data.decode("utf-8"))


def get_details(page):
    dataList = get_list(page)
    dataList = dataList.get('data').get('list')
    time.sleep(random.uniform(0.5, 2))
    juList = []
    for data in dataList:
        id = data.get('id')
        print(id)
        basestr = f'julijuwaiandroid149officialandroid1{id}01.4.9'
        one_md5 = md5_encryption(basestr)
        at = md5_encryption(md5_her + one_md5)
        baseparam = f"id={id}&category=1&platform=0&versionName=1.4.9&_atype=Android&_app=julijuwai&_av=149&_channel=official&_platform=android&_at={at}"
        url = '/api/v1/episode/detail?' + baseparam
        conn = http.client.HTTPSConnection("api.lebuybuy.com")
        payload = ''
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'Accept': '*/*',
            'Host': 'api.lebuybuy.com',
            'Connection': 'keep-alive',
            'Cookie': 'aliyungf_tc=847dda78f28f1b254d0196a812da2fecd9502d8eb46ac4cb3fafcd5bb37b6b62; acw_tc=ac11000117337087856886094e8d724176c418f0791848aa841958d284581c'
        }
        print(url)
        conn.request("GET", url, payload, headers)
        res = conn.getresponse()
        time.sleep(random.uniform(0.5, 1))
        data = res.read()
        result = json.loads(data.decode("utf-8"))
        result = result.get('data')
        # print(result)
        title = result.get('title')
        coverImage = result.get('coverImage')
        onlineTime = result.get('onlineTime')
        description = result.get('description')
        netdisk = result.get('netdisk')
        if result.get('tags'):
            classification = result.get('tags')[0]
            tags =[{"labelname": tag} for tag in result.get('tags')]
            tags = str(tags).replace('\'', '\"')
        else:
            tags = []
            classification = '爽剧'
        juList.append(['采集', title, coverImage, onlineTime, description, netdisk, tags, classification])
    # print(juList)
    df = pd.DataFrame(juList)
    filePath = f'src/好省短剧_{int(time.time())}.xlsx'
    df.to_excel(filePath)
    put_sql(filePath)


def put_sql(filePath):
    df = pd.read_excel(filePath)

    df.fillna('', inplace=True)
    df = np.array(df)
    # print(df)

    val = []

    for i in df.tolist():
        i.pop(0)
        # i[5] = json.dumps(i[5], ensure_ascii=False)
        i.append(int(time.time()))
        val.append(tuple(i))
    print(val)

    sql = 'INSERT INTO fa_wanlshop_skits (username, name, fileimage, date, profile, driveurl, label, classification, createtime) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
    connect_mysql(sql, val)


# get_list(3)
get_details(249)
# put_sql(f'src/好省短剧采集数据_1733722963.xlsx')































