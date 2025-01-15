"""
虚拟物品 自动发货脚本
"""


"""
淘宝自动发货
1. 获取订单信息
2. 发送消息
"""


import requests
import json, time


# 发送请求，调用淘宝api接口
def get_taobao_product_data(params, app_secret):

    # 根据App Secret生成签名
    params['sign'] = generate_sign(params, app_secret)
    # print(params)

    # 发送请求
    response = requests.get('https://gw.api.taobao.com/router/rest', params=params)


    # 解析响应数据
    data = json.loads(response.text)
    print(data)
    if data.get('success'):
        return data['result']['items']
    else:
        return None


# session: 6100600f11816cfbfc65b7c2177a47a72e2b4f4a81de5133675831756
# refresh_token: 6101600218c6e9be5b7cd4bb043e432a0d154c8d67f22c73675831756


def generate_sign(params, app_secret):
    # 将参数按照字母顺序排序
    sorted_params = sorted(params.items(), key=lambda x: x[0])
    # print(sorted_params)

    # 构造待签名字符串
    sign_string = app_secret
    for key, value in sorted_params:
        if key != 'sign' and value is not None:
            sign_string += key + value
    sign_string += app_secret

    # print(sign_string)
    # 生成签名
    import hashlib
    md5 = hashlib.md5()
    md5.update(sign_string.encode('utf-8'))
    return md5.hexdigest().upper()


# 使用你的App Key和App Secret
app_key = '34816000'
app_secret = 'cf5802e09f3d450dbd6c8a13da685875'


# 淘宝客-推广者-物料id列表查询
def get_material_ids():
    method = 'taobao.tbk.optimus.tou.material.ids.get'
    # 构造请求参数
    params = {
        'app_key': app_key,
        'method': method,
        'timestamp': str(int(time.time())),
        'format': 'json',
        'v': '2.0',
        'sign_method': 'md5',
        'session': '6100600f11816cfbfc65b7c2177a47a72e2b4f4a81de5133675831756',
        'material_query': "{'subject': 1,'material_type': 1}",
    }
    # 调用函数获取商品数据
    product_data = get_taobao_product_data(params, app_secret)


# 查询卖家已经卖出的交易数据
def get_trades_sold():
    method = 'taobao.trade.fullinfo.get'
    # 构造请求参数
    params = {
        'app_key': app_key,
        'method': method,
        'timestamp': str(int(time.time())),
        'format': 'json',
        'v': '2.0',
        'sign_method': 'md5',
        'session': '6100600f11816cfbfc65b7c2177a47a72e2b4f4a81de5133675831756',
    }
    # 调用函数获取商品数据
    product_data = get_taobao_product_data(params, app_secret)


# 无需物流发货处理
def get_send_dummy():
    method = 'taobao.logistics.dummy.send'
    # 构造请求参数
    params = {
        'app_key': app_key,
        'method': method,
        'timestamp': str(int(time.time())),
        'format': 'json',
        'v': '2.0',
        'sign_method': 'md5',
        'session': '6100600f11816cfbfc65b7c2177a47a72e2b4f4a81de5133675831756',
    }
    # 调用函数获取商品数据
    product_data = get_taobao_product_data(params, app_secret)

get_send_dummy()


















