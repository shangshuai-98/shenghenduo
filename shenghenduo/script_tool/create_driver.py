"""
创建 driver
"""

import os
import json

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# from selenium_driverless import webdriver
# from selenium_driverless.types.by import By

import time, random




def create_driver():
    # 设置 ChromeDriver 路径
    chrome_driver_path = "D:/chromedriver/chromedriver.exe"

    # 配置 Chrome 选项
    options = Options()
    # options.add_argument("--headless")  # 无界面模式
    options.add_argument('no-sandbox')  # 禁止沙盒
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("-disable-extensions")
    driver = webdriver.Chrome(service=Service(executable_path=chrome_driver_path), options=options)
    driver.maximize_window()
    return driver




