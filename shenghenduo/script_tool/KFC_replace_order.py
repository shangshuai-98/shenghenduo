"""肯德基代下单"""
import json, time, requests






def kf_get_KFC_coupon_goods(word, sku):
    url = "https://test.haomachina.cn/api/Coupon/getGoods"
    payload = json.dumps({
        "page": 1,
        "goodsType": 1,
        "type": 2,
        "word": f'{word}'
    })
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Host': 'test.haomachina.cn',
        'Connection': 'keep-alive'
    }
    response = requests.request("POST", url, headers=headers, data=payload)

    # print(json.loads(response.text))
    response_text = json.loads(response.text)
    # response_text = {'allCount': 1, 'allPage': 1, 'code': 1000, 'data': [{'id': 2257, 'number': 1836, 'name': '①号货源 23元面值  瑞幸咖啡 ', 'price': 0, 'money': 8.13, 'type': 1, 'day': 0, 'keyId': 8, 'status': 1, 'multiple': 1, 'isRepeat': 0, 'skuType': 0}], 'msg': '获取成功'}
    data = response_text.get('data')
    if data:
        pwd = ''
        for i in data:
            if int(i.get('status')) != 1:
                continue
            print(i.get('id'))
            url = "https://guchi.haomachina.cn/api/Coupon/addOrder"
            payload = json.dumps({
                "id": i.get('id'),
                "count": 1,
                "payType": 0,
                "sku": sku
            })
            # print(payload)
            response = requests.request("POST", url, headers=headers, data=payload)
            response_text = json.loads(response.text)
            # response_text = {'cards': [{'number': '', 'pwd': 'https://luckin.hqyi.net/#/?code=JBk4BJBbBupeqpNTlf', 'time': '', 'gifts': ''}], 'code': 1000, 'id': 155364, 'msg': '购买成功', 'number': '20241228151832574'}
            # print(response_text)
            cards = response_text.get('cards')
            pwd = cards[0].get('pwd')
            print(pwd)
            break
        if pwd:
            return pwd
        else:
            return ''
    else:
        return ''



# 选择店铺
def select_stores(gbCityCode, keyword):
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://xd.foodyh.cn",
        "Referer": "https://xd.foodyh.cn/?dp=1&order=20250108103332474",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "X-Requested-With": "XMLHttpRequest"
    }
    url = "https://xd.foodyh.cn/index/index/keywordgetstores.html"
    data = {
        "gbCityCode": gbCityCode,
        "keyword": keyword
    }
    response = requests.post(url, headers=headers, data=data)
    return response


# 店铺时间
def get_break_fasttime(storecode):
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://xd.foodyh.cn",
        "Referer": "https://xd.foodyh.cn/?dp=1&order=20250108103332474",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "X-Requested-With": "XMLHttpRequest"
    }
    url = "https://xd.foodyh.cn/index/index/getbreakfasttime.html"
    data = {
        "storecode": storecode
    }
    response = requests.post(url, headers=headers, data=data)
    return response


# 提交订单
def submit_order(data):
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://xd.foodyh.cn",
        "Referer": "https://xd.foodyh.cn/?dp=1&order=20250108103332474",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "X-Requested-With": "XMLHttpRequest"
    }
    url = "https://xd.foodyh.cn/index/index/submit.html"
    # data = {
    #     "order": "20250108103332474",
    #     "remark": "",
    #     "storeCode": "ZGZ179",
    #     "cityName": "焦作",
    #     "packType": "1",
    #     "bookingTime": "1736381700000",
    #     "haveFail": "0",
    #     "address": ""
    # }
    response = requests.post(url, headers=headers, data=data)
    return response


# 获取取餐码
def get_order_info(orderId):
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://xd.foodyh.cn",
        "Referer": "https://xd.foodyh.cn/?dp=1&order=20250108103332474",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "X-Requested-With": "XMLHttpRequest"
    }
    url = "https://xd.foodyh.cn/index/index/getorderinfo.html"
    data = {
        "orderId": orderId
    }
    response = requests.post(url, headers=headers, data=data)
    # print(json.loads(response.text))
    return response

# gbCityCode = 410800
# keyword = '塔南餐厅'
# code_url = 'https://xd.foodyh.cn/?dp=1&order=20250108103332474'
# code_url = 'https://xd.foodyh.cn/?dp=1&order=20250108180300942'
# code_url = 'https://xd.foodyh.cn/?dp=1&order=20250109101629962'
# code_url = 'https://xd.foodyh.cn/?dp=1&order=20250109112236666'
# 兑换优惠券
def exchange_coupons(gbCityCode, keyword, code_url):
    orderId = code_url.split('order=')[-1]

    stores_stores = select_stores(gbCityCode, keyword)
    stores_text = json.loads(stores_stores.text)
    # stores_text = {'code': 200, 'data': {'code': 0, 'data': {'haveMore': False, 'stores': [{'storecode': 'ZGZ179', 'storename': '塔南餐厅', 'starttime': '06:00', 'endtime': '23:00', 'address': '塔南路摩登商业步行街2号楼一层卖场内', 'status': 1, 'bookingExt': {'timeCurStr': '2025-01-08 14:52:49', 'timeCur': 1736319169054, 'bookingArr': [['15:30-22:45'], ['06:15-09:15']], 'bookingOffList': [[], {'off': ['09:30-23:00']}], 'bookingArrOrigin': [['06:15-22:45'], ['06:15-09:15']], 'boolInTime': True, 'boolOpenTime': True, 'boolImmediate': True, 'isShowMenu': 1, 'disable': False, 'boolBooking': True, 'boolTomorrow': True, 'boolToday': True, 'storePublicSign': 'ADBCCECE39D199C6BAA95396A2F94648'}, 'citycode': '01737', 'cityName': '焦作', 'marketcode': '086', 'districtcode': '02676', 'districtName': '山阳区', 'breakfastStart': '06:00', 'breakfastEnd': '10:00', 'bookingInterval': 15, 'bookingDays': 2, 'dayParts': [{'dayPartCode': '1', 'daypart_from': '06:00', 'daypart_to': '09:30', 'name': '早餐'}, {'dayPartCode': '9', 'daypart_from': '20:00', 'daypart_to': '23:00', 'name': '夜宵0'}, {'dayPartCode': '5', 'daypart_from': '17:00', 'daypart_to': '20:00', 'name': '晚餐'}, {'dayPartCode': '8', 'daypart_from': '09:30', 'daypart_to': '10:00', 'name': '早正餐'}, {'dayPartCode': '3', 'daypart_from': '11:00', 'daypart_to': '14:00', 'name': '午餐'}, {'dayPartCode': '4', 'daypart_from': '14:00', 'daypart_to': '17:00', 'name': '下午茶'}, {'dayPartCode': '2', 'daypart_from': '10:00', 'daypart_to': '11:00', 'name': '正餐'}]}], 'labels': [{'icon': 'https://pcp-pic.hwwt8.com/SPH/e7d9e3e8-2798-4994-9db6-9c0ca2b18207.png', 'labelCode': '13', 'labelName': '早餐', 'labelTypeCode': '4', 'labelTypeName': '营业', 'seqNo': '130', 'typeSeqNo': '4'}, {'icon': 'https://pcp-pic.hwwt8.com/SPH/e7b6c0dd-a1db-4e88-9574-2a9f240ceaf5.png', 'labelCode': '15', 'labelName': '儿童乐园', 'labelTypeCode': '6', 'labelTypeName': '设施', 'seqNo': '150', 'typeSeqNo': '6'}, {'icon': 'https://pcp-pic.hwwt8.com/SPH/5da0314c-66b1-4f6e-af43-b12a13d88474.png', 'labelCode': '17', 'labelName': 'K-Music', 'labelTypeCode': '6', 'labelTypeName': '设施', 'seqNo': '170', 'typeSeqNo': '6'}, {'icon': 'https://pcp-pic.hwwt8.com/SPH/6e9ea6da-5fed-451f-9817-20e697842719.png', 'labelCode': '18', 'labelName': '洗手间', 'labelTypeCode': '6', 'labelTypeName': '设施', 'seqNo': '180', 'typeSeqNo': '6'}]}, 'syncTime': 1736319169054, 'traceId': 'puLsE4IuaugIPlWU', 'env': 'wgb'}}
    # print(stores_text)
    data = stores_text.get('data').get('data')
    # print(data)
    storecode = data.get('stores')[0].get('storecode')
    print(storecode)

    fasttime_stores = get_break_fasttime(storecode)
    fast_text = json.loads(fasttime_stores.text)
    # fast_text = {'code': 200, 'data': {'code': 0, 'data': {'store': {'storecode': 'ZGZ179', 'storename': '塔南餐厅', 'starttime': '06:00', 'endtime': '23:00', 'address': '塔南路摩登商业步行街2号楼一层卖场内', 'status': 1, 'distance': 1376776.0958199773, 'bookingExt': {'timeCurStr': '2025-01-08 15:28:14', 'timeCur': 1736321294157, 'bookingArr': [[], ['06:15-09:15']], 'bookingOffList': [[], {'off': ['09:30-10:00']}], 'bookingArrOrigin': [['06:15-09:45'], ['06:15-09:15']], 'boolInTime': True, 'boolOpenTime': True, 'boolImmediate': False, 'isShowMenu': 0, 'disable': False, 'boolBooking': True, 'boolTomorrow': True, 'boolToday': True, 'storePublicSign': '6082EBCBECB0C728B04C9B97B846B708'}, 'citycode': '01737', 'cityName': '焦作', 'marketcode': '086', 'districtcode': '02676', 'districtName': '山阳区', 'breakfastStart': '06:00', 'breakfastEnd': '10:00', 'bookingInterval': 15, 'bookingDays': 2, 'dayParts': [{'dayPartCode': '1', 'daypart_from': '06:00', 'daypart_to': '09:30', 'name': '早餐'}, {'dayPartCode': '9', 'daypart_from': '20:00', 'daypart_to': '23:00', 'name': '夜宵0'}, {'dayPartCode': '5', 'daypart_from': '17:00', 'daypart_to': '20:00', 'name': '晚餐'}, {'dayPartCode': '8', 'daypart_from': '09:30', 'daypart_to': '10:00', 'name': '早正餐'}, {'dayPartCode': '3', 'daypart_from': '11:00', 'daypart_to': '14:00', 'name': '午餐'}, {'dayPartCode': '4', 'daypart_from': '14:00', 'daypart_to': '17:00', 'name': '下午茶'}, {'dayPartCode': '2', 'daypart_from': '10:00', 'daypart_to': '11:00', 'name': '正餐'}]}, 'systemX': False, 'systemxSwitch': False}, 'syncTime': 1736321294157, 'traceId': 'uMYtRuNvIpx3O9Gz', 'env': 'wgb'}}
    cityName = fast_text.get('data').get('data').get('store').get('cityName')
    print(cityName)

    # bookingTime = '1736640900'
    for n in range(2):
        bookingTime = 0
        data = {
            "order": orderId,
            "remark": "",
            "storeCode": storecode,
            "cityName": cityName,
            "packType": "1",
            "bookingTime": bookingTime,
            "haveFail": n,
            "address": ""
        }
        order_res = submit_order(data)
        print(json.loads(order_res.text))
        if json.loads(order_res.text).get('code') == 200:
            break
    else:
        return {'msg':json.loads(order_res.text).get('msg')}

    print(orderId)
    order_response = get_order_info(orderId)
    order_info_text = json.loads(order_response.text)
    # order_info_text = {'code': 200, 'errCode': 0, 'data': {'orders': [{'phone': '0074', 'extensionPhone': '7828', 'remark': '', 'bookingTime': 0, 'localId': '20250109112236666', 'orderId': '1736392989384172959', 'pickupCode': 'A0062', 'name': '热辣香骨鸡(3块)*5', 'storename': '【焦作】塔南餐厅@外带', 'storecode': 'ZGZ179', 'status': 1, 'create': 1736392993, 'source': 13}], 'links_order': {'status': 2, 'type': 3, 'orderId': '20250109112236666', 'shop_api_id': 0}, 'fail_orders': [], 'payParamUpdateLog': [], 'delivery': []}}
    pickupCode = order_info_text.get('data').get('orders')[0].get('pickupCode')
    takeMealCodeInfo = {"code": pickupCode,"takeOrderId": ""}
    print(takeMealCodeInfo)
    return takeMealCodeInfo





# exchange_coupons(gbCityCode, keyword, code_url)



















