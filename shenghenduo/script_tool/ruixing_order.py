"""
瑞幸代下单脚本
https://luckin.hqyi.net/#/?code=aDWSvnTrVWYmBpNx7H
https://kmapi.hqyi.net/LuckinCoffee/api/getCdkeyInfo?code=aDWSvnTrVWYmBpNx7H
1.接收参数：下单门店，下单商品规格, 优惠券链接
2.选择门店，选择商品，兑换优惠券下单
3.返回取餐码


门店id获取菜单，优惠券信息获取可以兑换的商品id，对比sku确认商品id，下单兑换
"""
import json
import time
import requests
import pandas as pd
from script_tool.database import connect_mysql
from script_tool.KFC_replace_order import exchange_coupons




def request_from(url, method, payload=None, headers=None):
    if not payload:
        payload = {}
    if not headers:
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'Accept': '*/*',
            'Host': 'luffi.cn:8443',
            'Connection': 'keep-alive'
        }
    response = requests.request(method, url, headers=headers, data=payload)
    return response


def down_order(code, deptData, productDataList, remarks):

    url = "https://kmapi.hqyi.net/LuckinCoffee/api/creatOrderTask"

    payload = json.dumps({
    "code": code,
    "deptData": deptData,
    "productDataList": productDataList,
    "remark": remarks
    })
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Host': 'kmapi.hqyi.net',
        'Connection': 'keep-alive'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
    # {"code": 0, "message": "成功", "data": {"oid": "1870408939511169024"}, "error": "null"}
    if json.loads(response.text).get('code') == -1:
        return json.loads(response.text).get('error')
    oid = json.loads(response.text).get('data').get('oid')
    # oid = 1872937873159196672
    # print(oid)

    for _ in range(300):
        url = f"https://kmapi.hqyi.net/LuckinCoffee/api/getOrderTaskInfo?code={code}&oid={oid}"
        payload = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        # print(json.loads(response.text))
        # response_text = {'code': 0, 'message': '成功', 'data': {'oid': '1870408939511169024', 'mobile': '4851', 'orderDetail': {'deptId': 385361, 'remark': '', 'shopName': '焦作摩登街店', 'productList': [{'name': '苹果C果茶', 'amount': 1, 'skuCode': 'SP3152-00022', 'productId': '4732', 'additionDesc': '热/不另外加糖/锡兰红茶', 'bigPicUrl': 'https://img04.luckincoffeecdn.com/group3/M00/82/95/CtxgFGc-3juAL-18AAGLM5YV0Io311.png'}], 'shopAddress': '河南省焦作市山阳区新城街道中海摩登街3-1-1门市', 'orderStatusDesc': '预估取餐时间18:06，感谢您的支持！', 'orderStatusName': '等待取餐', 'takeMealCodeInfo': {'code': '272', 'takeOrderId': 'Z2aRxxrVAAI='}}, 'status': '支付成功', 'error': '', 'retry': 1, 'createdAt': '2024-12-21 18:00:16', 'updatedAt': '2024-12-21 18:00:49'}, 'error': None}
        response_text = json.loads(response.text)
        status = response_text.get('data').get('status')  # 创建中 创建订单成功 支付成功
        print(status)
        time.sleep(1)
        if status == '支付成功':
            orderDetail = response_text.get('data').get('orderDetail')
            takeMealCodeInfo = orderDetail.get('takeMealCodeInfo')
            # {"code": "272","takeOrderId": "Z2aRxxrVAAI="}
            print(takeMealCodeInfo)
            return takeMealCodeInfo


def luck_down_order(sku, count, code, deptId, product_name, price, remarks, city_id, store_name):
    # 瑞幸下单
    if '杯' in sku:
        if 'oz' in sku:
            order_sku_list = sku.split(',')
        else:
            order_sku_list = [sk for sk in sku.split(',') if '杯' not in sk]
    else:
        order_sku_list = sku.split(',')
    productId = get_store_menu(code, deptId, product_name)
    # print(productId)

    url = f"https://kmapi.hqyi.net/LuckinCoffee/api/getProductDetail?deptId={deptId}&productId={productId}"
    print(url)

    payload = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Host': 'kmapi.hqyi.net',
        'Connection': 'keep-alive'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    # print(response.text,6666666)
    response_text = json.loads(response.text)
    # response_text = {'code': 0, 'message': '成功', 'data': {'defaultPicUrl': 'https://img02.luckincoffeecdn.com/group3/M00/83/D0/CtxgFGc_F5CAL2cwAAJTeu2PFN0630.jpg', 'enName': 'Apple Tea', 'htmlDesc': '<p><strong style="color: rgb(102, 102, 102); font-size: 12.5px;">【0脂0咖啡】</strong></p><p><strong style="color: rgb(102, 102, 102); font-size: 12.5px;">【含真实果汁，1杯喝到1.4颗苹果*】</strong></p><p><strong style="color: rgb(102, 102, 102); font-size: 12.5px;">【3款清爽茶底随心选择*，妙趣横生】</strong></p><p><span style="color: rgb(102, 102, 102); font-size: 12.5px;">推荐搭配「锡兰红茶」风味茶底，清甜苹果香气飘逸，四散进洋溢花果蜜香的茶汤里，碰撞出明快甜感，一杯便将整个暖冬轻拥入怀。另外，更有「清新淡雅的茉莉花香」、「岩韵兰香武夷大红袍」风味可供选择，搭配不同茶底，别有风味。</span></p><p><br></p><p><span style="color: rgb(102, 102, 102); font-size: 12.5px;">*本饮品添加苹果复合果蔬汁饮料浓浆。原料选用的苹果平均重约120g（出汁率约70%）。根据配方比例，以出汁率折算对比，本饮品在不另外加糖选项下，约有1.4颗苹果在里面。手工操作可能存在误差，仅供参考。</span></p><p><span style="color: rgb(102, 102, 102); font-size: 12.5px;">*茶风味可选类型请以各门店实际情况为准，下单前请注意查看并确认。</span></p>', 'initialPrice': 23, 'name': '苹果C果茶', 'productId': 4732, 'saleAttrGroup': {'100': '茶风味', '17': '温度', '18': '糖度'}, 'saleAttrGroupValues': {'100': ['锡兰红茶', '茉莉花香', '大红袍乌龙茶'], '17': ['冰', '热'], '18': ['不另外加糖', '微甜', '少少甜', '少甜', '标准甜']}, 'skuList': [{'skuCode': 'SP3152-00018', 'skuSaleAttrValue': {'100': ['茉莉花香'], '17': ['冰'], '18': ['少甜']}}, {'skuCode': 'SP3152-00019', 'skuSaleAttrValue': {'100': ['锡兰红茶'], '17': ['热'], '18': ['少甜']}}, {'skuCode': 'SP3152-00016', 'skuSaleAttrValue': {'100': ['茉莉花香'], '17': ['冰'], '18': ['标准甜']}}, {'skuCode': 'SP3152-00038', 'skuSaleAttrValue': {'100': ['锡兰红茶'], '17': ['热'], '18': ['微甜']}}, {'skuCode': 'SP3152-00017', 'skuSaleAttrValue': {'100': ['大红袍乌龙茶'], '17': ['热'], '18': ['少甜']}}, {'skuCode': 'SP3152-00039', 'skuSaleAttrValue': {'100': ['大红袍乌龙茶'], '17': ['冰'], '18': ['微甜']}}, {'skuCode': 'SP3152-00040', 'skuSaleAttrValue': {'100': ['大红袍乌龙茶'], '17': ['热'], '18': ['微甜']}}, {'skuCode': 'SP3152-00025', 'skuSaleAttrValue': {'100': ['茉莉花香'], '17': ['热'], '18': ['少甜']}}, {'skuCode': 'SP3152-00026', 'skuSaleAttrValue': {'100': ['大红袍乌龙茶'], '17': ['热'], '18': ['不另外加糖']}}, {'skuCode': 'SP3152-00023', 'skuSaleAttrValue': {'100': ['锡兰红茶'], '17': ['冰'], '18': ['不另外加糖']}}, {'skuCode': 'SP3152-00024', 'skuSaleAttrValue': {'100': ['锡兰红茶'], '17': ['冰'], '18': ['少甜']}}, {'skuCode': 'SP3152-00021', 'skuSaleAttrValue': {'100': ['茉莉花香'], '17': ['冰'], '18': ['少少甜']}}, {'skuCode': 'SP3152-00022', 'skuSaleAttrValue': {'100': ['锡兰红茶'], '17': ['热'], '18': ['不另外加糖']}}, {'skuCode': 'SP3152-00020', 'skuSaleAttrValue': {'100': ['茉莉花香'], '17': ['热'], '18': ['少少甜']}}, {'skuCode': 'SP3152-00029', 'skuSaleAttrValue': {'100': ['锡兰红茶'], '17': ['热'], '18': ['少少甜']}}, {'skuCode': 'SP3152-00027', 'skuSaleAttrValue': {'100': ['大红袍乌龙茶'], '17': ['冰'], '18': ['不另外加糖']}}, {'skuCode': 'SP3152-00028', 'skuSaleAttrValue': {'100': ['大红袍乌龙茶'], '17': ['冰'], '18': ['少甜']}}, {'skuCode': 'SP3152-00014', 'skuSaleAttrValue': {'100': ['茉莉花香'], '17': ['热'], '18': ['不另外加糖']}}, {'skuCode': 'SP3152-00036', 'skuSaleAttrValue': {'100': ['大红袍乌龙茶'], '17': ['冰'], '18': ['标准甜']}}, {'skuCode': 'SP3152-00015', 'skuSaleAttrValue': {'100': ['茉莉花香'], '17': ['热'], '18': ['标准甜']}}, {'skuCode': 'SP3152-00037', 'skuSaleAttrValue': {'100': ['锡兰红茶'], '17': ['冰'], '18': ['微甜']}}, {'skuCode': 'SP3152-00012', 'skuSaleAttrValue': {'100': ['茉莉花香'], '17': ['冰'], '18': ['微甜']}}, {'skuCode': 'SP3152-00034', 'skuSaleAttrValue': {'100': ['锡兰红茶'], '17': ['冰'], '18': ['标准甜']}}, {'skuCode': 'SP3152-00013', 'skuSaleAttrValue': {'100': ['茉莉花香'], '17': ['热'], '18': ['微甜']}}, {'skuCode': 'SP3152-00035', 'skuSaleAttrValue': {'100': ['大红袍乌龙茶'], '17': ['热'], '18': ['标准甜']}}, {'skuCode': 'SP3152-00032', 'skuSaleAttrValue': {'100': ['大红袍乌龙茶'], '17': ['冰'], '18': ['少少甜']}}, {'skuCode': 'SP3152-00011', 'skuSaleAttrValue': {'100': ['茉莉花香'], '17': ['冰'], '18': ['不另外加糖']}}, {'skuCode': 'SP3152-00033', 'skuSaleAttrValue': {'100': ['锡兰红茶'], '17': ['冰'], '18': ['少少甜']}}, {'skuCode': 'SP3152-00030', 'skuSaleAttrValue': {'100': ['锡兰红茶'], '17': ['热'], '18': ['标准甜']}}, {'skuCode': 'SP3152-00031', 'skuSaleAttrValue': {'100': ['大红袍乌龙茶'], '17': ['热'], '18': ['少少甜']}}]}, 'error': None}

    sku_list = response_text.get('data').get('skuList')
    for sku in sku_list:
        skuSaleAttrValue = sku.get('skuSaleAttrValue')
        print(sku.get('skuCode'))
        # print(skuSaleAttrValue)
        xxx = 0
        for sku_k, sku_v in skuSaleAttrValue.items():
            print(sku_v)
            if sku_v[0] in order_sku_list:
                xxx += 1
        if xxx >= len(skuSaleAttrValue):
            productData = response_text.get('data')
            productData['skuCode'] = sku.get('skuCode')
            productData['count'] = int(count)
            productData['newprice'] = price
            productDataList = [productData]
            # productDataList = [{"initialPrice": price, "productId": int(productId), "skuCode": sku.get('skuCode'), "count": int(count)}]
            url = f'https://kmapi.hqyi.net/LuckinCoffee/api/getShopList?cityId={city_id}&search={store_name}'
            dept_data = requests.request("GET", url, headers=headers, data=payload)
            dept_data_text = json.loads(dept_data.text)
            otherShopList = dept_data_text.get('data').get('otherShopList')
            deptData = otherShopList[0]
            deptData['cityId'] = city_id
            takeMealCodeInfo = down_order(code, deptData, productDataList, remarks)
            return takeMealCodeInfo
    # print(sku_list)

def get_store_menu(code, deptId, product_name):
    product_name = product_name.replace('(', '（')
    product_name = product_name.replace(')', '）')
    url = f"https://kmapi.hqyi.net/LuckinCoffee/api/getCdkeyInfo?code={code}"

    payload = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Host': 'kmapi.hqyi.net',
        'Connection': 'keep-alive'
    }

    requests.request("GET", url, headers=headers, data=payload)
    time.sleep(0.5)
    response = requests.request("GET", url, headers=headers, data=payload)

    # print(response.text)
    response_text = json.loads(response.text)
    # response_text = {"code":0,"data":{"code":"aDWSvnTrVWYmBpNx7H","status":"1","name":"瑞幸-23面额通兑","productId":"4731,4732,2500,4417,4418,4455,4571,4572","initialPrice":"23,23,23,23,23,23,23,23","productStatus":"1"},"message":"成功"}
    product_id_list = response_text.get('data').get('productId').split(',')
    # 优惠券能兑换下单的商品列表
    print(product_id_list)

    # 根据门店id获取门店菜单
    url = f"https://kmapi.hqyi.net/LuckinCoffee/api/getStaticMenu?deptId={deptId}"

    response = requests.request("GET", url, headers=headers, data=payload)

    # print(response.text, '333333')
    # response_text = {"code":0,"message":"成功","data":{"commodityList":[{"kindDesc":"瑞幸必喝爆款，无限回购","kindName":"人气Top","twoProductList":[{"productList":[{"defaultPicUrl":"https://img03.luckincoffeecdn.com/group1/M00/2F/24/CtwhA2Hnw5-APh3XAAI1QTyCyOU499.png","initialPrice":29,"name":"生椰拿铁","productId":"1262","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img05.luckincoffeecdn.com/group3/M00/1D/B8/CtxgEmbUmxaASNpWAAHQ1KzA06Y488.png","initialPrice":26,"name":"轻轻茉莉","productId":"4541","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img02.luckincoffeecdn.com/group3/M00/02/0B/CtxgEmdZLJuASE7lAAIjjJbHPGo854.png","initialPrice":29,"name":"大冻梨美式","productId":"4698","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img02.luckincoffeecdn.com/group1/M00/D3/42/CtwhAmdZNO-AGRW3AAI04m3VdT8098.png","initialPrice":32,"name":"大冻梨拿铁","productId":"4697","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img02.luckincoffeecdn.com/group1/M00/76/37/CtwhA2cVI-CAaAEsAAJ1L155Z14676.png","initialPrice":32,"name":"小黄油拿铁","productId":"4549","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img05.luckincoffeecdn.com/group2/M00/1F/DA/CtwiPGdNGw6AaibRAAHIukvcnwU165.png","initialPrice":29,"name":"枫丹锡兰轻乳茶","productId":"4642","stockSurplusAmount":"null"}]}]},{"kindDesc":"","kindName":"今日特价","twoProductList":[{"productList":[{"defaultPicUrl":"https://img02.luckincoffeecdn.com/group3/M00/1D/B8/CtxgEmbUmyyAZQ3NAAIYsBljwaM588.png","initialPrice":29,"name":"轻轻茉莉（特大杯）","productId":"4506","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img03.luckincoffeecdn.com/group2/M00/65/32/CtwiPWcnhq2AaLymAAHuMNJXGqg488.png","initialPrice":29,"name":"轻咖柠檬茶（超大杯）","productId":"4448","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img03.luckincoffeecdn.com/group1/M00/2F/24/CtwhA2Hnw5-APh3XAAI1QTyCyOU499.png","initialPrice":29,"name":"生椰拿铁","productId":"1262","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img05.luckincoffeecdn.com/group3/M00/1E/FE/CtxgEmdfoHeAHl3eAAJI9ycs7q0454.png","initialPrice":32,"name":"烤椰拿铁","productId":"4680","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img04.luckincoffeecdn.com/group1/M00/9C/9B/CtwhA2QdDWKAAK2fAAJI2VTEYZQ975.png","initialPrice":29,"name":"橙C美式","productId":"4054","stockSurplusAmount":"null"}]},{"productList":[{"defaultPicUrl":"https://img06.luckincoffeecdn.com/group2/M00/6B/46/CtwiPGdcC72ASBe1AAHti32M4YU297.png","initialPrice":58,"name":"双杯·猎罪图鉴2同款","productId":"PF1452","stockSurplusAmount":"null"}]}]},{"kindDesc":"","kindName":"下午茶","twoProductList":[{"productList":[{"defaultPicUrl":"https://img02.luckincoffeecdn.com/group3/M00/1F/27/CtxgFGdfpNSAcZuyAAIQDOOVWSs886.png","initialPrice":32,"name":"枫丹锡兰轻乳茶（特大杯）","productId":"4643","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img02.luckincoffeecdn.com/group3/M00/1D/B8/CtxgEmbUmyyAZQ3NAAIYsBljwaM588.png","initialPrice":29,"name":"轻轻茉莉（特大杯）","productId":"4506","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img03.luckincoffeecdn.com/group1/M00/76/36/CtwhA2cVI0yAcXkDAAIX-fpCsKc649.png","initialPrice":29,"name":"生椰锡兰轻乳茶（特大杯）","productId":"4667","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img05.luckincoffeecdn.com/group3/M00/1D/B8/CtxgEmbUmgmAOc3-AAIPC3sFji0771.png","initialPrice":29,"name":"轻轻乌龙（特大杯）","productId":"4600","stockSurplusAmount":"null"}]},{"productList":[{"defaultPicUrl":"https://img03.luckincoffeecdn.com/group2/M00/65/32/CtwiPWcnhq2AaLymAAHuMNJXGqg488.png","initialPrice":29,"name":"轻咖柠檬茶（超大杯）","productId":"4448","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img06.luckincoffeecdn.com/group3/M00/0A/C8/CtxgEmcnh_OASGXmAAIMZhTL9WU070.png","initialPrice":32,"name":"葡萄柠檬茶（超大杯）","productId":"4565","stockSurplusAmount":"null"}]}]},{"kindDesc":"","kindName":"东北大冻梨","twoProductList":[{"productList":[{"defaultPicUrl":"https://img02.luckincoffeecdn.com/group1/M00/D3/42/CtwhAmdZNO-AGRW3AAI04m3VdT8098.png","initialPrice":32,"name":"大冻梨拿铁","productId":"4697","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img02.luckincoffeecdn.com/group3/M00/02/0B/CtxgEmdZLJuASE7lAAIjjJbHPGo854.png","initialPrice":29,"name":"大冻梨美式","productId":"4698","stockSurplusAmount":"null"}]},{"productList":[{"defaultPicUrl":"https://img03.luckincoffeecdn.com/group3/M00/04/5D/CtxgEmdZkY-AM80QAALmu6tvu8A506.png","initialPrice":58,"name":"双杯·下午茶放心整【赠周边】","productId":"PF1332","stockSurplusAmount":0},{"defaultPicUrl":"https://img06.luckincoffeecdn.com/group2/M00/5F/7D/CtwiPGdZjBOAArg0AAJLf97fIew478.png","initialPrice":55,"name":"双杯·新品咖咖炫【赠周边】","productId":"PF1418","stockSurplusAmount":0},{"defaultPicUrl":"https://img01.luckincoffeecdn.com/group3/M00/04/55/CtxgFGdZj1-AErIeAAJhh8u_r0c587.png","initialPrice":55,"name":"双杯·爆品库库喝【赠周边】","productId":"PF1422","stockSurplusAmount":0}]}]},{"kindDesc":"","kindName":"生酪拿铁","twoProductList":[{"productList":[{"defaultPicUrl":"https://img04.luckincoffeecdn.com/group2/M00/1D/B6/CtwiPWdMeLaAPDUrAAJsY4Sih4o548.png","initialPrice":32,"name":"新西兰生酪拿铁","productId":"4589","stockSurplusAmount":"null"}]}]},{"kindDesc":"","kindName":"冬日暖咖","twoProductList":[{"productList":[{"defaultPicUrl":"https://img04.luckincoffeecdn.com/group2/M00/1D/B6/CtwiPWdMeLaAPDUrAAJsY4Sih4o548.png","initialPrice":32,"name":"新西兰生酪拿铁","productId":"4589","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img05.luckincoffeecdn.com/group3/M00/1E/FE/CtxgEmdfoHeAHl3eAAJI9ycs7q0454.png","initialPrice":32,"name":"烤椰拿铁","productId":"4680","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img02.luckincoffeecdn.com/group1/M00/D3/42/CtwhAmdZNO-AGRW3AAI04m3VdT8098.png","initialPrice":32,"name":"大冻梨拿铁","productId":"4697","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img03.luckincoffeecdn.com/group1/M00/EF/E4/CtwhAmdfoOSATe5HAAIKPCX03ZE913.png","initialPrice":29,"name":"费尔岛拿铁","productId":"4645","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img06.luckincoffeecdn.com/group1/M00/EF/EA/CtwhAmdfoWKAfrL2AAHVd5rcQqA773.png","initialPrice":32,"name":"太妃榛香拿铁","productId":"4652","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img02.luckincoffeecdn.com/group1/M00/76/37/CtwhA2cVI-CAaAEsAAJ1L155Z14676.png","initialPrice":32,"name":"小黄油拿铁","productId":"4549","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img01.luckincoffeecdn.com/group3/M00/5E/48/CtxgFGZ77feAOrjeAAIvfBrDxSA376.png","initialPrice":26,"name":"燕麦拿铁","productId":"4500","stockSurplusAmount":"null"}]},{"productList":[{"defaultPicUrl":"https://img04.luckincoffeecdn.com/group1/M00/9C/9B/CtwhA2QdDWKAAK2fAAJI2VTEYZQ975.png","initialPrice":29,"name":"橙C美式","productId":"4054","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img03.luckincoffeecdn.com/group1/M00/DB/FA/CtwhAmcnhjaAdwkVAAJ5Em1SwYU169.png","initialPrice":29,"name":"苹果C美式","productId":"4619","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img06.luckincoffeecdn.com/group1/M00/4D/E8/CtwhA2c9etyAESmCAAJptGJaYQo924.png","initialPrice":29,"name":"茉莉花香美式","productId":"4647","stockSurplusAmount":"null"}]},{"productList":[{"defaultPicUrl":"https://img06.luckincoffeecdn.com/group1/M00/75/A2/CtwhAmGTC7qAc2ddAAIcRCRcoYE360.png","initialPrice":29,"name":"丝绒拿铁","productId":"1800","stockSurplusAmount":0}]}]},{"kindDesc":"","kindName":"小黄油系列","twoProductList":[{"productList":[{"defaultPicUrl":"https://img02.luckincoffeecdn.com/group1/M00/76/37/CtwhA2cVI-CAaAEsAAJ1L155Z14676.png","initialPrice":32,"name":"小黄油拿铁","productId":"4549","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img06.luckincoffeecdn.com/group3/M00/A5/12/CtxgFGcVI7SAEQ2qAAJv9FuuRZ4709.png","initialPrice":29,"name":"小黄油美式","productId":"4596","stockSurplusAmount":"null"}]}]},{"kindDesc":"","kindName":"生椰家族","twoProductList":[{"productList":[{"defaultPicUrl":"https://img03.luckincoffeecdn.com/group1/M00/2F/24/CtwhA2Hnw5-APh3XAAI1QTyCyOU499.png","initialPrice":29,"name":"生椰拿铁","productId":"1262","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img05.luckincoffeecdn.com/group3/M00/1E/FE/CtxgEmdfoHeAHl3eAAJI9ycs7q0454.png","initialPrice":32,"name":"烤椰拿铁","productId":"4680","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img01.luckincoffeecdn.com/group3/M00/1E/5D/CtxgFGdfj9CAEdWeAAH-4uIQq0U495.png","initialPrice":26,"name":"生椰美式","productId":"4644","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img02.luckincoffeecdn.com/group1/M00/76/37/CtwhA2cVI2WAFWgUAAHPbwxC4fg751.png","initialPrice":26,"name":"生椰锡兰轻乳茶","productId":"4668","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img03.luckincoffeecdn.com/group1/M00/76/36/CtwhA2cVI0yAcXkDAAIX-fpCsKc649.png","initialPrice":29,"name":"生椰锡兰轻乳茶（特大杯）","productId":"4667","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img01.luckincoffeecdn.com/group1/M00/FF/03/CtwhA2OqvFWANACGAAGpbqlOucU355.png","initialPrice":32,"name":"抹茶好喝椰","productId":"1302","stockSurplusAmount":"null"}]},{"productList":[{"defaultPicUrl":"https://img05.luckincoffeecdn.com/group2/M00/63/25/CtwiPGPyQP2AHvaTAAIU-J06nY0805.png","initialPrice":32,"name":"生椰丝绒拿铁","productId":"1884","stockSurplusAmount":0}]}]},{"kindDesc":"有事没事，来杯美式","kindName":"美式家族","twoProductList":[{"productList":[{"defaultPicUrl":"https://img02.luckincoffeecdn.com/group1/M00/2F/26/CtwhA2Hnw-GABuwhAAIZH9vQLIg476.png","initialPrice":23,"name":"标准美式","productId":"2500","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img05.luckincoffeecdn.com/group2/M00/B3/21/CtwiPGHnxAiAd6UwAAIdb0ZJv1E742.png","initialPrice":26,"name":"加浓美式","productId":"2507","stockSurplusAmount":"null"}]},{"productList":[{"defaultPicUrl":"https://img04.luckincoffeecdn.com/group1/M00/9C/9B/CtwhA2QdDWKAAK2fAAJI2VTEYZQ975.png","initialPrice":29,"name":"橙C美式","productId":"4054","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img03.luckincoffeecdn.com/group1/M00/DB/FA/CtwhAmcnhjaAdwkVAAJ5Em1SwYU169.png","initialPrice":29,"name":"苹果C美式","productId":"4619","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img02.luckincoffeecdn.com/group1/M00/C0/B1/CtwhA2Xt0pyAC5fkAAJkceVWxqg135.png","initialPrice":29,"name":"柚C美式","productId":"4365","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img04.luckincoffeecdn.com/group3/M00/86/F8/CtxgEmYrSRGAF4JtAAKDRdnJaCE696.png","initialPrice":29,"name":"柠C美式","productId":"4454","stockSurplusAmount":"null"}]},{"productList":[{"defaultPicUrl":"https://img02.luckincoffeecdn.com/group3/M00/02/0B/CtxgEmdZLJuASE7lAAIjjJbHPGo854.png","initialPrice":29,"name":"大冻梨美式","productId":"4698","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img06.luckincoffeecdn.com/group1/M00/F0/55/CtwhA2dfpH2AQE58AAHGNIPdcF4843.png","initialPrice":32,"name":"枫丹红酒美式","productId":"4694","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img06.luckincoffeecdn.com/group1/M00/4D/E8/CtwhA2c9etyAESmCAAJptGJaYQo924.png","initialPrice":29,"name":"茉莉花香美式","productId":"4647","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img06.luckincoffeecdn.com/group3/M00/A5/12/CtxgFGcVI7SAEQ2qAAJv9FuuRZ4709.png","initialPrice":29,"name":"小黄油美式","productId":"4596","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img01.luckincoffeecdn.com/group3/M00/1E/5D/CtxgFGdfj9CAEdWeAAH-4uIQq0U495.png","initialPrice":26,"name":"生椰美式","productId":"4644","stockSurplusAmount":"null"}]},{"productList":[{"defaultPicUrl":"https://img06.luckincoffeecdn.com/group3/M00/52/99/CtxgEmadJZWAX4e2AALECwlCBwo365.png","initialPrice":32,"name":"葡萄冰萃美式","productId":"4408","stockSurplusAmount":"null"}]}]},{"kindDesc":"","kindName":"丝绒拿铁","twoProductList":[{"productList":[{"defaultPicUrl":"https://img06.luckincoffeecdn.com/group1/M00/75/A2/CtwhAmGTC7qAc2ddAAIcRCRcoYE360.png","initialPrice":29,"name":"丝绒拿铁","productId":"1800","stockSurplusAmount":0},{"defaultPicUrl":"https://img05.luckincoffeecdn.com/group2/M00/63/25/CtwiPGPyQP2AHvaTAAIU-J06nY0805.png","initialPrice":32,"name":"生椰丝绒拿铁","productId":"1884","stockSurplusAmount":0},{"defaultPicUrl":"https://img01.luckincoffeecdn.com/group1/M00/75/A3/CtwhAmGTC7qADjI1AAIpJBx_k7I039.png","initialPrice":32,"name":"香草丝绒拿铁","productId":"2143","stockSurplusAmount":0}]}]},{"kindDesc":"WBC（世界咖啡师大赛）冠军团队拼配\n瑞幸咖啡豆*连续7年获得IIAC金奖","kindName":"大师咖啡","twoProductList":[{"productList":[{"defaultPicUrl":"https://img05.luckincoffeecdn.com/group3/M00/5E/21/CtxgFGZ76i6AUN1MAAITQmZpPdU211.png","initialPrice":26,"name":"拿铁","productId":"117","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img06.luckincoffeecdn.com/group3/M00/5E/3A/CtxgFGZ77KqAO-AHAAH5MljksPM292.png","initialPrice":29,"name":"精萃澳瑞白","productId":"124","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img01.luckincoffeecdn.com/group3/M00/5E/48/CtxgFGZ77feAOrjeAAIvfBrDxSA376.png","initialPrice":26,"name":"燕麦拿铁","productId":"4500","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img05.luckincoffeecdn.com/group3/M00/5E/37/CtxgFGZ77FyAK1qfAAIJ_l_C5E4909.png","initialPrice":29,"name":"香草拿铁","productId":"127","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img04.luckincoffeecdn.com/group3/M00/5E/38/CtxgFGZ77HiAMBzxAAISoQKWKG0143.png","initialPrice":29,"name":"焦糖玛奇朵","productId":"125","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img05.luckincoffeecdn.com/group2/M00/B3/16/CtwiPWHnwW6AL4KjAAH1Y8uFSSc827.png","initialPrice":29,"name":"卡布奇诺","productId":"121","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img02.luckincoffeecdn.com/group3/M00/5E/3B/CtxgFGZ77MKAKKSOAAHlCfUYH_w371.png","initialPrice":29,"name":"摩卡","productId":"118","stockSurplusAmount":"null"}]}]},{"kindDesc":"中式茗茶搭配IIAC金奖豆","kindName":"中国茶咖","twoProductList":[{"productList":[{"defaultPicUrl":"https://img06.luckincoffeecdn.com/group3/M00/5E/45/CtxgFGZ77bKAFC4qAAKm6XDeNPE018.png","initialPrice":29,"name":"茉莉花香拿铁","productId":"4012","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img06.luckincoffeecdn.com/group1/M00/4D/E8/CtwhA2c9etyAESmCAAJptGJaYQo924.png","initialPrice":29,"name":"茉莉花香美式","productId":"4647","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img03.luckincoffeecdn.com/group3/M00/B8/1E/CtxgFGbdzeGAQ7fVAAKK_wU7qfI983.png","initialPrice":32,"name":"乌龙拿铁","productId":"4604","stockSurplusAmount":"null"}]}]},{"kindDesc":"采用OATLY咖啡大师燕麦奶，0乳糖轻负担","kindName":"燕麦奶专区","twoProductList":[{"productList":[{"defaultPicUrl":"https://img02.luckincoffeecdn.com/group2/M00/65/58/CtwiPWcno42AT_5HAAHVd5rcQqA776.png","initialPrice":35,"name":"太妃榛香燕麦拿铁","productId":"4661","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img01.luckincoffeecdn.com/group3/M00/5E/48/CtxgFGZ77feAOrjeAAIvfBrDxSA376.png","initialPrice":26,"name":"燕麦拿铁","productId":"4500","stockSurplusAmount":"null"}]},{"productList":[{"defaultPicUrl":"https://img06.luckincoffeecdn.com/group3/M00/5E/3A/CtxgFGZ77KqAO-AHAAH5MljksPM292.png","initialPrice":29,"name":"精萃澳瑞白","productId":"124","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img02.luckincoffeecdn.com/group3/M00/5E/3B/CtxgFGZ77MKAKKSOAAHlCfUYH_w371.png","initialPrice":29,"name":"摩卡","productId":"118","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img04.luckincoffeecdn.com/group3/M00/5E/38/CtxgFGZ77HiAMBzxAAISoQKWKG0143.png","initialPrice":29,"name":"焦糖玛奇朵","productId":"125","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img06.luckincoffeecdn.com/group3/M00/5E/45/CtxgFGZ77bKAFC4qAAKm6XDeNPE018.png","initialPrice":29,"name":"茉莉花香拿铁","productId":"4012","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img02.luckincoffeecdn.com/group3/M00/5E/3C/CtxgFGZ77NOAAONiAAG3-n0KdV8571.png","initialPrice":29,"name":"抹茶拿铁","productId":"1227","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img05.luckincoffeecdn.com/group3/M00/5E/21/CtxgFGZ76i6AUN1MAAITQmZpPdU211.png","initialPrice":26,"name":"拿铁","productId":"117","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img05.luckincoffeecdn.com/group3/M00/5E/37/CtxgFGZ77FyAK1qfAAIJ_l_C5E4909.png","initialPrice":29,"name":"香草拿铁","productId":"127","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img03.luckincoffeecdn.com/group1/M00/EF/E4/CtwhAmdfoOSATe5HAAIKPCX03ZE913.png","initialPrice":29,"name":"费尔岛拿铁","productId":"4645","stockSurplusAmount":"null"}]},{"productList":[{"defaultPicUrl":"https://img02.luckincoffeecdn.com/group2/M00/09/8F/CtwiPGcXIUmAaRlAAAIdbVBDqVM106.png","initialPrice":32,"name":"南瓜燕麦拿铁","productId":"4650","stockSurplusAmount":0}]}]},{"kindDesc":"真奶好茶，轻负担","kindName":"轻乳茶","twoProductList":[{"productList":[{"defaultPicUrl":"https://img02.luckincoffeecdn.com/group3/M00/1F/27/CtxgFGdfpNSAcZuyAAIQDOOVWSs886.png","initialPrice":32,"name":"枫丹锡兰轻乳茶（特大杯）","productId":"4643","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img05.luckincoffeecdn.com/group2/M00/1F/DA/CtwiPGdNGw6AaibRAAHIukvcnwU165.png","initialPrice":29,"name":"枫丹锡兰轻乳茶","productId":"4642","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img02.luckincoffeecdn.com/group3/M00/1D/B8/CtxgEmbUmyyAZQ3NAAIYsBljwaM588.png","initialPrice":29,"name":"轻轻茉莉（特大杯）","productId":"4506","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img05.luckincoffeecdn.com/group3/M00/1D/B8/CtxgEmbUmxaASNpWAAHQ1KzA06Y488.png","initialPrice":26,"name":"轻轻茉莉","productId":"4541","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img03.luckincoffeecdn.com/group1/M00/76/36/CtwhA2cVI0yAcXkDAAIX-fpCsKc649.png","initialPrice":29,"name":"生椰锡兰轻乳茶（特大杯）","productId":"4667","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img02.luckincoffeecdn.com/group1/M00/76/37/CtwhA2cVI2WAFWgUAAHPbwxC4fg751.png","initialPrice":26,"name":"生椰锡兰轻乳茶","productId":"4668","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img05.luckincoffeecdn.com/group3/M00/1D/B8/CtxgEmbUmgmAOc3-AAIPC3sFji0771.png","initialPrice":29,"name":"轻轻乌龙（特大杯）","productId":"4600","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img06.luckincoffeecdn.com/group3/M00/1D/B6/CtxgFGbUmfeAM_MXAAHIPlq9YHw441.png","initialPrice":26,"name":"轻轻乌龙","productId":"4601","stockSurplusAmount":"null"}]}]},{"kindDesc":"SOE单一产区精品咖啡豆\nSCA80+精品级认证，味觉升级","kindName":"SOE小黑杯","twoProductList":[{"productList":[{"defaultPicUrl":"https://img01.luckincoffeecdn.com/group3/M00/B0/69/CtxgEmbt1n6AYTllAAHUz5ypd4U031.png","initialPrice":29,"name":"瑰夏·美式","productId":"4615","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img05.luckincoffeecdn.com/group3/M00/B0/69/CtxgEmbt1gOAPtl1AAIC5xcv1c4774.png","initialPrice":32,"name":"瑰夏·Dirty","productId":"4618","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img01.luckincoffeecdn.com/group2/M00/5D/DD/CtwiPWMRxEqAWSBYAAGppnzo4l4661.png","initialPrice":32,"name":"瑰夏·拿铁","productId":"4616","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img02.luckincoffeecdn.com/group2/M00/5D/DD/CtwiPGMRxIyAWzPnAAGSfvB31P0343.png","initialPrice":35,"name":"瑰夏·澳瑞白","productId":"4617","stockSurplusAmount":"null"}]},{"productList":[{"defaultPicUrl":"https://img05.luckincoffeecdn.com/group1/M00/79/47/CtwhAmR8tIGAO3cLAAHFWuMuuxQ575.png","initialPrice":29,"name":"耶加雪菲·美式","productId":"1223","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img05.luckincoffeecdn.com/group1/M00/79/56/CtwhA2R8tMeAXNIlAAHk1BhrGhs886.png","initialPrice":32,"name":"耶加·Dirty","productId":"2822","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img03.luckincoffeecdn.com/group1/M00/79/47/CtwhAmR8tLaAKKYIAAG33wEoiB0615.png","initialPrice":32,"name":"耶加雪菲·拿铁","productId":"1222","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img05.luckincoffeecdn.com/group1/M00/79/56/CtwhA2R8tJ2AMWqQAAGxjxHEkr0857.png","initialPrice":35,"name":"耶加雪菲·澳瑞白","productId":"1256","stockSurplusAmount":"null"}]}]},{"kindDesc":"","kindName":"柠檬茶","twoProductList":[{"productList":[{"defaultPicUrl":"https://img03.luckincoffeecdn.com/group2/M00/65/32/CtwiPWcnhq2AaLymAAHuMNJXGqg488.png","initialPrice":29,"name":"轻咖柠檬茶（超大杯）","productId":"4448","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img06.luckincoffeecdn.com/group3/M00/0A/C8/CtxgEmcnh_OASGXmAAIMZhTL9WU070.png","initialPrice":32,"name":"葡萄柠檬茶（超大杯）","productId":"4565","stockSurplusAmount":"null"}]}]},{"kindDesc":"精选厚牛乳注入  醇厚新口感\n2020 EDGE Awards年度新消费产品","kindName":"厚乳拿铁","twoProductList":[{"productList":[{"defaultPicUrl":"https://img03.luckincoffeecdn.com/group1/M00/2F/22/CtwhA2Hnwx-AEHK-AAI9IDQSqvE194.png","initialPrice":29,"name":"厚乳拿铁","productId":"1108","stockSurplusAmount":"null"}]},{"productList":[{"defaultPicUrl":"https://img03.luckincoffeecdn.com/group3/M00/B0/67/CtxgFGbt1ruAR7FYAAJhDRKzLec820.png","initialPrice":29,"name":"深烘拿铁","productId":"4551","stockSurplusAmount":0}]}]},{"kindDesc":"","kindName":"爆款套餐","twoProductList":[{"productList":[{"defaultPicUrl":"https://img06.luckincoffeecdn.com/group3/M00/55/5A/CtxgEmc1nmSAZ4oOAAIgctsh8Xo324.png","initialPrice":52,"name":"双杯尝鲜【赠变脸笔】","productId":"PF1330","stockSurplusAmount":"null"}]},{"productList":[{"defaultPicUrl":"https://img04.luckincoffeecdn.com/group1/M00/D5/81/CtwhA2dZjNuAeWpiAAIyIyLEGKQ643.png","initialPrice":55,"name":"双杯·一起尝新品【无周边】","productId":"PF1420","stockSurplusAmount":"null"}]},{"productList":[{"defaultPicUrl":"https://img01.luckincoffeecdn.com/group3/M00/55/C4/CtxgFGc1qF6AK0pJAAIz_S0vQ2A677.png","initialPrice":55,"name":"双杯一起享【赠PU徽章】","productId":"PF1363","stockSurplusAmount":0},{"defaultPicUrl":"https://img03.luckincoffeecdn.com/group3/M00/04/5D/CtxgEmdZkY-AM80QAALmu6tvu8A506.png","initialPrice":58,"name":"双杯·下午茶放心整【赠周边】","productId":"PF1332","stockSurplusAmount":0},{"defaultPicUrl":"https://img06.luckincoffeecdn.com/group2/M00/5F/7D/CtwiPGdZjBOAArg0AAJLf97fIew478.png","initialPrice":55,"name":"双杯·新品咖咖炫【赠周边】","productId":"PF1418","stockSurplusAmount":0},{"defaultPicUrl":"https://img01.luckincoffeecdn.com/group3/M00/04/55/CtxgFGdZj1-AErIeAAJhh8u_r0c587.png","initialPrice":55,"name":"双杯·爆品库库喝【赠周边】","productId":"PF1422","stockSurplusAmount":0}]}]},{"kindDesc":"","kindName":"周边上新","twoProductList":[{"productList":[{"defaultPicUrl":"","initialPrice":0,"name":"","productId":"5452"},{"defaultPicUrl":"","initialPrice":0,"name":"","productId":"5453"},{"defaultPicUrl":"","initialPrice":0,"name":"","productId":"5454"},{"defaultPicUrl":"","initialPrice":0,"name":"","productId":"5455"}]},{"productList":[{"defaultPicUrl":"","initialPrice":0,"name":"","productId":"5335"}]}]},{"kindDesc":"","kindName":"瑞纳冰®","twoProductList":[{"productList":[{"defaultPicUrl":"https://img02.luckincoffeecdn.com/group2/M00/04/14/CtwiPGN_Jy-AJFxMAAHhy_aGStk220.png","initialPrice":32,"name":"抹茶瑞纳冰","productId":"311","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img05.luckincoffeecdn.com/group1/M00/7E/74/CtwhA2N_J1qAQhFZAAJS9vRcSNU059.png","initialPrice":32,"name":"巧克力瑞纳冰","productId":"119","stockSurplusAmount":"null"}]}]},{"kindDesc":"","kindName":"特色酒咖","twoProductList":[{"productList":[{"defaultPicUrl":"https://img05.luckincoffeecdn.com/group2/M00/80/00/CtwiPGVHv0KAVGGxAAJLvbAFMR4573.png","initialPrice":38,"name":"酱香拿铁","productId":"4160","stockSurplusAmount":0}]}]},{"kindDesc":"","kindName":"不喝咖啡","twoProductList":[{"productList":[{"defaultPicUrl":"https://img01.luckincoffeecdn.com/group2/M00/DD/D6/CtwiPGc-3XqAeDw7AAGdnPyqbnc614.png","initialPrice":23,"name":"橙C果茶","productId":"4731","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img06.luckincoffeecdn.com/group3/M00/82/95/CtxgFGc-3juAL-18AAGLM5YV0Io311.png","initialPrice":23,"name":"苹果C果茶","productId":"4732","stockSurplusAmount":"null"}]},{"productList":[{"defaultPicUrl":"https://img01.luckincoffeecdn.com/group1/M00/75/A2/CtwhAmGTC7mAZBwgAAFVEyQ-aGM681.png","initialPrice":19,"name":"纯牛奶","productId":"167","stockSurplusAmount":"null"}]},{"productList":[{"defaultPicUrl":"https://img03.luckincoffeecdn.com/group1/M00/FA/0B/CtwhAmOoafaANRjMAAG1rDGq1VM913.png","initialPrice":26,"name":"一杯黑巧","productId":"3959","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img05.luckincoffeecdn.com/group1/M00/7E/74/CtwhA2N_J1qAQhFZAAJS9vRcSNU059.png","initialPrice":32,"name":"巧克力瑞纳冰","productId":"119","stockSurplusAmount":"null"}]},{"productList":[{"defaultPicUrl":"https://img01.luckincoffeecdn.com/group1/M00/FF/03/CtwhA2OqvFWANACGAAGpbqlOucU355.png","initialPrice":32,"name":"抹茶好喝椰","productId":"1302","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img02.luckincoffeecdn.com/group2/M00/04/14/CtwiPGN_Jy-AJFxMAAHhy_aGStk220.png","initialPrice":32,"name":"抹茶瑞纳冰","productId":"311","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img02.luckincoffeecdn.com/group3/M00/5E/3C/CtxgFGZ77NOAAONiAAG3-n0KdV8571.png","initialPrice":29,"name":"抹茶拿铁","productId":"1227","stockSurplusAmount":"null"}]}]},{"kindDesc":"","kindName":"甜品小点","twoProductList":[{"productList":[{"defaultPicUrl":"https://img03.luckincoffeecdn.com/group2/M00/F9/C4/CtwiPGGSMreAMn6rAAJZMAjCpWI769.png","initialPrice":10,"name":"提拉米苏风味大福","productId":"1079","stockSurplusAmount":"null"}]},{"productList":[{"defaultPicUrl":"https://img01.luckincoffeecdn.com/group1/M00/55/E3/CtwhA2c_EnWAXS4UAAJq8WUpqBY870.png","initialPrice":15,"name":"双重莓莓车轮泡芙","productId":"4539","stockSurplusAmount":"null"}]},{"productList":[{"defaultPicUrl":"https://img03.luckincoffeecdn.com/group2/M00/F9/C4/CtwiPGGSMreAcosqAAI3z9J_tsI019.png","initialPrice":11,"name":"半熟芝士蛋糕","productId":"1143","stockSurplusAmount":"null"}]},{"productList":[{"defaultPicUrl":"https://img02.luckincoffeecdn.com/group1/M00/8C/23/CtwhAmGcwlaAGcadAALjzzuOD6Y598.png","initialPrice":5,"name":"巧克力味曲奇","productId":"1084","stockSurplusAmount":"null"}]},{"productList":[{"defaultPicUrl":"https://img05.luckincoffeecdn.com/group3/M00/36/8D/CtxgFGYKhXCAf0mTAAH2H59QlnY517.png","initialPrice":11,"name":"椰子大福","productId":"4362","stockSurplusAmount":0},{"defaultPicUrl":"https://img05.luckincoffeecdn.com/group1/M00/10/42/CtwhAmXAgReATpyPAAISMxei8t4445.png","initialPrice":11,"name":"粉樱荔荔大福","productId":"4244","stockSurplusAmount":0},{"defaultPicUrl":"https://img02.luckincoffeecdn.com/group2/M00/F9/C4/CtwiPGGSMreARrUmAALKPnQ4rIA182.png","initialPrice":5,"name":"燕麦提子曲奇","productId":"1255","stockSurplusAmount":0},{"defaultPicUrl":"https://img04.luckincoffeecdn.com/group3/M00/3D/ED/CtxgEmcHusqALhj8AAJIW3KXfwk129.png","initialPrice":15,"name":"栗子蒙布朗蛋糕","productId":"4533","stockSurplusAmount":0},{"defaultPicUrl":"https://img01.luckincoffeecdn.com/group2/M00/D9/BE/CtwiPGcOSWmAPRNxAAHAdTcNASA864.png","initialPrice":11,"name":"捣蛋南瓜大福","productId":"4523","stockSurplusAmount":0},{"defaultPicUrl":"https://img03.luckincoffeecdn.com/group2/M00/4B/AF/CtwiPGcjEfyAVvbnAAIUqixB2aY794.png","initialPrice":12,"name":"黑巧脆脆半熟芝士","productId":"4534","stockSurplusAmount":0},{"defaultPicUrl":"https://img04.luckincoffeecdn.com/group2/M00/61/13/CtwiPWdaQteAK94sAAIaGE-tmCs486.png","initialPrice":11,"name":"红苹果大福","productId":"4711","stockSurplusAmount":0},{"defaultPicUrl":"https://img04.luckincoffeecdn.com/group2/M00/FD/E8/CtwiPWdFl2qAP95JAAJvsvvH9Ok526.png","initialPrice":15,"name":"圣诞鹿卡龙-黑巧风味","productId":"4624","stockSurplusAmount":0},{"defaultPicUrl":"https://img03.luckincoffeecdn.com/group2/M00/DE/FD/CtwiPGc_EpKACKjpAAKAlVNxJe0781.png","initialPrice":15,"name":"焦糖榛果车轮泡芙","productId":"4536","stockSurplusAmount":0},{"defaultPicUrl":"https://img05.luckincoffeecdn.com/group1/M00/74/BD/CtwhA2dFlwCARgfrAAITdajGXgs906.png","initialPrice":15,"name":"圣诞鹿卡龙-伯爵红茶风味","productId":"4626","stockSurplusAmount":0},{"defaultPicUrl":"https://img06.luckincoffeecdn.com/group3/M00/4A/75/CtxgEmY99I2ALwdbAAIDAIv84do084.png","initialPrice":11,"name":"脆皮瓜瓜大福","productId":"4380","stockSurplusAmount":0}]}]},{"kindDesc":"元气唤醒，谷物给我力量","kindName":"烘焙轻食","twoProductList":[{"productList":[{"defaultPicUrl":"https://img01.luckincoffeecdn.com/group2/M00/F9/C5/CtwiPWGSMreAaIE_AAJQOtCBNnA984.png","initialPrice":12,"name":"海盐芝士吐司","productId":"784","stockSurplusAmount":0},{"defaultPicUrl":"https://img05.luckincoffeecdn.com/group1/M00/7D/22/CtwhAmUBanKAEJN5AAFxHeoiZ0k605.PNG","initialPrice":11,"name":"黄油葡萄干司康","productId":"4121","stockSurplusAmount":0}]}]},{"kindDesc":"","kindName":"经典饮品","twoProductList":[{"productList":[{"defaultPicUrl":"https://img03.luckincoffeecdn.com/group1/M00/FA/0B/CtwhAmOoafaANRjMAAG1rDGq1VM913.png","initialPrice":26,"name":"一杯黑巧","productId":"3959","stockSurplusAmount":"null"},{"defaultPicUrl":"https://img01.luckincoffeecdn.com/group1/M00/75/A2/CtwhAmGTC7mAZBwgAAFVEyQ-aGM681.png","initialPrice":19,"name":"纯牛奶","productId":"167","stockSurplusAmount":''}]}]}]},"error":''}
    response_text = json.loads(response.text)
    commodityList = response_text.get('data').get('commodityList')
    for commodity_info in commodityList:
        # print(commodity_info)
        twoProductList = commodity_info.get('twoProductList')
        for productList in twoProductList:
            for goods_info in productList.get('productList'):
                name = goods_info.get('name')
                name = name.replace('(', '（')
                name = name.replace(')', '）')
                productId = goods_info.get('productId')
                if productId in product_id_list and product_name in name:
                    print(name)
                    print(productId)
                    return productId


# skuCode = luck_down_order()
# print(skuCode)


def get_city():
    url = "https://kmapi.hqyi.net/LuckinCoffee/api/getCityList?search="
    payload = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Host': 'kmapi.hqyi.net',
        'Connection': 'keep-alive'
    }
    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)


def get_shop():
    url = "https://kmapi.hqyi.net/LuckinCoffee/api/getShopList?cityId=92&search=&longitude=113.241902&latitude=35.215726"

    payload = {}
    headers = {
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Accept': '*/*',
        'Host': 'kmapi.hqyi.net',
        'Connection': 'keep-alive'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)


# data = {
#     "code": "aDWSvnTrVWYmBpNx7H",
#     "deptId": 385361,
#     "price": 23,
#     "sku": {"温度": "热", "糖度": "不另外加糖", "茶风味": "锡兰红茶"},
#     "count": 1,
#     "product_name": "苹果C果茶"
# }
# sku = data.get('sku')
# count = data.get('count')
# code = data.get('code')
# deptId = data.get('deptId')
# product_name = data.get('product_name')
# price = data.get('price')
# remarks = data.get('remarks')
# result = luck_down_order(sku, count, code, deptId, product_name, price, remarks)
# print(result)



def get_token(code):
    url = f"https://luffi.cn:8443/api/third/validateKey/{code}"
    payload = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        'Accept': '*/*',
        'Host': 'luffi.cn:8443',
        'Connection': 'keep-alive'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.text)
    # {"code": 200, "msg": "成功", "data": {"price": "23", "type": 1, "token": "a1f3679e8a634cdb8d0ce43039280915"}}
    response_text = json.loads(response.text)
    return response_text.get('data').get('token')


def get_luffi_product_id(deptId, token, product_name):
    product_name = product_name.replace('(', '（')
    product_name = product_name.replace(')', '）')
    url = f"https://luffi.cn:8443/api/rx/goodsAppList?deptId={deptId}"
    payload = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        'token': token,
        'Accept': '*/*',
        'Host': 'luffi.cn:8443',
        'Connection': 'keep-alive'
    }
    response = requests.request("GET", url, headers=headers, data=payload)

    # print(json.loads(response.text))
    # response_text = {'busiCode': 'BASE000', 'code': 1, 'handler': 'CLIENT', 'msg': '成功', 'status': 'SUCCESS', 'uid': 'c7a3585c-f927-4bc0-95cc-b9e7efd7cabb1734918574073', 'version': '101', 'zeusId': 'luckycapiproxy-0ade0844-481921-2685693', 'content': {'commodityList': [{'kindDesc': '有事没事，来杯美式', 'kindId': '100300', 'kindName': '美式家族', 'topPlanId': '', 'twoProductList': [{'sortId': 0, 'twoKindName': '大师美式', 'twoKindId': '100301', 'twoKindNumber': 2, 'productList': [{'bigPicUrl': 'https://img02.luckincoffeecdn.com/group1/M00/35/EC/CtwhAmYE50eAflkVAAIIPlCqP2o101.jpg', 'categoryId': 22, 'categorySecondId': 55, 'categoryThirdId': 160, 'commodityCode': 'SP2277', 'commodityOriginPrice': 23.0, 'commoditySendOriginPrice': 26.0, 'defaultPicUrl': 'https://img02.luckincoffeecdn.com/group1/M00/2F/26/CtwhA2Hnw-GABuwhAAIZH9vQLIg476.png', 'discountPrice': 13.0, 'discountType': 0, 'eatway': 'both', 'enName': 'Americano', 'estimatePrice': 0.0, 'initialPrice': 23.0, 'inventoryType': 1, 'isHaveStorageStock': 0, 'maxAmount': 24, 'memberCardPrice': 0.0, 'messageOne': '', 'mode': 0, 'multiProcessType': 0, 'multiSku': 1, 'name': '标准美式', 'productId': '2500', 'productType': 0, 'quickOrderTag': 0, 'relationId': '', 'saleVolumn': 0, 'searchScore': 0, 'sendDiscountPrice': 14.0, 'sendInitialPrice': 26.0, 'shopPrice': 0.0, 'shopStockCount': -1, 'skuCode': 'SP2277-00107', 'skuName': 'IIAC金奖豆/热/不另外加糖/无奶', 'sortId': 0, 'source': 0, 'spuId': 2500, 'stockSurplusAmount': 0, 'supportSend': 1, 'unit': '杯'}]}]}, {'kindDesc': '', 'kindId': '100029', 'kindName': '不喝咖啡', 'topPlanId': '', 'twoProductList': [{'sortId': 0, 'twoKindName': '特调果茶', 'twoKindId': '100036', 'twoKindNumber': 2, 'productList': [{'bigPicUrl': 'https://img04.luckincoffeecdn.com/group3/M00/83/D0/CtxgFGc_F6aAeOITAAJaoLpW-PI968.jpg', 'categoryId': 22, 'categorySecondId': 73, 'categoryThirdId': 94, 'commodityCode': 'SP3151', 'commodityOriginPrice': 23.0, 'commoditySendOriginPrice': 26.0, 'defaultPicUrl': 'https://img01.luckincoffeecdn.com/group2/M00/DD/D6/CtwiPGc-3XqAeDw7AAGdnPyqbnc614.png', 'discountPrice': 13.0, 'discountType': 0, 'eatway': 'both', 'enName': 'Orange Tea', 'estimatePrice': 0.0, 'initialPrice': 23.0, 'inventoryType': 1, 'isHaveStorageStock': 0, 'maxAmount': 24, 'memberCardPrice': 0.0, 'messageOne': '', 'mode': 0, 'multiProcessType': 0, 'multiSku': 1, 'name': '橙C果茶', 'productId': '4731', 'productType': 0, 'quickOrderTag': 0, 'relationId': '', 'saleVolumn': 0, 'searchScore': 0, 'sendDiscountPrice': 14.0, 'sendInitialPrice': 26.0, 'shopPrice': 0.0, 'shopStockCount': -1, 'skuCode': 'SP3151-00022', 'skuName': '热/不另外加糖/锡兰红茶', 'sortId': 0, 'source': 0, 'spuId': 4731, 'stockSurplusAmount': 0, 'supportSend': 1, 'unit': '杯'}, {'bigPicUrl': 'https://img01.luckincoffeecdn.com/group3/M00/83/D0/CtxgFGc_F5CAL2cwAAJTeu2PFN0630.jpg', 'categoryId': 22, 'categorySecondId': 73, 'categoryThirdId': 94, 'commodityCode': 'SP3152', 'commodityOriginPrice': 23.0, 'commoditySendOriginPrice': 26.0, 'defaultPicUrl': 'https://img06.luckincoffeecdn.com/group3/M00/82/95/CtxgFGc-3juAL-18AAGLM5YV0Io311.png', 'discountPrice': 13.0, 'discountType': 0, 'eatway': 'both', 'enName': 'Apple Tea', 'estimatePrice': 0.0, 'initialPrice': 23.0, 'inventoryType': 1, 'isHaveStorageStock': 0, 'maxAmount': 24, 'memberCardPrice': 0.0, 'messageOne': '', 'mode': 0, 'multiProcessType': 0, 'multiSku': 1, 'name': '苹果C果茶', 'productId': '4732', 'productType': 0, 'quickOrderTag': 0, 'relationId': '', 'saleVolumn': 0, 'searchScore': 0, 'sendDiscountPrice': 14.0, 'sendInitialPrice': 26.0, 'shopPrice': 0.0, 'shopStockCount': -1, 'skuCode': 'SP3152-00022', 'skuName': '热/不另外加糖/锡兰红茶', 'sortId': 0, 'source': 0, 'spuId': 4732, 'stockSurplusAmount': 0, 'supportSend': 1, 'unit': '杯'}]}]}, {'kindDesc': '', 'kindId': '100011', 'kindName': '甜品小点', 'topPlanId': '', 'twoProductList': [{'sortId': 0, 'twoKindName': '瑞幸曲奇', 'twoKindId': '100013', 'twoKindNumber': 1, 'productList': [{'bigPicUrl': 'https://img06.luckincoffeecdn.com/group1/M00/F3/65/CtwhAmMZuqCAFthpAAO4w3VUhTM102.jpg', 'categoryId': 23, 'categorySecondId': 168, 'categoryThirdId': 0, 'commodityCode': 'SP1899', 'commodityOriginPrice': 5.0, 'commoditySendOriginPrice': 5.0, 'defaultPicUrl': 'https://img02.luckincoffeecdn.com/group1/M00/8C/23/CtwhAmGcwlaAGcadAALjzzuOD6Y598.png', 'discountPrice': 3.5, 'discountType': 0, 'eatway': 'both', 'enName': 'Chocolate Flavored Cookies', 'estimatePrice': 0.0, 'initialPrice': 5.0, 'inventoryType': 1, 'isHaveStorageStock': 0, 'maxAmount': 24, 'memberCardPrice': 0.0, 'messageOne': '', 'mode': 1, 'multiProcessType': 0, 'multiSku': 0, 'name': '巧克力味曲奇', 'productId': '1084', 'productType': 0, 'quickOrderTag': 0, 'relationId': '', 'saleVolumn': 0, 'searchScore': 0, 'sendDiscountPrice': 3.5, 'sendInitialPrice': 5.0, 'shopPrice': 0.0, 'shopStockCount': 59, 'skuCode': 'SP1899-00001', 'skuName': '', 'sortId': 0, 'source': 0, 'spuId': 1084, 'stockSurplusAmount': 0, 'supportSend': 1, 'unit': '袋'}]}, {'sortId': 0, 'twoKindName': '已售罄', 'twoKindId': '-1', 'twoKindNumber': 0, 'productList': [{'bigPicUrl': 'https://img03.luckincoffeecdn.com/group2/M00/03/7D/CtwiPWA_TfSARDirAAQMZetZSqg668.jpg', 'categoryId': 23, 'categorySecondId': 168, 'categoryThirdId': 0, 'commodityCode': 'SP2070', 'commodityOriginPrice': 5.0, 'commoditySendOriginPrice': 5.0, 'defaultPicUrl': 'https://img02.luckincoffeecdn.com/group2/M00/F9/C4/CtwiPGGSMreARrUmAALKPnQ4rIA182.png', 'discountPrice': 3.5, 'discountType': 0, 'eatway': 'both', 'enName': 'Oatmeal&Raisin Cookies', 'estimatePrice': 0.0, 'initialPrice': 5.0, 'inventoryType': 1, 'isHaveStorageStock': 0, 'maxAmount': 0, 'memberCardPrice': 0.0, 'messageOne': '', 'mode': 1, 'multiProcessType': 0, 'multiSku': 0, 'name': '燕麦提子曲奇', 'productId': '1255', 'productType': 0, 'quickOrderTag': 0, 'relationId': '', 'saleVolumn': 0, 'searchScore': 0, 'sendDiscountPrice': 3.5, 'sendInitialPrice': 5.0, 'shopPrice': 0.0, 'shopStockCount': 0, 'skuCode': 'SP2070-00001', 'skuName': '', 'sortId': 0, 'source': 0, 'spuId': 1255, 'stockSurplusAmount': 0, 'supportSend': 1, 'unit': '袋'}]}]}], 'shopInfo': {'isWork': 1, 'shopMode': 0, 'shopSwitchDesc': '', 'tipsToastStr': '', 'workDesc': '09:00-22:00'}}}
    response_text = json.loads(response.text)
    # print(response_text)
    commodityList = response_text.get('content').get('commodityList')
    for commodity_info in commodityList:
        # print(commodity_info)
        twoProductList = commodity_info.get('twoProductList')
        for productList in twoProductList:
            for goods_info in productList.get('productList'):
                name = goods_info.get('name')
                name = name.replace('(', '（')
                name = name.replace(')', '）')
                productId = goods_info.get('productId')
                if product_name in name:
                    print(name)
                    print(productId)
                    return productId


def luffi_down_order(code, deptId, product_name, sku, count, price, remarks):
    token = get_token(code)
    # order_sku_list = ['热', '不另外加糖', '锡兰红茶']
    if '杯' in sku:
        if 'oz' in sku:
            order_sku_list = sku.split(',')
        else:
            order_sku_list = [sk for sk in sku.split(',') if '杯' not in sk]
    else:
        order_sku_list = sku.split(',')
    time.sleep(1)
    productId = get_luffi_product_id(deptId, token, product_name)
    # productId = 4732
    url = f"https://luffi.cn:8443/api/rx/goods/detail?deptId=385361&productId={productId}"
    response = request_from(url, "GET")
    response_text = json.loads(response.text)
    # response_text = {'busiCode': 'BASE000', 'code': 1, 'content': {'abName': '', 'activityTagList': [], 'amount': 0, 'canCheck': 1, 'celebrityCommentList': [], 'checked': 0, 'coffeeBeanConsumerInfo': None, 'coffeeLabel': '', 'comboCode': '', 'comboId': 0, 'comboProductList': [], 'commodityCode': 'SP3152', 'currSeckillCount': 0, 'custom': 0, 'dealDiscount': 0, 'defaultPicUrl': 'https://img01.luckincoffeecdn.com/group3/M00/83/D0/CtxgFGc_F5CAL2cwAAJTeu2PFN0630.jpg', 'defaultSkuCode': '', 'desc': '', 'descriptionContent': '锡兰红茶风味固体饮料/茉莉花茶调味茶固体饮料/大红袍调味茶固体饮料，苹果复合果蔬汁饮料浓浆。\n\n图片及包装仅供参考，请以实物为准。\n尽快享用风味更佳哦~', 'descriptionTitle': '主要原料', 'detailDesc': '', 'discount': 0, 'discountPrice': 13, 'discountType': 0, 'eatway': 'both', 'enName': 'Apple Tea', 'estimatePriceContext': None, 'expireFootTips': None, 'extendsData': None, 'firstOrderFlag': 0, 'fixedNumber': 0, 'footTips': None, 'growLableName': '', 'htmlDesc': '<p><strong style="color: rgb(102, 102, 102); font-size: 12.5px;">【0脂0咖啡】</strong></p><p><strong style="color: rgb(102, 102, 102); font-size: 12.5px;">【含真实果汁，1杯喝到1.4颗苹果*】</strong></p><p><strong style="color: rgb(102, 102, 102); font-size: 12.5px;">【3款清爽茶底随心选择*，妙趣横生】</strong></p><p><span style="color: rgb(102, 102, 102); font-size: 12.5px;">推荐搭配「锡兰红茶」风味茶底，清甜苹果香气飘逸，四散进洋溢花果蜜香的茶汤里，碰撞出明快甜感，一杯便将整个暖冬轻拥入怀。另外，更有「清新淡雅的茉莉花香」、「岩韵兰香武夷大红袍」风味可供选择，搭配不同茶底，别有风味。</span></p><p><br></p><p><span style="color: rgb(102, 102, 102); font-size: 12.5px;">*本饮品添加苹果复合果蔬汁饮料浓浆。原料选用的苹果平均重约120g（出汁率约70%）。根据配方比例，以出汁率折算对比，本饮品在不另外加糖选项下，约有1.4颗苹果在里面。手工操作可能存在误差，仅供参考。</span></p><p><span style="color: rgb(102, 102, 102); font-size: 12.5px;">*茶风味可选类型请以各门店实际情况为准，下单前请注意查看并确认。</span></p>', 'initialPrice': 23, 'inventoryType': 1, 'isGift': 0, 'isHaveStorageStock': 0, 'isReachCondition': 1, 'isSoeSpu': 0, 'label': '', 'mallPayOffTitle': '确认订单', 'mallPayOffUrl': 'https://m.lkcoffee.com/pmall/order/confirm', 'matchTicketStatus': 0, 'maxAmount': 24, 'memberCardPrice': 0, 'memberTagList': [], 'mode': 0, 'multiSku': 1, 'name': '苹果C果茶', 'newMemberTag': '', 'oneCategoryId': 22, 'oneOrderMultipleitems': 0, 'payMoney': 0, 'pictureUrlList': ['https://img01.luckincoffeecdn.com/group3/M00/83/D0/CtxgFGc_F5CAL2cwAAJTeu2PFN0630.jpg'], 'popularityLabel': '', 'priceDesc': '1.面价：是指在菜单中标示为划横线的价格，是兑换商品所需商品券的券面价格、瑞幸总部优惠活动的计算基数及商品在部分门店展示或销售的价格，并非商品原价。\r\n2.未划线价：是指商品的当前价格，未划线价通常不能与咖啡钱包（商品券）及其他优惠活动同时享有，具体成交价格最终以订单结算页显示为准。\r\n3.预估到手、超值折扣等价格提示：是指根据您当前持有的咖啡钱包（电子商品券）/优惠券、可享优惠活动等进行的单件商品最低应付预估金额提示（首杯/新人等新用户权益提示：根据新人券包等进行的单件商品应付预估金额提示），不包含配送费、选配等费用。最终请以实付金额为准。\r\n4.咖啡钱包（商品券）：可兑换面额与面价等同的部分门店商品（配送费及另行选配的奶油、风味糖浆等费用需额外支付）。咖啡钱包（商品券）不兑现、不找零、超额需补差价，且1杯饮品限使用1张，详见使用规则。\r\n5.优惠活动：除另有说明外，优惠券及其他优惠活动通常以面价为计算基数，具体使用方式及活动详情，详见使用规则及优惠活动规则。\r\n6.自提及幸运送订单：\r\n瑞幸提供自提及幸运送两种独立的订单模式。\r\n自提订单：瑞幸部分门店的商品和价格略有不同。选择自提模式下单时，系统将为您推荐距离最近的门店，您也可以根据需要自行更改自提门店。商品实际价格以对应自提门店价格为准。下单前请仔细确认下单门店及商品价格。\r\n幸运送订单：幸运送实行专属菜单，选择幸运送模式下单时，商品种类、价格及优惠活动等方面，可能与自提订单存在差异。下单前请仔细确认订单模式及商品价格。\r\n7.商品具体成交价格以订单最终结算页面价格为准。瑞幸建议您在下单前仔细阅读本价格说明。如有疑问，请及时联系客服。瑞幸将根据实际情况，不时更新本价格说明。', 'priceDescLabel': '{{面价:}} 是指在菜单中标示为划横线的价格，是兑换商品所需商品券的券面价格、瑞幸总部优惠活动的计算基数及商品在部分门店展示或销售的价格，并非商品原价。\n\n{{预估到手、超值折扣等价格提示:}} 是指根据您当前持有的咖啡钱包（电子商品券）/优惠券、可享优惠活动等进行的单件商品最低应付预估金额提示（首杯/新人等新用户权益提示：根据新人券包等进行的单件商品应付预估金额提示），不包含配送费、选配等费用。最终请以实付金额为准。\n\n 具体价格说明请见详情页。 ', 'priceTag': None, 'processTypeList': [], 'productAttr4Customs': [], 'productDetailBuyTips': '全场饮品', 'productId': 4732, 'productInfoContext': {'cupDesc': '大杯', 'cupTitle': '杯型', 'showCupFlag': 1}, 'productPrice': None, 'productRecommend': '', 'productType': 1, 'promotionMsg': '', 'promptDesc': '', 'proposalId': 0, 'proposalName': '', 'purchaseTips': None, 'recommendPriceDesc': '', 'relationId': '', 'restTime': 0, 'saleAttrGroup': {'17': '温度', '18': '糖度', '100': '茶风味'}, 'saleAttrGroupObjectValues': {'17': [{'attrValueId': 57, 'attrValueName': '冰', 'checkIconUrl': '', 'unCheckIconUrl': ''}, {'attrValueId': 56, 'attrValueName': '热', 'checkIconUrl': '', 'unCheckIconUrl': ''}], '18': [{'attrValueId': 60, 'attrValueName': '标准甜', 'checkIconUrl': '', 'unCheckIconUrl': ''}, {'attrValueId': 112, 'attrValueName': '少甜', 'checkIconUrl': '', 'unCheckIconUrl': ''}, {'attrValueId': 59, 'attrValueName': '少少甜', 'checkIconUrl': '', 'unCheckIconUrl': ''}, {'attrValueId': 254, 'attrValueName': '微甜', 'checkIconUrl': '', 'unCheckIconUrl': ''}, {'attrValueId': 69, 'attrValueName': '不另外加糖', 'checkIconUrl': '', 'unCheckIconUrl': ''}], '100': [{'attrValueId': 661, 'attrValueName': '锡兰红茶', 'checkIconUrl': '', 'unCheckIconUrl': ''}, {'attrValueId': 615, 'attrValueName': '茉莉花香', 'checkIconUrl': '', 'unCheckIconUrl': ''}, {'attrValueId': 663, 'attrValueName': '大红袍乌龙茶', 'checkIconUrl': '', 'unCheckIconUrl': ''}]}, 'saleAttrGroupSeq': ['17', '18', '100'], 'saleAttrGroupValues': {'17': ['冰', '热'], '18': ['标准甜', '少甜', '少少甜', '微甜', '不另外加糖'], '100': ['锡兰红茶', '茉莉花香', '大红袍乌龙茶']}, 'saleAttrGroupValuesRecommendSeq': {'17': [], '18': [], '100': ['0']}, 'saleAttrGroupValuesRecommendSeqTag': {'17': [], '18': [], '100': [{'isRecommend': 1, 'seq': '0', 'tag': '推荐'}]}, 'seckillCount': 0, 'seckillInfo': None, 'seckillPic': '', 'seckillPrice': 0, 'sellingTags': {'middleBackgroundImage': '', 'qualityIcon': '', 'tags': ['真果汁', '0脂', '1杯≈1.4颗苹果']}, 'showAttrGroupValues': [], 'skuCode': 'SP3152-00022', 'skuList': [{'skuCode': 'SP3152-00018', 'skuSaleAttrSeq': {'17': ['0'], '18': ['1'], '100': ['1']}, 'skuSaleAttrValue': {'17': ['冰'], '18': ['少甜'], '100': ['茉莉花香']}}, {'skuCode': 'SP3152-00019', 'skuSaleAttrSeq': {'17': ['1'], '18': ['1'], '100': ['0']}, 'skuSaleAttrValue': {'17': ['热'], '18': ['少甜'], '100': ['锡兰红茶']}}, {'skuCode': 'SP3152-00016', 'skuSaleAttrSeq': {'17': ['0'], '18': ['0'], '100': ['1']}, 'skuSaleAttrValue': {'17': ['冰'], '18': ['标准甜'], '100': ['茉莉花香']}}, {'skuCode': 'SP3152-00038', 'skuSaleAttrSeq': {'17': ['1'], '18': ['3'], '100': ['0']}, 'skuSaleAttrValue': {'17': ['热'], '18': ['微甜'], '100': ['锡兰红茶']}}, {'skuCode': 'SP3152-00017', 'skuSaleAttrSeq': {'17': ['1'], '18': ['1'], '100': ['2']}, 'skuSaleAttrValue': {'17': ['热'], '18': ['少甜'], '100': ['大红袍乌龙茶']}}, {'skuCode': 'SP3152-00039', 'skuSaleAttrSeq': {'17': ['0'], '18': ['3'], '100': ['2']}, 'skuSaleAttrValue': {'17': ['冰'], '18': ['微甜'], '100': ['大红袍乌龙茶']}}, {'skuCode': 'SP3152-00040', 'skuSaleAttrSeq': {'17': ['1'], '18': ['3'], '100': ['2']}, 'skuSaleAttrValue': {'17': ['热'], '18': ['微甜'], '100': ['大红袍乌龙茶']}}, {'skuCode': 'SP3152-00025', 'skuSaleAttrSeq': {'17': ['1'], '18': ['1'], '100': ['1']}, 'skuSaleAttrValue': {'17': ['热'], '18': ['少甜'], '100': ['茉莉花香']}}, {'skuCode': 'SP3152-00026', 'skuSaleAttrSeq': {'17': ['1'], '18': ['4'], '100': ['2']}, 'skuSaleAttrValue': {'17': ['热'], '18': ['不另外加糖'], '100': ['大红袍乌龙茶']}}, {'skuCode': 'SP3152-00023', 'skuSaleAttrSeq': {'17': ['0'], '18': ['4'], '100': ['0']}, 'skuSaleAttrValue': {'17': ['冰'], '18': ['不另外加糖'], '100': ['锡兰红茶']}}, {'skuCode': 'SP3152-00024', 'skuSaleAttrSeq': {'17': ['0'], '18': ['1'], '100': ['0']}, 'skuSaleAttrValue': {'17': ['冰'], '18': ['少甜'], '100': ['锡兰红茶']}}, {'skuCode': 'SP3152-00021', 'skuSaleAttrSeq': {'17': ['0'], '18': ['2'], '100': ['1']}, 'skuSaleAttrValue': {'17': ['冰'], '18': ['少少甜'], '100': ['茉莉花香']}}, {'skuCode': 'SP3152-00022', 'skuSaleAttrSeq': {'17': ['1'], '18': ['4'], '100': ['0']}, 'skuSaleAttrValue': {'17': ['热'], '18': ['不另外加糖'], '100': ['锡兰红茶']}}, {'skuCode': 'SP3152-00020', 'skuSaleAttrSeq': {'17': ['1'], '18': ['2'], '100': ['1']}, 'skuSaleAttrValue': {'17': ['热'], '18': ['少少甜'], '100': ['茉莉花香']}}, {'skuCode': 'SP3152-00029', 'skuSaleAttrSeq': {'17': ['1'], '18': ['2'], '100': ['0']}, 'skuSaleAttrValue': {'17': ['热'], '18': ['少少甜'], '100': ['锡兰红茶']}}, {'skuCode': 'SP3152-00027', 'skuSaleAttrSeq': {'17': ['0'], '18': ['4'], '100': ['2']}, 'skuSaleAttrValue': {'17': ['冰'], '18': ['不另外加糖'], '100': ['大红袍乌龙茶']}}, {'skuCode': 'SP3152-00028', 'skuSaleAttrSeq': {'17': ['0'], '18': ['1'], '100': ['2']}, 'skuSaleAttrValue': {'17': ['冰'], '18': ['少甜'], '100': ['大红袍乌龙茶']}}, {'skuCode': 'SP3152-00014', 'skuSaleAttrSeq': {'17': ['1'], '18': ['4'], '100': ['1']}, 'skuSaleAttrValue': {'17': ['热'], '18': ['不另外加糖'], '100': ['茉莉花香']}}, {'skuCode': 'SP3152-00036', 'skuSaleAttrSeq': {'17': ['0'], '18': ['0'], '100': ['2']}, 'skuSaleAttrValue': {'17': ['冰'], '18': ['标准甜'], '100': ['大红袍乌龙茶']}}, {'skuCode': 'SP3152-00015', 'skuSaleAttrSeq': {'17': ['1'], '18': ['0'], '100': ['1']}, 'skuSaleAttrValue': {'17': ['热'], '18': ['标准甜'], '100': ['茉莉花香']}}, {'skuCode': 'SP3152-00037', 'skuSaleAttrSeq': {'17': ['0'], '18': ['3'], '100': ['0']}, 'skuSaleAttrValue': {'17': ['冰'], '18': ['微甜'], '100': ['锡兰红茶']}}, {'skuCode': 'SP3152-00012', 'skuSaleAttrSeq': {'17': ['0'], '18': ['3'], '100': ['1']}, 'skuSaleAttrValue': {'17': ['冰'], '18': ['微甜'], '100': ['茉莉花香']}}, {'skuCode': 'SP3152-00034', 'skuSaleAttrSeq': {'17': ['0'], '18': ['0'], '100': ['0']}, 'skuSaleAttrValue': {'17': ['冰'], '18': ['标准甜'], '100': ['锡兰红茶']}}, {'skuCode': 'SP3152-00013', 'skuSaleAttrSeq': {'17': ['1'], '18': ['3'], '100': ['1']}, 'skuSaleAttrValue': {'17': ['热'], '18': ['微甜'], '100': ['茉莉花香']}}, {'skuCode': 'SP3152-00035', 'skuSaleAttrSeq': {'17': ['1'], '18': ['0'], '100': ['2']}, 'skuSaleAttrValue': {'17': ['热'], '18': ['标准甜'], '100': ['大红袍乌龙茶']}}, {'skuCode': 'SP3152-00032', 'skuSaleAttrSeq': {'17': ['0'], '18': ['2'], '100': ['2']}, 'skuSaleAttrValue': {'17': ['冰'], '18': ['少少甜'], '100': ['大红袍乌龙茶']}}, {'skuCode': 'SP3152-00011', 'skuSaleAttrSeq': {'17': ['0'], '18': ['4'], '100': ['1']}, 'skuSaleAttrValue': {'17': ['冰'], '18': ['不另外加糖'], '100': ['茉莉花香']}}, {'skuCode': 'SP3152-00033', 'skuSaleAttrSeq': {'17': ['0'], '18': ['2'], '100': ['0']}, 'skuSaleAttrValue': {'17': ['冰'], '18': ['少少甜'], '100': ['锡兰红茶']}}, {'skuCode': 'SP3152-00030', 'skuSaleAttrSeq': {'17': ['1'], '18': ['0'], '100': ['0']}, 'skuSaleAttrValue': {'17': ['热'], '18': ['标准甜'], '100': ['锡兰红茶']}}, {'skuCode': 'SP3152-00031', 'skuSaleAttrSeq': {'17': ['1'], '18': ['2'], '100': ['2']}, 'skuSaleAttrValue': {'17': ['热'], '18': ['少少甜'], '100': ['大红袍乌龙茶']}}], 'soeImgUrl': '', 'sortId': 0, 'stockMsg': '', 'stockSurplusAmount': -1, 'storeyType': 0, 'supportSend': 1, 'tasteCollection': 0, 'tasteDate': None, 'tasteId': 0, 'tasteName': '', 'threeCategoryId': 94, 'totalDiscountPrice': 0, 'totalInitialPrice': 0, 'totalPriceDes': '苹果C果茶¥13+热¥0+不另外加糖¥0+锡兰红茶¥0', 'transmission': None, 'unCheckMsg': '', 'unit': '杯', 'upgradeCupRe': None, 'usableTimes': 0, 'videoUrl': '', 'warehouseProduct': 0}, 'handler': 'CLIENT', 'msg': '成功', 'status': 'SUCCESS', 'zeusId': 'luckycapiproxy-0add07bb-481922-388900', 'abTest': []}
    sku_list = response_text.get('content').get('skuList')
    # print(sku_list)
    for sku in sku_list:
        skuSaleAttrValue = sku.get('skuSaleAttrValue')
        print(sku.get('skuCode'))
        # print(skuSaleAttrValue)
        xxx = 0
        for sku_k, sku_v in skuSaleAttrValue.items():
            # print(sku_v)
            if sku_v[0] in order_sku_list:
                xxx += 1
        if xxx >= len(skuSaleAttrValue):

            url = "https://luffi.cn:8443/api/third/OrderCreate"
            payload = json.dumps({
                "deptId": deptId,
                "productList": [
                    {
                        "productId": productId,
                        "amount": count,
                        "skuCode": sku.get('skuCode'),
                        "productPrice": price,
                        "productName": product_name
                    }
                ],
                "remark": remarks
            })
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
                'token': token,
                'Content-Type': 'application/json',
                'Accept': '*/*',
                'Host': 'luffi.cn:8443',
                'Connection': 'keep-alive'
            }

            response = requests.request("POST", url, headers=headers, data=payload)

            print(response.text)
            data = json.loads(response.text).get('data')
            if data: # 有值时购买失败
                print('兑换失败')

            # takeMealCodeInfo = down_order(code, deptId, productDataList, remarks)
            for _ in range(300):
                try:
                    url = f'https://luffi.cn:8443/api/rx/order/self?key={code}'
                    request_from(url, "GET")
                    time.sleep(0.5)

                    result = request_from(url, "GET")
                    data = json.loads(result.text).get('data')
                    # print(data)
                    orderInfo = data.get('orderInfo')
                    if orderInfo:
                        takeMealCodeInfo = orderInfo.get('takeMealCodeInfo')
                        codeINfo = {'code': takeMealCodeInfo.get('code'), 'takeOrderId': takeMealCodeInfo.get('takeOrderId')}
                        return codeINfo
                except Exception as e:
                    print(e)


# data = {
#     "code": "u45JcPg2inN7wY8QcN",
#     "deptId": 390716,
#     "price": 23,
#     "sku": {"温度": "热", "糖度": "不另外加糖", "茶风味": "锡兰红茶"},
#     "count": 1,
#     "product_name": "苹果C果茶"
# }
# sku = data.get('sku')
# count = data.get('count')
# code = data.get('code')
# deptId = data.get('deptId')
# product_name = data.get('product_name')
# price = data.get('price')
# remarks = data.get('remarks')
#
# codeInfo = luffi_down_order(code, deptId, product_name, sku, count)
# print(codeInfo)


def get_order(pay_no):
    sql = f'SELECT order_id FROM fa_wanlshop_pay WHERE pay_no = {pay_no}'
    data = connect_mysql(sql, type=1)
    order_id = data[0][0]

    sql = f'SELECT fa_wanlshop_order.couponcode, fa_wanlshop_order.store_id, fa_wanlshop_order.city_id, fa_wanlshop_order.store_name, fa_wanlshop_order_goods.market_price, fa_wanlshop_order_goods.difference, fa_wanlshop_order_goods.title, fa_wanlshop_order_goods.number, fa_wanlshop_order_goods.goods_id FROM fa_wanlshop_order INNER JOIN fa_wanlshop_order_goods on fa_wanlshop_order.id = fa_wanlshop_order_goods.order_id WHERE fa_wanlshop_order.id = {order_id}'
    data = connect_mysql(sql, type=1)
    # data = (('https://luckin.hqyi.net/#/?code=aSjBR0kpdxAsm4Qs8s', 385361, '26.00', '热,不另外加糖,大杯 16oz,含轻咖', '轻轻茉莉', 1),)
    # data = (('https://luckin.hqyi.net/#/?code=JBk4BJBbBupeqpNTlf', 385361, '29.00', '冰,标准甜', '生椰拿铁', 1),)
    print(data)
    code_url = data[0][0]
    deptId = data[0][1]
    city_id = data[0][2]
    store_name = data[0][3]
    price = float(data[0][4])
    sku = data[0][5]
    product_name = data[0][6]
    count = data[0][7]
    goods_id = data[0][8]
    # todo
    remarks = ''
    sql = f'SELECT fa_wanlshop_brand.`name` FROM fa_wanlshop_goods JOIN fa_wanlshop_brand ON fa_wanlshop_goods.brand_id = fa_wanlshop_brand.id WHERE fa_wanlshop_goods.id = {goods_id}'
    data = connect_mysql(sql, type=1)
    print(data)
    brand = data[0][0]
    if brand == '瑞幸咖啡':
        if not code_url:
            code_url = kf_get_coupon_goods({'face_price': f'{int(price)}元'})
            sql = f'UPDATE fa_wanlshop_order SET couponcode = %s WHERE id = %s'
            val = [tuple([code_url, order_id])]
            connect_mysql(sql, val)
        result = ''

        if 'luckin.hqyi' in code_url:
            code = code_url.split('code=')[1]
            result = luck_down_order(sku, count, code, deptId, product_name, price, remarks, city_id, store_name)
        elif 'd.luffi' in code_url:
            code = code_url.split('key=')[1]
            result = luffi_down_order(code, deptId, product_name, sku, count, price, remarks)
        print(result)
        if result:
            sql = f'UPDATE fa_wanlshop_order SET couponcode = %s, changecode = %s, couponstate = %s, coupontime = %s, state = %s WHERE id = %s'
            val = [tuple([code_url, json.dumps(result), 2, int(time.time()), 6, order_id])]
            connect_mysql(sql, val)
            return result
        else:
            return result
    elif brand == '肯德基':
        pass
        # gbCityCode = 410800
        # keyword = '塔南餐厅'
        # # code_url = 'https://xd.foodyh.cn/?dp=1&order=20250108103332474'
        # code_url = 'https://xd.foodyh.cn/?dp=1&order=20250108180300942'
        # exchange_coupons(gbCityCode, keyword, code_url)
# get_order('202501091408400292046356499848')

# 快发平台买优惠券
def kf_get_coupon_goods(params):
    print(params)
    face_price = params.get('face_price')
    order_id = params.get('order_id')
    url = "https://test.haomachina.cn/api/Coupon/getGoods"
    payload = json.dumps({
        "page": 1,
        "goodsType": 1,
        "type": 2,
        "word": f'{face_price}元'
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
            if '瑞幸' in i.get('name') and str(face_price) in i.get('name'):
                print(i.get('id'))
                url = "https://guchi.haomachina.cn/api/Coupon/addOrder"
                payload = json.dumps({
                    "id": i.get('id'),
                    "count": 1,
                    "payType": 0
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




# kf_get_coupon_goods(29)













