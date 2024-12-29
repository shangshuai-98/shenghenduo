"""
商品上架
1. 通过数据id拿到用户输入内容
2.判断是哪个平台
3.获取链接的内容
4.通过对应平台淘宝客找商品
5.判断条件：第一优先：主图一致，sku一致
          第二优先：sku不一致，店铺一致
          第三优先：店铺不一致，找相似商品
6.省很多上架商品参数设置判断
"""

import json, hashlib, base64

import requests, pyperclip
import jieba
import jieba.analyse
from decimal import Decimal, ROUND_HALF_UP
from urllib.parse import unquote

import time, random, re
from script_tool.database import connect_mysql


def md5_encryption(data):
    md5 = hashlib.md5()  # 创建一个md5对象
    md5.update(data.encode('utf-8'))  # 使用utf-8编码数据
    return md5.hexdigest()  # 返回加密后的十六进制字符串


# 提取中心思想
def extract_central_idea(text, topK=5):
    # 为jieba设置停用词
    jieba.analyse.set_stop_words('script_tool/stopwords.txt')
    # 使用jieba提取关键词
    keywords = jieba.analyse.extract_tags(text, topK=topK)
    # 将关键词组合成句子作为中心思想
    central_idea = ''.join(keywords)
    return central_idea


# 判断平台，提取url
def link_platform(user_url):
    plat_dict = {'拼多多': 2, '抖音': 5, '快手': 4, '淘宝': 1, '京东': 3}
    plat = ''
    url = ''
    if 'yangkeduo.com' in user_url:
        print('拼多多平台')
        plat = plat_dict.get('拼多多')
    elif 'douyin.com' in user_url or '抖音' in user_url:
        print('抖音平台')
        plat = plat_dict.get("抖音")
    elif 'tb.cn' in user_url or '淘宝' in user_url:
        print('淘宝平台')
        plat = plat_dict.get('淘宝')
    elif 'jd.com' in user_url or '京东' in user_url:
        print('京东平台')
        plat = plat_dict.get('京东')

    pattern = re.compile(r'(https?)://.*.c[onm].*')
    res = pattern.search(user_url)
    if res:
        url = res.group()
    print(url)

    return plat, url


# 获取链接内容
def get_goods_info(bottom_money_id):
    sql = f'SELECT `name`, url, remark FROM fa_wanlshop_bottommoney WHERE id = {bottom_money_id}'
    data = connect_mysql(sql, type=1)
    # print(data)
    # data = [['取暖器', '6.97 y@T.LJ 07/23 fOk:/ 【抖音商城】https://v.douyin.com/CeiJAMAVf/ 钻石牌新款取暖器塔式暖风机全屋升温高热干衣立式取暖办公室两用长按复制此条消息，打开抖音搜索，查看商品详情！', '']]
    kw = ''
    user_url = data[0][1]
    remark = data[0][2]
    # if not k_name:
    #     print('商品无法识别')
    #     return ''
    plat, url = link_platform(user_url)  # 拿着url请求，获取用户提交的商品的信息
    if plat == 2:  # 拼多多
        print('拼多多')
    elif plat == 5:  # 抖音
        # print('抖音')
        # 尝试获取产品参数元素位置
        try:
            # url = 'https://v.douyin.com/iUqwFX7b/ 超有趣的数学启蒙机关书物理启蒙机关书立体书图形几何探索【DMZZ】'
            # url = 'https://v.douyin.com/iUQ1E11y/ 【小R妈推荐 双瓶特惠】Optrex爱滴氏 双效润眼喷雾 人10ml*2 H'
            # url = 'https://v.douyin.com/iU28LmJf/ 【答菲】羽绒服清洁湿巾免水洗衣物去渍应急清洁去污不留痕便携小包'
            k_name = url.split(' ')[1]
            k_name = extract_central_idea(k_name, 3)
            kw = {'k_name': k_name}
        except Exception as e:
            print('获取商品信息失败')

    elif plat == 4:  # 快手
        print('快手')
    elif plat == 1:  # 淘宝
        print('淘宝')
        # url = 'https://e.tb.cn/h.T6GaCyg3hddqwvO?tk=KAqI3AJld5E CZ0015 「法丽兹蛇年曲奇礼盒巧克力味饼干零食糕点大礼包年礼亲戚春节送礼」'
        # url = 'https://e.tb.cn/h.T6iJKmwmD59CN83?tk=3ALa3AJlZ2J CZ3456 「美的云朵M60cm超薄526零嵌入式冰箱家用法式双开四门双系统大容量」'
        k_name = url.split(' ')[-1]
        k_name = extract_central_idea(k_name, 3)
        kw = {'k_name': k_name}
    elif plat == 3:  # 京东
        print('京东')

    res = get_goods(plat, kw)

    # res = {'shopName': '钰彪汽车用品专营店', 'title': '汽车玻璃水强力去污去油膜玻璃清洁养护冬季强力去污除虫胶雨刮液', 'sku': [{'price': 1.1, 'info': '【体验装一瓶装】0度 复合升级款'}, {'price': 3.8, 'info': '【两桶装2600ML】复合升级款*2桶0度'}, {'price': 7.9, 'info': '【四桶装5200ML】清洁去污款*4桶 0℃以上地区可用'}, {'price': 8.5, 'info': '【四桶装5200ML】二代复合升级款*4桶 0℃以上地区可用'}, {'price': 11.6, 'info': '【四桶装5200ML】二代复合升级款*4桶 -15℃以上地地可用'}, {'price': 13.8, 'info': '【四桶装5200ML】二代复合升级款*4桶 -25℃以上地区可用'}, {'price': 15.8, 'info': '【四桶装5200ML】二代复合升级款*4桶 -40℃以上地区可用'}], 'bottom_price': 1.1, 'url': 'https://haohuo.jinritemai.co om/ecommerce/trade/detail/index.html?id=3688272076612960619&ins_activity_param=iAr2wpN4&origin_type=pc_buyin_group&pick_source=v.bw0nf', 'image': 'https://p3-item.ecombdimg.com/img/ecom-shop-material/UchAgOkX_m_c74b0a64d39542a7cdeb155217383284_sx_200442_www800-800~tplv-5mmsx3fupr-re_cp:410:410:q100.jpeg', 'commission': 8}
    if res:
        # 商品表新增数据
        # for i in res:
            # print(i)
        val_list = []
        sku_val = []
        title = res.get('title')
        image = res.get('image')
        shopName = res.get('shopName')
        commission = res.get('commission')  # 佣金率  20%
        bottom_price = res.get('bottom_price')  # 来源平台价格
        number = Decimal(bottom_price * (commission / 100))
        commission_ratio = number.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)  # 佣金
        commission_rate = get_dy_commission_rate(bottom_price, commission)  # 抖音佣金比例
        profit_ratio = commission_rate * 100  # 省很多利润率
        number = Decimal(bottom_price * commission_rate)
        profit = number.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)  # 省很多利润
        number = Decimal(float(commission_ratio - profit) / bottom_price)
        discount_ratio = number.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)  # 省很多优惠比例=优惠金额/来源平台售价
        url = res.get('url')

        factory_name = {"mall_name": shopName}
        val_list.append(tuple(["1", "1", title, image, int(time.time()), int(time.time()), json.dumps(factory_name), commission, bottom_price, url, plat, 'normal', '0', "1", float(commission_ratio), float(profit_ratio), float(profit), float(discount_ratio)]))
        sql = 'INSERT INTO fa_wanlshop_goods (shop_id, brand_id, title, image, createtime, updatetime, factory_name, commission, third_price, third_url, source_platform, status, state, freight_id, commission_ratio, profit_ratio, profit, discount_ratio) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        print(val_list)
        goods_id = connect_mysql(sql, val_list)
        print(goods_id)
        # goods_id = 859586

        spu_list = []
        sku = res.get('sku')
        for item in sku:
            price = item.get('price')
            info = item.get('info')
            spu_list.append(info)
            sku_val.append(tuple([goods_id, image, info, price, price, price, price, int(time.time()), int(time.time()), 10000]))

        sku_sql = 'INSERT INTO fa_wanlshop_goods_sku (goods_id, thumbnail, difference, price, market_price, dijia_price, sale_price, createtime, updatetime, stock) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        print(sku_val)
        connect_mysql(sku_sql, sku_val)

        spu_sql = 'INSERT INTO fa_wanlshop_goods_spu (goods_id, `name`, item, createtime, updatetime) VALUES (%s, %s, %s, %s, %s)'
        spu_val = []
        spu_val.append(tuple([goods_id, '规格', ','.join(spu_list), int(time.time()), int(time.time())]))
        connect_mysql(spu_sql, spu_val)

        bottommoney_sql = 'UPDATE fa_wanlshop_bottommoney SET status = 3, good_id = %s WHERE id = %s'
        bottommoney_val = [(goods_id, bottom_money_id)]
        connect_mysql(bottommoney_sql, bottommoney_val)
        print('商品识别成功')  # 上架商品
        return "True"
    else:
        bottommoney_sql = 'UPDATE fa_wanlshop_bottommoney SET status = 4 WHERE id = %s'
        bottommoney_val = [(bottom_money_id,)]
        connect_mysql(bottommoney_sql, bottommoney_val)
        print('商品无法识别')
        return "False"


def get_goods(plat, kw):
    if plat == 2:  # 拼多多
        print('拼多多')
    elif plat == 5:  # 抖音
        # print('抖音')
        goods_list = get_douyin_goods(kw)
        return goods_list
    elif plat == 4:  # 快手
        print('快手')
    elif plat == 1:  # 淘宝
        # print('淘宝')
        goods_list = get_taobao_goods(kw)
        return goods_list
    elif plat == 3:  # 京东
        print('京东')




def get_douyin_goods(kw):
    k_name = kw.get('k_name')
    res_list = []
    for page in range(1,6):
        data = f'by=&cm=&f0=&f1=&is_displayreward=0&is_guarantee=0&is_newyeartd=&jrsx=0&kw={k_name}&member_id=&page={page}&pf=&platform=&pp0=&pp1=&product_category_id=&product_category_three_id=&product_category_two_id=&product_tag_ids=&sign_type=md5&sort=&timestamp={int(time.time())}&type=&xsjl=0&xxbp=0&xxgy=0&secret=EC7259DFCAD1715C23D400B7A88407A3'
        sign = md5_encryption(data).upper()
        # print(sign)
        url = f"https://e.reduxingxuan.com/open/offical/product/index-search-v2?kw={k_name}&cm=&pp0=&pp1=&f0=&f1=&pf=&by=&xxbp=0&xxgy=0&jrsx=0&xsjl=0&sort=&platform=&type=&page={page}&member_id=&product_category_id=&product_category_two_id=&product_category_three_id=&is_guarantee=0&product_tag_ids=&is_displayreward=0&is_newyeartd=&timestamp={int(time.time())}&sign_type=md5&sign={sign}"
        print(url)

        payload = {}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Host': 'e.reduxingxuan.com',
            'Connection': 'keep-alive'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        # print(response.text)
        list_response = json.loads(response.text)
        # list_response = [{'shop': {'id': '34465', 'sell_num': '800+', 'name': '答菲官方旗舰店', 'logo': 'https://p3-ecom-qualification-sign.ecombdimg.com/tos-cn-i-6vegkygxbk/9f1453e293f14f33b84bdd5f180dafd6~tplv-6vegkygxbk-s:750.image?lk3s=c9156bde&x-expires=1761803488&x-signature=XydYYOm7WNiUjKPJgG3k%2BNp68w0%3D', 'creadit_logistics': '100', 'creadit_product': '79', 'creadit_service': '100'}, 'productImages': [{'product_id': '404944', 'url': 'https://p3-aio.ecombdimg.com/obj/ecom-shop-material/XkUxBBQb_m_a0ef7c35549d7167ad072cf2d305a4fa_sx_492457_www800-800'}], 'begin_time': 1733068800, 'end_time': 1746028800, 'id': '404944', 'shop_creadit_logistics': '100', 'shop_creadit_product': '79', 'shop_creadit_service': '100', 'status': '1', 'xingxuan_credit': 'B级', 'self_support': 0, 'product_category_id': '488', 'sell_num': '800+', 'is_newcomers': 0, 'sales_all': '3895030', 'sales24hour': '100000', 'sales_24': '379.5w+', 'memberSelectionCart': None, 'is_guarantee': '', 'platform': 'douyin', 'title': '【答菲】羽绒服清洁湿巾免水洗衣物去渍应急清洁去污不留痕便携小包', 'commission': '27', 'bottom_price': 9.9, 'url': 'https://haohuo.jinritemai.com/ecommerce/trade/detail/index.html?id=3642386234002822969&ins_activity_param=idV3dDub&origin_type=pc_buyin_group&pick_source=v.km7fi', 'platform_product_id': '3642386234002822969', 'specimen_count': '1000', 'reward_begin_time': '0', 'reward_end_time': '0', 'true_sales': '919', 'product_tag': ['投流奖励', '安心购'], 'is_displayreward': '0', 'parse_word': ['【答菲】羽绒服清洁湿巾免水洗衣物去渍应急清洁去污不留痕便携小包', '清洁湿巾', '清洁', '羽绒服', '答菲', '不留痕', '衣物', '包', '应急', '去污', '水洗', '免', '去渍', '便携'], 'is_newyeartd': '0', 'is_shop_reward_investment': 1, 'commission_value': 2.67, 'remaining': 81}]
        if list_response:
            for data in list_response:
                id = data.get('id')
                # print(id)
                details_md5 = f'id={id}&sign_type=md5&timestamp={int(time.time())}&secret=EC7259DFCAD1715C23D400B7A88407A3'
                details_sign = md5_encryption(details_md5).upper()
                details_url = f"https://e.reduxingxuan.com/open/offical/product/view?id={id}&timestamp={int(time.time())}&sign_type=md5&sign={details_sign}"
                print(details_url)
                details_response = requests.request("GET", details_url, headers=headers, data=payload)
                # print(response.text)
                details_response_text = json.loads(details_response.text)
                # details_response_text = {'id': '404944', 'shop_id': '34465', 'platform_product_id': '3642386234002822969', 'product_category_id': '488', 'partner_id': '171', 'platform': 'douyin', 'url': 'https://haohuo.jinritemai.com/ecommerce/trade/detail/index.html?id=3642386234002822969&ins_activity_param=idV3dDub&origin_type=pc_buyin_group&pick_source=v.km7fi', 'title': '【答菲】羽绒服清洁湿巾免水洗衣物去渍应急清洁去污不留痕便携小包', 'rebate_order_limit': '0', 'rebate_order_count': '0', 'rebate_time_limit': '0', 'bottom_price': 9.9, 'top_price': 17.9, 'discount_type': '1', 'coupon': '0.00', 'commission': 27, 'kol_cos_ratio': '5.000', 'specimen_count': '1000', 'sales': '0', 'true_sales': '923', 'need_fans_number': '8000', 'begin_time': '1733068800', 'end_time': '2025/05/01 00:00:00', 'gift_info': '', 'requirement': '月销3000单', 'copy_writer': '1、 180mmx150mm大尺寸，衣物清洁一张搞定\n2、便携小包装：旅行、就餐、日常出门方便携带\n3、中性pH配方，富含牛油果精华，清香不刺鼻，温和不伤手\n4、免水干洗，一次清洁，速干无痕迹\n5、3.3倍去污精华液，富含多种去污因子，轻松洁净各种污渍\n', 'post_place': '', 'post_time': '', 'no_post_area': '新疆,西藏,内蒙古', 'description': '<p><img src="https://p3-aio.ecombdimg.com/obj/ecom-shop-material/XkUxBBQb_m_d0c71cdd1c6dad4b890cdebd7d40367e_sx_306956_www790-550" style="max-width:100%;"/><img src="https://p3-aio.ecombdimg.com/obj/ecom-shop-material/XkUxBBQb_m_263d88772cf74b4e423aa3c7d4f31906_sx_444938_www790-1096" style="max-width:100%;"/><img src="https://p3-aio.ecombdimg.com/obj/ecom-shop-material/XkUxBBQb_m_e605c97068800a23b47da57750af297a_sx_221308_www790-698" style="max-width:100%;"/><img src="https://p3-aio.ecombdimg.com/obj/ecom-shop-material/XkUxBBQb_m_8a9a6f7236af152ffa21b1a22e7c0d11_sx_523421_www790-1635" style="max-width:100%;"/><img src="https://p3-aio.ecombdimg.com/obj/ecom-shop-material/XkUxBBQb_m_12ddee6877d1f27210516ec6d6dc7745_sx_963648_www790-1486" style="max-width:100%;"/><img src="https://p3-aio.ecombdimg.com/obj/ecom-shop-material/XkUxBBQb_m_a10fc6bdd80566c4c9ef2557e32abd6c_sx_269016_www790-905" style="max-width:100%;"/><img src="https://p3-aio.ecombdimg.com/obj/ecom-shop-material/XkUxBBQb_m_9d0ced1f2d320bafe3a4da7f1f48d19c_sx_430247_www790-1147" style="max-width:100%;"/><img src="https://p3-aio.ecombdimg.com/obj/ecom-shop-material/XkUxBBQb_m_3de588e720400a72322df99e0d7d08ff_sx_789107_www790-1469" style="max-width:100%;"/><img src="https://p3-aio.ecombdimg.com/obj/ecom-shop-material/XkUxBBQb_m_f4adc15b9d95d47666d077f95a864087_sx_523509_www790-1156" style="max-width:100%;"/><img src="https://p3-aio.ecombdimg.com/obj/ecom-shop-material/XkUxBBQb_m_eed46c796c857cddfdc48b522d14ff0f_sx_117139_www790-674" style="max-width:100%;"/><img src="https://p3-aio.ecombdimg.com/obj/ecom-shop-material/XkUxBBQb_m_22547deb1061c3890c5e329edb1d9d8f_sx_171215_www790-635" style="max-width:100%;"/><img src="https://p3-aio.ecombdimg.com/obj/ecom-shop-material/XkUxBBQb_m_2818d728af479f73ce590ebefa71aa66_sx_474260_www790-1523" style="max-width:100%;"/><img src="https://p3-aio.ecombdimg.com/obj/ecom-shop-material/XkUxBBQb_m_1cfb314ab9c5a9d456212619cbe594b4_sx_85189_www790-660" style="max-width:100%;"/></p>', 'status': '1', 'holidays_explain': '', 'other_fields': {'key': 'key', 'value': 'key'}, 'shop_name': '答菲官方旗舰店', 'shop_logo': 'https://p3-ecom-qualification-sign.ecombdimg.com/tos-cn-i-6vegkygxbk/9f1453e293f14f33b84bdd5f180dafd6~tplv-6vegkygxbk-s:750.image?lk3s=c9156bde&x-expires=1761803488&x-signature=XydYYOm7WNiUjKPJgG3k%2BNp68w0%3D', 'shop_sell_num': '800', 'shop_creadit_product': '98.00', 'shop_creadit_service': '100.00', 'shop_creadit_logistics': '98.00', 'partner_recommend_text': '【可试用一包，擦不干净退全款】', 'partner_recommend_images': [], 'partner_recommend_video': '', 'is_deposit': '0', 'is_sole': '0', 'is_prime_cost': '0', 'is_buy_rebate': '0', 'is_sf_send': '0', 'is_fx': '1', 'is_newcomers': '0', 'is_guarantee': '0', 'is_newyeartd': '0', 'ext_field': {'head_activity_id': '928328', 'ex_shop_id': '0', 'total_need_fans_number': '8000'}, 'is_displayreward': '0', 'reward_begin_time': None, 'reward_end_time': None, 'productImages': [{'product_id': '404944', 'url': 'https://p3-aio.ecombdimg.com/obj/ecom-shop-material/XkUxBBQb_m_a0ef7c35549d7167ad072cf2d305a4fa_sx_492457_www800-800', 'is_endorsement_video': '0'}, {'product_id': '404944', 'url': 'https://p3-aio.ecombdimg.com/obj/ecom-shop-material/XkUxBBQb_m_2231e17fa051972eb37a187f2d8f9173_sx_428014_www800-800', 'is_endorsement_video': '0'}, {'product_id': '404944', 'url': 'https://p3-aio.ecombdimg.com/obj/ecom-shop-material/XkUxBBQb_m_f884730d1fcc0ec75378e88e69bf4c4a_sx_352699_www800-800', 'is_endorsement_video': '0'}, {'product_id': '404944', 'url': 'https://p3-aio.ecombdimg.com/obj/ecom-shop-material/XkUxBBQb_m_d1493f354d28ec76101ea71a95358b38_sx_371970_www800-800', 'is_endorsement_video': '0'}, {'product_id': '404944', 'url': 'https://p3-aio.ecombdimg.com/obj/ecom-shop-material/XkUxBBQb_m_939648c26aa3e1d6e100018d4b70bb67_sx_428724_www800-800', 'is_endorsement_video': '0'}], 'shop': {'id': '34465', 'sell_num': '800', 'name': '答菲官方旗舰店', 'creadit_product': 98, 'creadit_service': 100, 'creadit_logistics': 98, 'shop_score': '99.00', 'logo': 'https://p3-ecom-qualification-sign.ecombdimg.com/tos-cn-i-6vegkygxbk/9f1453e293f14f33b84bdd5f180dafd6~tplv-6vegkygxbk-s:750.image?lk3s=c9156bde&x-expires=1761803488&x-signature=XydYYOm7WNiUjKPJgG3k%2BNp68w0%3D', 'performance': {'id': '1025615', 'shop_id': '34465', 'daily_delivery_capacity': '10000', 'daily_production_capacity': '10000', 'Three_minute_response': '95', 'video_url': '', 'created_at': '1733278365', 'updated_at': None}, 'endorsement': {'id': '764782', 'shop_id': '34465', 'logo': 'https://p3-ecom-qualification-sign.ecombdimg.com/tos-cn-i-6vegkygxbk/9f1453e293f14f33b84bdd5f180dafd6~tplv-6vegkygxbk-s:750.image?lk3s=c9156bde&x-expires=1761803488&x-signature=XydYYOm7WNiUjKPJgG3k%2BNp68w0%3D', 'video_url_ed': '', 'video_img_ed': None, 'newvideo_url_ed': None, 'created_at': '1733278365', 'updated_at': None, 'is_delete': '0'}}, 'productSpecs': [{'product_id': '404944', 'name': '【单片便携装】1片*24片/提', 'price': '0.00', 'current_price': '9.90', 'id': '12177630', 'skuid': '3422746026341634', 'is_delivery': '1'}, {'product_id': '404944', 'name': '【超值装】10抽*8包（加大加厚）', 'price': '0.00', 'current_price': '14.90', 'id': '12177631', 'skuid': '3379636487004930', 'is_delivery': '1'}, {'product_id': '404944', 'name': '【实惠装】10抽*5包（加大加厚）', 'price': '0.00', 'current_price': '9.90', 'id': '12177632', 'skuid': '3384790728137218', 'is_delivery': '1'}, {'product_id': '404944', 'name': '10抽*6包（加大加厚）', 'price': '0.00', 'current_price': '11.90', 'id': '12177633', 'skuid': '3426560251192322', 'is_delivery': '1'}, {'product_id': '404944', 'name': '【巨划算】10抽*10包（加大加厚）', 'price': '0.00', 'current_price': '17.90', 'id': '12177634', 'skuid': '3430327731027458', 'is_delivery': '1'}], 'partner': {'id': '171', 'name': '钟毅强', 'workwx_qrcode': 'https://static1.redu.com/uploads/images/2021/1020/20211020115729_65803.jpg', 'code': '1', 'flower_name': '子期'}, 'productExpressRelations': [{'product_id': '404944', 'express_id': '10', 'express': {'id': '10', 'name': '极兔速递', 'ename': 'JITU', 'status': '1', 'sort_order': '0', 'created_at': '1599743614', 'updated_at': '1599743614'}}, {'product_id': '404944', 'express_id': '16', 'express': {'id': '16', 'name': '中通', 'ename': 'ZTO', 'status': '1', 'sort_order': '0', 'created_at': '1599743614', 'updated_at': '1599743614'}}, {'product_id': '404944', 'express_id': '17', 'express': {'id': '17', 'name': '圆通', 'ename': 'YTO', 'status': '1', 'sort_order': '0', 'created_at': '1599743614', 'updated_at': '1599743614'}}, {'product_id': '404944', 'express_id': '27', 'express': {'id': '27', 'name': '邮政快递包裹', 'ename': 'CHINAPOST', 'status': '1', 'sort_order': '0', 'created_at': '1636036689', 'updated_at': '1636036689'}}], 'productSellwayRelations': [{'product_id': '404944', 'product_sellway_id': '1', 'productSellway': {'id': '1', 'name': '短视频', 'status': '1', 'sort_order': '0', 'created_at': '1606987860', 'updated_at': '1606987860'}}], 'productExtFields': [{'id': '70824472', 'product_id': '404944', 'name': 'logistics_info', 'value': '48小时内从江苏省发货，运费0元起'}], 'logistics_info': '48小时内从江苏省发货，运费0元起', 'commission_value': 2.67, 'hosting': 0, 'kol_commission': 5, 'kol_commission_value': '0.49', 'remaining': 77, 'support_sellways': '短视频', 'support_express': '极兔速递, 中通, 圆通, 邮政快递包裹', 'partner_name': '钟毅强', 'workwx': 'https://static1.redu.com/uploads/images/2021/1020/20211020115729_65803.jpg', 'wx_code': '1', 'p_status': 'ing', 'comment': [], 'percent': [], 'scheduled_date': [1, 2, 3, 4, 5], 'spec_count': [1, 2, 3], 'spec_count_new': 1, 'product_labels': [], 'product_tags': [{'name': '投流奖励'}, {'id': 25, 'name': '安心购', 'sort_order': '4'}, {'id': 27, 'name': '随心推资质', 'sort_order': '2'}, {'id': 65, 'name': '超值购', 'sort_order': 0}], 'back_cash_orders': '3', 'back_cash_days': '30', 'can_get_free_sample': 1, 'talent_average_sales': 0.03, 'rule_type': '1', 'is_product_investment': 1}
                # print(details_response_text)
                productSpecs = details_response_text.get('productSpecs')
                commission = details_response_text.get('commission')  # 佣金率
                shopName = details_response_text.get('shop_name')  # 店铺名称
                title = details_response_text.get('title')  # 标题
                url = details_response_text.get('url')  # url
                productImages = details_response_text.get('productImages')[0].get('url')  # 图片
                bottom_price = details_response_text.get('bottom_price')  # 最低价
                sku = []
                for sku_info in productSpecs:
                    print(sku_info)
                    sku.append({
                        "price": sku_info.get('current_price'),
                        "info": sku_info.get('name'),
                    })
                res = {
                    'shopName': shopName,
                    'title': title,
                    'sku': sku,
                    'bottom_price': bottom_price,
                    'url': url,
                    'image': productImages,
                    'commission': commission,
                }
                res_list.append(res)
        else:
            break
    if res_list:
        res_list = sorted(res_list, key=lambda x: x['bottom_price'])
        print(res_list)
        return res_list[0]

    else:
        print('商品匹配失败')
        return False


def get_dy_commission_rate(price, commission):
    if price <= 50:
        if commission <= 15:
            return 0.01
        elif commission > 15 and commission <= 20:
            return 0.02
        elif commission > 20 and commission <= 25:
            return 0.03
        elif commission > 25 and commission <= 30:
            return 0.04
        elif commission > 30 and commission <= 35:
            return 0.05
        elif commission > 35 and commission <= 40:
            return 0.06
        elif commission > 40 and commission <= 45:
            return 0.07
        elif commission > 45 and commission <= 50:
            return 0.08
        elif commission > 50:
            return 0.09
    elif price >50:
        if commission <= 15:
            return 0.02
        elif commission > 15 and commission <= 20:
            return 0.03
        elif commission > 20 and commission <= 25:
            return 0.04
        elif commission > 25 and commission <= 30:
            return 0.05
        elif commission > 30 and commission <= 35:
            return 0.06
        elif commission > 35 and commission <= 40:
            return 0.07
        elif commission > 40 and commission <= 45:
            return 0.08
        elif commission > 45:
            return 0.09

# '20000M大容量快充充电宝自带四线迷你便携10000M手机通用毫安'
# get_douyin_goods({'k_name': '充电宝'})

def get_taobao_goods(kw):
    k_name = kw.get('k_name')
    res_list = []
    for page in range(1, 2):
        url = f"https://dtkapi.ffquan.cn/go_getway/proxy/search-v2?platform=1&page={page}&px=zh&version=2&kw={k_name}&api_v=1&flow_identifier=normal"

        payload = {}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Host': 'dtkapi.ffquan.cn',
            'Connection': 'keep-alive',
        }

        # response = requests.request("GET", url, headers=headers, data=payload)
        # print(json.loads(response.text))
        response_text = {'cache': False, 'code': 1, 'data': {'category_range_price': None, 'search': {'bi_k': 'retry', 'bi_v': '1', 'category_name': '', 'goodsid': '', 'list': [{'activity_end_time': '2025-01-31 23:59:59', 'activity_price_tag': '', 'activity_start_time': '2024-12-01 00:00:01', 'activity_type': '3', 'add_time': '2024-12-26 17:54:01', 'avgday7_plus_today': '0.00', 'brand_id': '119069', 'brand_name': '趣多多', 'bybt_fee': '0.00', 'cate_lowest_price': '', 'category_name': '曲奇饼干', 'cid': '6', 'comment': '0', 'commission_rate': '8.50', 'commission_type': '3', 'coupon_amount': '5.00', 'coupon_condition': '5.01', 'coupon_end_time': '2025-01-03 23:59:59', 'coupon_end_time_stamp': 1735919999, 'coupon_id': 'abe3e1ae924a4f17bccf9f8ccf72080e', 'coupon_link': 'https://uland.taobao.com/quan/detail?sellerId=144185701108507162&activityId=abe3e1ae924a4f17bccf9f8ccf72080e', 'coupon_num': '99999', 'coupon_over': '1', 'coupon_start_time': '2024-12-27 00:00:00', 'cut': '0', 'cut_price': '0.00', 'd_title': '趣多多豆豆曲奇缤纷口味新年礼盒24包*384g', 'daily_tk_total': '2', 'deposit': '', 'direct_commission': '0.00', 'direct_commission_type': '1', 'discount_cut': '0', 'discount_full': '0', 'divisor': '1', 'flagship_store': '0', 'freeship_remote_district': '0', 'fresh': '1', 'goods_sign': 'jjjejQMU0tJZJdvjjnHBeJhJte-bXG76geHGP7jVrvMiZb', 'goods_unit': '', 'goodsid': 'jjjejQMU0tJZJdvjjnHBeJhJte-bXG76geHGP7jVrvMiZb', 'gray_type': [], 'has_coupon': '1', 'hot_push': '2', 'id': '44592050', 'is_88vip': '1', 'is_brand_business': '0', 'is_buydance_goods': '0', 'is_buydance_top': '0', 'is_chaoshi': '1', 'is_choice': '1', 'is_delete': '0', 'is_editor_recommend': '0', 'is_flagship': '1', 'is_goldseller': '0', 'is_gray': '0', 'is_haitao': '0', 'is_high_com': '0', 'is_online': '1', 'is_online_brand': '0', 'is_pure_push': '0', 'is_recommend_goods': 0, 'is_red_shop': '0', 'is_sample': '0', 'is_subdivision': '0', 'is_tmall': '1', 'is_top': 0, 'kol_num': '0', 'lowest': '0', 'lowest_day': '0', 'main_pic': 'https://img.alicdn.com/i1/6000000002991/O1CN01emMLqy1XxvemAXGPH_!!6000000002991-0-at.jpg', 'mao_chao_return': '0.00', 'market_group': [], 'market_img': [], 'max_sales_time': '', 'min_unit_price_by_cate': '0', 'nearly_min_price': '', 'official_fee': '0.00', 'original_price': '44.90', 'price': '39.90', 'promotion_group_num': '0', 'pure_push_switch': '0', 'rank_num': '0', 'red_packet': '0', 'reward': '0.00', 'sales': '3', 'sales_2h': '0', 'sales_daily': '1', 'search_goods_rate': 0, 'seckill_fee': '0.00', 'selection_users_recommend_num': '0', 'seller_id': '144185701108507162', 'sentiment': '0.43', 'server_tag': ['假一赔十', '7天无理由退换', '春节', '破损包退', '极速退款', '30天放心退', '上门取退', '实惠货盘'], 'service_percent': '0.00', 'service_score': '4.88', 'ship_score': '4.88', 'shop_level': '20', 'shop_name': '天猫超市', 'similar_goods': 0, 'special': '', 'special_content': '', 'special_text': [], 'start_time': '2024-12-27 00:00:00', 'start_time_stamp': 1735228800, 'sub_title': '趣多多豆豆曲奇缤纷口味新年礼盒24包*384g', 'subdivision_id': '0', 'subdivision_name': '', 'subdivision_rank': '0', 'subsidy_rate': '0.00', 'tag_id': [16], 'taobao_cate_id': '17835', 'team_name': '冰橙-珠穆朗玛', 'title': '趣多多豆豆软曲奇缤纷口味新年礼盒384g整箱24包饼干零食新年礼物', 'tk_zs_id': '48224298', 'top_days': '0', 'topn_quantity': '0', 'topn_rate': '', 'topn_total_count': '0', 'trans_device_day8': '0', 'unique_activity': '', 'unit_price': '0', 'users_recommend_num': '0', 'yunfeixian': '0', 'zs_uid': '1235027'}, {'activity_end_time': '2025-01-31 23:59:59', 'activity_price_tag': '', 'activity_start_time': '2024-12-01 00:00:01', 'activity_type': '3', 'add_time': '2024-12-24 11:53:01', 'avgday7_plus_today': '1.00', 'brand_id': '139041082', 'brand_name': '皇冠', 'bybt_fee': '0.00', 'cate_lowest_price': '比同类曲奇饼干低6.02元', 'category_name': '曲奇饼干', 'cid': '6', 'comment': '0', 'commission_rate': '4.25', 'commission_type': '3', 'coupon_amount': '0.00', 'coupon_condition': '', 'coupon_end_time': '2024-12-31 23:59:59', 'coupon_end_time_stamp': 1735660799, 'coupon_id': '', 'coupon_link': '', 'coupon_num': '1', 'coupon_over': '0', 'coupon_start_time': '2024-12-24 11:52:49', 'cut': '0', 'cut_price': '0.00', 'd_title': '【皇冠丹麦】曲奇饼干681g*1年货礼盒装', 'daily_tk_total': '0', 'deposit': '', 'direct_commission': '0.00', 'direct_commission_type': '1', 'discount_cut': '0', 'discount_full': '0', 'divisor': '1', 'flagship_store': '0', 'freeship_remote_district': '0', 'fresh': '1', 'goods_sign': 'JkQZJaiRtqAyNgVG0IXKZcvta-eQGMq6ACGVVZPm0xH93', 'goods_unit': '', 'goodsid': 'JkQZJaiRtqAyNgVG0IXKZcvta-eQGMq6ACGVVZPm0xH93', 'gray_type': [], 'has_coupon': '0', 'hot_push': '0', 'id': '44580410', 'is_88vip': '1', 'is_brand_business': '0', 'is_buydance_goods': '0', 'is_buydance_top': '0', 'is_chaoshi': '1', 'is_choice': '1', 'is_delete': '0', 'is_editor_recommend': '0', 'is_flagship': '1', 'is_goldseller': '0', 'is_gray': '0', 'is_haitao': '0', 'is_high_com': '0', 'is_online': '1', 'is_online_brand': '1', 'is_pure_push': '0', 'is_recommend_goods': 0, 'is_red_shop': '0', 'is_sample': '0', 'is_subdivision': '0', 'is_tmall': '1', 'is_top': 0, 'kol_num': '1', 'lowest': '0', 'lowest_day': '0', 'main_pic': 'https://img.alicdn.com/i4/6000000005528/O1CN01QBqlJC1qhsKd1sYua_!!6000000005528-0-at.jpg', 'mao_chao_return': '0.00', 'market_group': [], 'market_img': [], 'max_sales_time': '', 'min_unit_price_by_cate': '0', 'nearly_min_price': '', 'official_fee': '0.00', 'original_price': '64.30', 'price': '64.30', 'promotion_group_num': '0', 'pure_push_switch': '0', 'rank_num': '0', 'red_packet': '0', 'reward': '0.00', 'sales': '15', 'sales_2h': '0', 'sales_daily': '0', 'search_goods_rate': 0, 'seckill_fee': '0.00', 'selection_users_recommend_num': '0', 'seller_id': '144185701108507162', 'sentiment': '-57.63', 'server_tag': ['极速退款', '30天放心退', '上门取退', '假一赔十', '7天无理由退换', '实惠货盘', '破损包退', '春节'], 'service_percent': '0.00', 'service_score': '4.88', 'ship_score': '4.88', 'shop_level': '20', 'shop_name': '天猫超市', 'similar_goods': 0, 'special': '', 'special_content': '', 'special_text': [], 'start_time': '2024-12-24 11:53:02', 'start_time_stamp': 1735012382, 'sub_title': '【皇冠丹麦】曲奇饼干681g*1年货礼盒装', 'subdivision_id': '0', 'subdivision_name': '', 'subdivision_rank': '0', 'subsidy_rate': '0.00', 'tag_id': [16], 'taobao_cate_id': '17835', 'team_name': '打工人好物采集', 'title': 'danisa皇冠丹麦进口曲奇饼干681g*1盒零食送礼盒新年礼物年货礼包', 'tk_zs_id': '48212484', 'top_days': '0', 'topn_quantity': '0', 'topn_rate': '', 'topn_total_count': '0', 'trans_device_day8': '2', 'unique_activity': '', 'unit_price': '0', 'users_recommend_num': '0', 'yunfeixian': '0', 'zs_uid': '413299'}, {'activity_end_time': '', 'activity_price_tag': '比双12低9元', 'activity_start_time': '', 'activity_type': '1', 'add_time': '2024-12-26 16:22:01', 'avgday7_plus_today': '0.00', 'brand_id': '16739791067', 'brand_name': '榛好季', 'bybt_fee': '0.00', 'cate_lowest_price': '', 'category_name': '坚果礼盒', 'cid': '6', 'comment': '0', 'commission_rate': '20.01', 'commission_type': '3', 'coupon_amount': '6.00', 'coupon_condition': '29', 'coupon_end_time': '2024-12-29 23:59:59', 'coupon_end_time_stamp': 1735487999, 'coupon_id': '2b4654fda93a44eabab911d6aa0bbe51', 'coupon_link': 'https://uland.taobao.com/quan/detail?sellerId=4801013124909192891&activityId=2b4654fda93a44eabab911d6aa0bbe51', 'coupon_num': '99998', 'coupon_over': '2', 'coupon_start_time': '2024-12-27 00:00:00', 'cut': '0', 'cut_price': '1.00', 'd_title': '榛好季礼盒曲奇华夫饼干500gx2盒', 'daily_tk_total': '1', 'deposit': '', 'direct_commission': '0.00', 'direct_commission_type': '1', 'discount_cut': '0', 'discount_full': '0', 'divisor': '1', 'flagship_store': '0', 'freeship_remote_district': '1', 'fresh': '0', 'goods_sign': '5kdr0Y0CxtyjyWmo5mu7dYCMtV-GKGOWR8cqPmXWDkZhZp', 'goods_unit': '', 'goodsid': '5kdr0Y0CxtyjyWmo5mu7dYCMtV-GKGOWR8cqPmXWDkZhZp', 'gray_type': [], 'has_coupon': '1', 'hot_push': '1', 'id': '44591247', 'is_88vip': '0', 'is_brand_business': '0', 'is_buydance_goods': '0', 'is_buydance_top': '0', 'is_chaoshi': '0', 'is_choice': '1', 'is_delete': '0', 'is_editor_recommend': '0', 'is_flagship': '0', 'is_goldseller': '0', 'is_gray': '0', 'is_haitao': '0', 'is_high_com': '0', 'is_online': '1', 'is_online_brand': '0', 'is_pure_push': '0', 'is_recommend_goods': 0, 'is_red_shop': '1', 'is_sample': '0', 'is_subdivision': '0', 'is_tmall': '1', 'is_top': 0, 'kol_num': '0', 'lowest': '1', 'lowest_day': '22', 'main_pic': 'https://img.alicdn.com/imgextra/i1/2256668114/O1CN01BxmIFB29oGhXE3J8G_!!2256668114.jpg', 'mao_chao_return': '0.00', 'market_group': [], 'market_img': [], 'max_sales_time': '', 'min_unit_price_by_cate': '0', 'nearly_min_price': '', 'official_fee': '0.00', 'original_price': '29.90', 'price': '23.90', 'promotion_group_num': '0', 'pure_push_switch': '0', 'rank_num': '0', 'red_packet': '0', 'reward': '0.00', 'sales': '6', 'sales_2h': '0', 'sales_daily': '0', 'search_goods_rate': 0, 'seckill_fee': '0.00', 'selection_users_recommend_num': '0', 'seller_id': '4801013124909192891', 'sentiment': '6.44', 'server_tag': [''], 'service_percent': '1.00', 'service_score': '4.84', 'ship_score': '4.85', 'shop_level': '12', 'shop_name': '惠通天下食品专营店', 'similar_goods': 0, 'special': '', 'special_content': '', 'special_text': [], 'start_time': '2024-12-27 00:00:00', 'start_time_stamp': 1735228800, 'sub_title': '榛好季礼盒曲奇华夫饼干500gx2盒', 'subdivision_id': '0', 'subdivision_name': '', 'subdivision_rank': '0', 'subsidy_rate': '0.00', 'tag_id': [], 'taobao_cate_id': '25870', 'team_name': '淘赢客', 'title': '榛好季坚果礼盒曲奇饼干华夫饼年货礼包节日送礼送长辈过年礼盒', 'tk_zs_id': '48223479', 'top_days': '0', 'topn_quantity': '0', 'topn_rate': '', 'topn_total_count': '0', 'trans_device_day8': '0', 'unique_activity': '', 'unit_price': '0', 'users_recommend_num': '0', 'yunfeixian': '0', 'zs_uid': '2668'}], 'no_goods': [], 'show_brand': None, 'show_brand_order': [], 'show_cid': [], 'subdivisionId': '0', 'subdivisionList': None, 'total': 3}}, 'msg': '获取成功', 'time': 1735350416, 'time_format': '2024-12-28 09:46:56'}
        data = response_text.get('data')
        search_list = data.get('search').get('list')
        if search_list:
            for goods in search_list:
                id = goods.get('id')
                shopName = goods.get('shop_name')
                title = goods.get('title')
                bottom_price = goods.get('original_price')
                productImages = goods.get('main_pic')
                commission = goods.get('commission_rate')
                sku = [{"price":  bottom_price, "info": goods.get('sub_title')}]
                url = f"https://dtkapi.ffquan.cn/taobaoapi/get-tpl?gid={id}"
                response = requests.request("GET", url, headers=headers, data=payload)
                # print(json.loads(response.text))
                response_text = {'code': 1, 'data': "<img src='http://imgproxy.linjiabang.cn/i1/6000000002991/*o1*c*n01em*m*lqy1*xxvem*a*x*g*p*h_!!6000000002991-0-at.jpg'></br>趣多多豆豆曲奇缤纷口味新年礼盒24包*384g</br>券后【39.9元】包邮秒杀</br>5元优惠券：<a  target='_blank' href='https://uland.TaoBao.com/quan/detail?sellerId=144185701108507162&activityId=abe3e1ae924a4f17bccf9f8ccf72080e'>https://uland.TaoBao.com/quan/detail?sellerId=144185701108507162&activityId=abe3e1ae924a4f17bccf9f8ccf72080e</a></br>下单链接：<a  target='_blank' href='https://uland.TaoBao.com/item/edetail?id=jjjejQMU0tJZJdvjjnHBeJhJte-bXG76geHGP7jVrvMiZb'>https://uland.TaoBao.com/item/edetail?id=jjjejQMU0tJZJdvjjnHBeJhJte-bXG76geHGP7jVrvMiZb</a></br>趣多多豆豆曲奇缤纷口味新年礼盒24包*384g，原价49.9券后39.9</br>", 'msg': 'ok'}

                url = ''
                res = {
                    'shopName': shopName,
                    'title': title,
                    'sku': sku,
                    'bottom_price': bottom_price,
                    'url': url,
                    'image': productImages,
                    'commission': commission,
                }
                res_list.append(res)
        else:
            break
    if res_list:
        print(res_list)
        return res_list[0]
    else:
        return False





get_taobao_goods({'k_name': '曲奇年礼法丽兹蛇'})
















