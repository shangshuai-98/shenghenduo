import json

from selenium import webdriver
import pyautogui, random, pymysql, datetime

from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from PIL import Image
import time



def connect_mysql(sql, val=(), type=0):
    '''连接数据库方法'''
    #连接数据库
    conn = pymysql.connect(host="rm-m5e21d360fpg0i912po.mysql.rds.aliyuncs.com",port=3306,user="phper",passwd="guchiphper666!",database="data")
    # 测试环境
    # conn = pymysql.connect(host="rm-m5ejp8p16i18lps279o.mysql.rds.aliyuncs.com",port=3306,user="guchi_admin",passwd="gucci_admin888",database="data")
    #使用cursor()方法创建一个游标对象
    cursor = conn.cursor()
    # #使用execute()方法执行SQL语句
    # cursor.execute("SELECT * FROM fa_etc_storeaftersalesdata")
    # #使用fetall()获取全部数据
    # data = cursor.fetchall()
    data = 'ok'
    if type == 1:
        cursor.execute(sql)
        data = cursor.fetchall()
    else:
        try:
            cursor.executemany(sql, val)
            conn.commit()
            # 获取最新的ID
            data = cursor.lastrowid
        except Exception as e:
            print(e)
            print('新增数据失败！')
            conn.rollback()

    cursor.close()
    conn.close()
    #关闭游标和数据库的连接
    return data


def update_image():
    import requests

    url = "https://test.haomachina.cn/addons/alioss/index/upload"

    files = [
        ('file', ('screenshot.png', open('screenshot.png', 'rb'), 'image/png'))
    ]
    payload = {
        "name": f'tao_bao_login_{int(time.time())}'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Host': 'test.haomachina.cn',
    }

    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    return json.loads(response.text)


def taobao_bind_auto(id, account):
    # 设置Chrome选项以在必要时启用无头模式
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # 无头模式
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument(
        'user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"')

    # 指定ChromeDriver的路径
    service = Service('D:/chromedriver/chromedriver.exe')

    # 初始化WebDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 千牛登录URL
    # login_url = 'https://login.taobao.com/member/login.jhtml'
    login_url = 'https://loginmyseller.taobao.com/'
    taobao_login_url = 'https://tb.wanmahui.com/delivery-settings/merchants-info'

    # 打开登录页面
    driver.get(login_url)
    driver.maximize_window()

    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => false})")

    # 等待页面加载完成
    time.sleep(2)

    iframe1 = driver.find_element(By.TAG_NAME, "iframe")
    driver.switch_to.frame(iframe1)

    driver.find_element(By.XPATH, '//*[@id="login"]/div[2]/div/div[1]/a[2]').click()
    time.sleep(1)

    # 输入用户名
    driver.find_element(By.ID, 'fm-sms-login-id').send_keys(account)
    # username_input = driver.find_element(By.ID, 'fm-login-id')
    # username_input.clear()
    # username_input.send_keys('15903071381')

    # 点击获取验证码
    send_btn = driver.find_element(By.XPATH, '//*[@id="login-form"]/div[2]/div[3]').click()
    time.sleep(1)

    # 刷新页面
    # driver.refresh()

    # 拖动鼠标的函数
    def drag_mouse(x1, y1, x2, y2, duration=1):
        # x1, y1 是起始位置
        # x2, y2 是结束位置
        # duration 是拖动的时间，单位是秒

        # 计算拖动的总距离
        distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

        # 计算每个小段的持续时间
        num_steps = 10  # 定义中间点的数量
        step_duration = duration / num_steps

        # 移动到起始位置
        pyautogui.moveTo(x1, y1, duration=0.25)
        # 按下左键
        pyautogui.mouseDown()

        # 在起始点和结束点之间插入中间点
        for i in range(1, num_steps + 1):
            # 计算当前步骤的偏移量
            # 使用随机偏移量来模拟人的不精确拖动
            offset_x = x1 + (x2 - x1) * i / num_steps + random.uniform(-5, 5)
            offset_y = y1 + (y2 - y1) * i / num_steps + random.uniform(-5, 5)

            # 移动到中间点
            pyautogui.moveTo(offset_x, offset_y, duration=step_duration)

        # 释放左键
        pyautogui.mouseUp()

    # for _ in range(6):
    #     drag_mouse(1195, 615, 1576, 621, duration=1)

    # 等待10秒，确保拖动操作完成
    # time.sleep(30)
    # user_input = pyautogui.prompt(text='请输入验证码', title='输入提示框', default='')
    for _ in range(30):
        sql = f'SELECT captcha FROM fa_wanlshop_bindingshop WHERE id = {id}'
        data = connect_mysql(sql, type=1)
        if data[0][0]:
            break
        time.sleep(2)
    captcha = data[0][0]
    # 输入验证码
    driver.find_element(By.XPATH, '//*[@id="fm-smscode"]').send_keys(captcha)
    time.sleep(1)
    # 点击登录按钮
    # login_button = driver.find_element(By.XPATH, '//*[@id="login-form"]/div[5]/button')
    login_button = driver.find_element(By.XPATH, '//*[@id="login-form"]/div[6]/button')
    login_button.click()
    time.sleep(6)

    try:
        # 需要扫码
        driver.find_element(By.XPATH, '//*[@id="alibaba-login-iframe"]')
        # 屏幕截图
        driver.save_screenshot('screenshot.png')
        # 打开原始截图文件
        image = Image.open('screenshot.png')
        # 定义裁剪区域
        left = 1140
        top = 220
        right = 1600
        bottom = 750
        width = right - left
        height = bottom - top
        # 裁剪图片
        cropped_image = image.crop((left, top, right, bottom))
        # 保存裁剪后的图片
        cropped_image.save('screenshot.png')
        # 上传图片
        data = update_image()
        url = data.get('data').get('url')
        sql = f'UPDATE fa_wanlshop_bindingshop SET taobao_login_QRcode = %s WHERE id = %s'
        val = [(url, id)]
        connect_mysql(sql, val)
    except Exception as e:
        # 登录成功，可以进行绑定
        sql = f'UPDATE fa_wanlshop_bindingshop SET taobao_login_QRcode = %s WHERE id = %s'
        val = [(1, id)]
        connect_mysql(sql, val)

    handler = driver.window_handles
    print(handler)
    driver.switch_to.window(handler[-1])

    for _ in range(120):
        try:
            # 找到头像元素 登录成功，可以进行绑定
            driver.find_element(By.XPATH,'//*[@id="icestark-container"]/div[1]/div/div[6]/div')
            break
        except Exception as e:
            # print(e)
            print('扫脸登录中')
            time.sleep(1)

    # 等待登录过程完成
    time.sleep(3)
    driver.get(
        'https://fuwu.taobao.com/ser/detail.htm?spm=a1z13.fuwu_search_result_2023.0.0.14e25acabKKAKc&service_code=FW_GOODS-1001269720&tracelog=qn_search&from_key=%E8%87%AA%E5%8A%A8%E5%8F%91%E8%B4%A7%E9%93%BA%E8%B4%A7%E7%A0%81%E9%80%9F%E8%BE%BE')
    # time.sleep(2)
    time.sleep(5)
    # driver.find_element(By.XPATH, '//*[@id="icestarkNode"]/div/div[2]/div[4]/div[1]/div/div[1]/div/div/div/a/div[1]/div[1]/div/div[1]/div').click()
    # time.sleep(5)
    driver.find_element(By.XPATH,
                        '//*[@id="icestarkNode"]/div/div/div[1]/div/div/div[1]/div/div/div[5]/div[1]/button').click()
    time.sleep(3)
    driver.find_element(By.XPATH,
                        '//*[@id="service-market-container"]/div[2]/div[2]/div/div[2]/div/div/div/div[2]/div/div/div/div/div[1]/div/div/div/ul/li[2]/div').click()
    time.sleep(3)
    driver.find_element(By.XPATH,
                        '//*[@id="service-market-container"]/div[2]/div[2]/div/div[2]/div/div/div/div[2]/div/div/div/div/div[2]/div/div/div/div/div[4]/div[2]/div[1]/span').click()
    time.sleep(1)
    driver.find_element(By.XPATH,
                        '//*[@id="service-market-container"]/div[2]/div[2]/div/div[2]/div/div/div/div[2]/div/div/div/div/div[2]/div/div/div/div/div[6]/div[2]/div[1]/span').click()
    time.sleep(1)
    driver.find_element(By.XPATH,
                        '//*[@id="service-market-container"]/div[2]/div[2]/div/div[2]/div/div/div/div[2]/div/div/div/div/div[2]/div/div/div/div/div[6]/div/div/button').click()
    time.sleep(5)

    handler = driver.window_handles
    driver.switch_to.window(handler[-1])
    driver.find_element(By.XPATH,
                        '//*[@id="icestarkNode"]/div/div/div/div/div[1]/div[2]/div/div/div/div[2]/div/div/div[2]/div/div[3]/label/span[1]/input').click()
    time.sleep(1)
    driver.find_element(By.XPATH,
                        '//*[@id="icestarkNode"]/div/div/div/div/div[1]/div[2]/div/div/div/div[2]/div/div/div[3]/div/button').click()
    time.sleep(2)
    driver.find_element(By.XPATH, '//*[@id="icestarkNode"]/div/div/div/div/div[2]/div[4]/button').click()
    time.sleep(1)

    # 弹框提示扫码付款
    pyautogui.alert(text='请扫码付款,付款后等待页面跳转完成再点击确定', title='消息')

    # 点击去使用
    driver.find_element(By.XPATH,
                        '//*[@id="icestarkNode"]/div/div/div/div/div/div/div[1]/div/div/div[3]/button[1]/span').click()
    time.sleep(10)
    handler = driver.window_handles
    print(handler)
    driver.switch_to.window(handler[-1])
    # # 进入码速达后台
    # driver.get(taobao_login_url)
    # driver.maximize_window()
    #
    # driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => false})")
    #
    # time.sleep(35)
    # 点击商户信息
    # pyautogui.moveTo(80, 735)
    # pyautogui.click()
    # time.sleep(2)
    driver.find_element(By.XPATH,
                        '//*[@id="app"]/section/section/section/div/div/div/div/div[1]/div[3]/div[2]/div[4]/span[2]').click()
    time.sleep(2)

    # # 点击复制商户授权码
    # pyautogui.moveTo(1825, 420)
    # pyautogui.click()
    # time.sleep(2)
    auth_code = driver.find_element(By.XPATH,
                                    '//*[@id="app"]/section/section/section/section/main/div/div[2]/div[2]/div[2]/div/div/div/div/table/tbody/tr/td[4]/span/span').text
    print(auth_code)
    openid_code = driver.find_element(By.XPATH,
                                      '//*[@id="app"]/section/section/section/section/main/div/div[2]/div[2]/div[2]/div/div/div/div/table/tbody/tr/td[5]/span/span').text
    print(openid_code)

    sql = f'UPDATE fa_wanlshop_bindingshop SET auth_code = %s, openid_code = %s WHERE id = {id}'
    val = [tuple([auth_code, openid_code])]
    connect_mysql(sql, val)


    # 关闭浏览器
    driver.quit()


if __name__ == '__main__':
    # account = '17338567044'

    id = ''
    while True:
        sql = 'SELECT * FROM fa_wanlshop_bindingshop ORDER BY id desc LIMIT 0, 1'
        data = connect_mysql(sql, type=1)
        if id == data[0][0] and data[0][9]:
            print('=-='*15)
            print(datetime.datetime.now())
            print('目前没有需要绑定店铺')
            print('=-='*15)
            time.sleep(1)
            continue
        else:
            # print(data)
            if data[0][9]:
                print('=-=' * 15)
                print(datetime.datetime.now())
                print('目前没有需要绑定店铺')
                print('=-=' * 15)
                time.sleep(1)
                continue
            id = data[0][0]
            platform = data[0][2]
            account = data[0][5]
            if platform == '5':
                print('=-=' * 15)
                print('开始绑定店铺自动发货')
                try:
                    taobao_bind_auto(id, account)
                    print(f'{id} 店铺自动发货已绑定')
                except Exception as e:
                    sql = 'UPDATE fa_wanlshop_bindingshop SET auth_code = "Binding failed", openid_code = "No Openid", taobao_login_QRcode = 1 WHERE id = %s'
                    val = [(id, )]
                    print(val)
                    print(sql)
                    connect_mysql(sql, val)
                    print(e)
                    print('绑定店铺失败')
                print('=-=' * 15)
        time.sleep(1)























