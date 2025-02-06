import json
import time, asyncio, os

from fastapi import FastAPI, Query, Body
from apscheduler.triggers.cron import CronTrigger
# from fastapi.middleware.cors import CORSMiddleware
from models import Item
from script_tool.shangpinshangjia_v2 import get_goods_info
from script_tool.celery_worker import scheduler
from script_tool.ruixing_order import get_order, kf_get_coupon_goods, kf_check_main, update_goods_price, kf_coupon_getDirs
from script_tool.KFC_replace_order import select_stores

app = FastAPI()



@app.get("/")
def read_root():
    return {"message": "wwwwww"}


@app.get("/lxy/bottomMoney/{bottom_money_id}")
def get_test(bottom_money_id):
    res = get_goods_info(bottom_money_id)
    if res == 'True':
        return {"code": 1, "msg": "商品上架成功", "time": int(time.time()), "data": res}
    return {"code": 2, "msg": "商品无法识别", "time": int(time.time()), "data": res}

# https://d.luffi.cn/#/?key=F12TlLyrFKa7q4tDMQ
# https://luckin.hqyi.net/#/?code=aDWSvnTrVWYmBpNx7H
# https://d.luffi.cn/#/?key=u45JcPg2inN7wY8QcN
# @app.post('/lxy/coffee/mealCode')
# def get_coffee_meal_code(data: dict):
#     # 914 915
#     print(data)
#     result = get_order(data.get('pay_on'))
#     if result:
#         return {"code":1, "msg": 'success', 'data': result}
#     return {"code":2, "msg": 'fail', 'data': result}


@app.get('/lxy/coffee/mealCode')
def get_coffee_meal_code(pay_on, order_id):
    # 快发平台优惠券兑换返回取餐码
    # print(pay_on)
    # print(order_id)
    params={'pay_on': pay_on, 'order_id': order_id}
    result = get_order(params)
    if result:
        return {"code":1, "msg": 'success', 'data': result}
    return {"code":2, "msg": 'fail', 'data': result}


@app.post('/lxy/kf_coupon')
def get_kf_coupon_code(params: dict):
    print(params)
    # face_price = params.get('face_price')
    result = kf_get_coupon_goods(params)
    if result:
        return {"code":1, "msg": 'success', 'data': result}
    return {"code":2, "msg": 'fail', 'data': result}


@app.get('/lxy/KFC_city')
def get_KFC_city_code(gbCityCode, keyword):
    result = select_stores(gbCityCode, keyword)
    result = json.loads(result.text)
    if result:
        return {"code":1, "msg": 'success', 'data': result}
    return {"code":2, "msg": 'fail', 'data': result}


@app.on_event("startup")
async def startup_event():
    # print(os.getenv('GUNICORN_WORKER'))
    # if os.getenv('GUNICORN_WORKER') == 'primary':
    # scheduler.add_job(
    #     kf_check_main, 'interval', seconds=60*30
    # )
    scheduler.add_job(
        func=kf_coupon_getDirs,
        trigger=CronTrigger(minute='25,55'),
        id='kf_coupon_getDirs_job',  # 为任务设置一个唯一标识符
        name='Update goods status',  # 为任务设置一个名称
    )
    # scheduler.add_job(
    #     func=update_goods_price,
    #     trigger=CronTrigger(hour=1, minute=0),
    #     id='update_goods_price_job',  # 为任务设置一个唯一标识符
    #     name='Update goods price',  # 为任务设置一个名称
    # )
    scheduler.start()


@app.post("/post")
def post_test():
    return {"method": "post方法"}


@app.put("/put")
def put_test():
    return {"method": "put方法"}


@app.delete("/delete")
def delete_test():
    return {"method": "delete方法"}








# if __name__ == '__main__':
#     import uvicorn
#
#     uvicorn.run("main:app", host="127.0.0.1", port=8080, debug=True, reload=True)














