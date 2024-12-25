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
import json

import requests, pyperclip
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# from selenium_driverless import webdriver
# from selenium_driverless.types.by import By
from decimal import Decimal, ROUND_HALF_UP

import time, random, re
from script_tool.database import connect_mysql




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
    print(data)
    # data = [['取暖器', '6.97 y@T.LJ 07/23 fOk:/ 【抖音商城】https://v.douyin.com/CeiJAMAVf/ 钻石牌新款取暖器塔式暖风机全屋升温高热干衣立式取暖办公室两用长按复制此条消息，打开抖音搜索，查看商品详情！', '']]
    kw = ''
    user_url = data[0][1]
    remark = data[0][2]
    # if not k_name:
    #     print('商品无法识别')
    #     return ''
    plat, url = link_platform(user_url)  # 拿着url请求，获取用户提交的商品的信息
    driver = create_driver()
    driver.get(url)
    time.sleep(3)
    if plat == 2:  # 拼多多
        print('拼多多')
    elif plat == 5:  # 抖音
        print('抖音')
        # 尝试获取产品参数元素位置
        point = 3
        try:
            try:
                # 执行JavaScript来滚动到页面底部
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                product_params_point = driver.find_element(By.XPATH, '//*[@id="container"]/div[3]/div[2]/div[4]/div/div[1]')
                if product_params_point.text == '产品参数':
                    point = 3
            except Exception as e:
                product_params_point = driver.find_element(By.XPATH, '//*[@id="container"]/div[4]/div[2]/div[4]/div/div[1]')
                if product_params_point.text == '产品参数':
                    point = 4
            shopName = driver.find_element(By.XPATH, f'//*[@id="container"]/div[{point}]/div[2]/div[3]/div/div/div/div[2]/div[1]/div')
            print(shopName.text)
            product_params_dict = {}
            try:
                for i in range(20):
                    # 获取产品参数
                    product_params_k = driver.find_element(By.XPATH, f'//*[@id="container"]/div[{point}]/div[2]/div[4]/div/div[3]/div/div/div[{i+1}]/span')
                    product_params_v = driver.find_element(By.XPATH, f'//*[@id="container"]/div[{point}]/div[2]/div[4]/div/div[3]/div/div/div[{i+1}]/div/div/span')
                    product_params_dict[product_params_k.text] = product_params_v.text
            except Exception as e:
                    print('商品参数获取完成')

            print(product_params_dict)
            brand = product_params_dict.get('品牌') if product_params_dict.get('品牌') else ''
            k_name = url.split('】 ')[1]
            kw = {'店铺名称': shopName.text, "品牌": brand, 'k_name': k_name}
        except Exception as e:
            print('获取商品信息失败')

    elif plat == 4:  # 快手
        print('快手')
    elif plat == 1:  # 淘宝
        print('淘宝')
        # time.sleep(30)
        product_params_dict = {}
        try:
            for i in range(20):
                product_params_k = driver.find_element(By.XPATH, f'//*[@id="ice-container"]/div/div[2]/div[1]/div[2]/div/div[2]/div/div[2]/div[2]/div/div/div[{i+1}]/div[1]')
                product_params_v = driver.find_element(By.XPATH, f'//*[@id="ice-container"]/div/div[2]/div[1]/div[2]/div/div[2]/div/div[2]/div[2]/div/div/div[{i+1}]/div[2]')
                product_params_dict[product_params_k.text] = product_params_v.text
        except Exception as e:
            print('商品参数获取完成')
        print(product_params_dict)
        shopName = driver.find_element(By.XPATH, '//*[@id="ice-container"]/div/div[2]/div[1]/div[1]/a/div[1]/div[2]/span')
        brand = product_params_dict.get('品牌') if product_params_dict.get('品牌') else ''
        k_name = url.split('「')[1]
        kw = {'店铺名称': shopName.text, "品牌": brand, 'k_name': k_name}

    elif plat == 3:  # 京东
        print('京东')

    driver.quit()
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
        return True
    else:
        bottommoney_sql = 'UPDATE fa_wanlshop_bottommoney SET status = 4 WHERE id = %s'
        bottommoney_val = [(bottom_money_id,)]
        connect_mysql(bottommoney_sql, bottommoney_val)
        print('商品无法识别')
        return False


def create_driver(is_headless=False):
    # 设置 ChromeDriver 路径(替换成你自己的路径)
    chrome_driver_path = "D:/chromedriver/chromedriver.exe"
    # 配置 Chrome 选项
    options = Options()
    if is_headless:
        options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('no-sandbox')  # 禁止沙盒
    driver = webdriver.Chrome(service=Service(executable_path=chrome_driver_path), options=options)
    driver.maximize_window()

    return driver


def get_goods(plat, kw):
    if plat == 2:  # 拼多多
        print('拼多多')
    elif plat == 5:  # 抖音
        print('抖音')
        goods_list = get_douyin_goods(kw)
        return goods_list
    elif plat == 4:  # 快手
        print('快手')
    elif plat == 1:  # 淘宝
        print('淘宝')
        goods_list = get_tb_goods(kw)
        return goods_list
    elif plat == 3:  # 京东
        print('京东')


def get_douyin_goods(kw):
    try:
        driver = create_driver()
        driver.get('https://www.reduxingxuan.com/warehouse')
        time.sleep(3)
        search_box = driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div/div[1]/div[2]/div[1]/div/div[1]/div[1]/input')
        # 清除搜索框中的任何现有文本
        search_box.clear()
        search_box.click()
        # 输入要搜索的文本
        print(kw)
        search_box.send_keys(kw.get('k_name'))
        time.sleep(1)
        # 添加回车键来提交搜索
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)
        # 执行JavaScript来滚动到页面底部
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        try:
            no_product = driver.find_element(By.XPATH, '//*[@id="app"]/div[3]/div/div/div/p')
        except Exception as e:
            no_product = False
        if no_product:
            return False
        goods_list = []
        shop_goods_list = []
        for i in range(15 * 2):
            # for i in range(2):
            handler = driver.window_handles
            driver.switch_to.window(handler[-1])
            driver.find_element(By.XPATH, f'//*[@id="app"]/div[3]/div/div/div[1]/div[{i + 1}]/div').click()
            time.sleep(1.2)
            try:
                handler = driver.window_handles
                driver.switch_to.window(handler[-1])
                driver.find_element(By.XPATH, '/html/body/div[7]/div/div/div[2]/div/i').click()
            except Exception as e:
                print(e, '=====ERROR=====')
            time.sleep(0.5)
            img = driver.find_element(By.XPATH, '//*[@id="app"]/div[3]/div[1]/div[1]/div[1]/div[1]/img')
            # 获取图片的src属性
            src = img.get_attribute('src')
            title = driver.find_element(By.XPATH, '//*[@id="app"]/div[3]/div[1]/div[2]/div[1]/div[1]/h3')
            title = title.text
            shopName = driver.find_element(By.XPATH, '//*[@id="app"]/div[3]/div[1]/div[1]/div[2]/div[1]/div[2]/h3')
            shopName = shopName.text
            skuInfo = driver.find_element(By.XPATH, '//*[@id="app"]/div[3]/div[1]/div[2]/div[5]/ul[1]')
            skuInfo = skuInfo.text
            commission = driver.find_element(By.XPATH, '//*[@id="app"]/div[3]/div[1]/div[2]/div[2]/div[3]/p/span[1]')
            commission = commission.text.replace('%', '') if commission else 0
            driver.find_element(By.XPATH, '//*[@id="app"]/div[3]/div[1]/div[2]/div[3]/span[3]').click()
            url = pyperclip.paste()

            # 执行JavaScript命令关闭当前标签页
            driver.execute_script("window.close();")

            if float(commission) <= 10:
                continue
            # if i % 10 == 7:
            #     handler = driver.window_handles
            #     driver.switch_to.window(handler[-1])
            #     driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)

            # if kw.get('店铺名称') in shopName:
                # skuInfo = skuInfo.split('(可领样)')
            sku_list = []
            for sku_info in skuInfo.split('(可领样)'):
                item = sku_info.split(')\n')
                print(item)
                if item[0]:
                    price = item[0].split('(赚')[0]
                    price = price.replace('￥', '')
                    price = price.replace('\n', '')
                    info = item[1]
                    # print(skuInfo)
                    sku_list.append({'price': float(price.strip()), 'info': info})
            sku_list = sorted(sku_list, key=lambda item: item['price'])
            goods_info = {
                'shopName': shopName,
                'title': title,
                'sku': sku_list,
                'bottom_price': sku_list[0].get('price'),
                'url': url,
                'image': src,
                'commission': float(commission),
            }
            if kw.get('店铺名称') in shopName:
                shop_goods_list.append(goods_info)
            else:
                goods_list.append(goods_info)
        if shop_goods_list:
            res_goods_list = shop_goods_list
        else:
            res_goods_list = goods_list
        # 按价格排序
        res = sorted(res_goods_list, key=lambda item: item['bottom_price'])
        print(res[0:5])
        return res[0]
    except Exception as e:
        print('商品识别失败')
        return False


def get_tb_goods(kw):
    driver = create_driver()
    driver.get('https://www.dataoke.com/xp/qlist')
    time.sleep(3)
    search_box = driver.find_element(By.XPATH, '//*[@id="biSearch"]/div[2]/div[2]/form/div[1]/div/div[1]/input')
    # 清除搜索框中的任何现有文本
    search_box.clear()
    search_box.click()
    # 输入要搜索的文本
    print(kw)
    search_box.send_keys(kw.get('k_name'))
    time.sleep(1)
    # 添加回车键来提交搜索
    search_box.send_keys(Keys.RETURN)
    time.sleep(3)
    # 执行JavaScript来滚动到页面底部
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    goods_list = []
    shop_goods_list = []
    for i in range(15 * 2):
        handler = driver.window_handles
        driver.switch_to.window(handler[-1])
        driver.find_element(By.XPATH, f'//*[@id="srcGoods"]/div/div[{i+1}]/div/div/div').click()
        time.sleep(1.2)


def price_count():
    x = 3.10
    y = 800.00
    print(x * (y / 10000))
    sx = x * (y / 10000)
    number = Decimal(sx)
    rounded_number = number.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
    print(rounded_number)


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



if __name__ == '__main__':
    # 我要底价 序号
    get_goods_info(155)


























