import json
import time, asyncio

from fastapi import FastAPI, Query, Body
# from fastapi.middleware.cors import CORSMiddleware
from models import Item
from script_tool.shangpinshangjia_v2 import get_goods_info
from script_tool.celery_worker import scheduler
from script_tool.ruixing_order import get_order, kf_get_coupon_goods, kf_check_main
from script_tool.KFC_replace_order import select_stores

app = FastAPI()

# # 允许所有来源的跨域请求
# app.add_middleware(
#     CORSMiddleware,
#     # 允许所有来源的跨域请求
#     allow_origins=["*"],
#     # 参数设置为True表示允许携带身份凭证，如cookies
#     allow_credentials=True,
#     # 表示允许所有HTTP方法的请求
#     allow_methods=["*"],
#     # 表示允许所有请求头
#     allow_headers=["*"]
# )


@app.get("/")
def read_root():
    return {"message": "wwwwww"}

@app.post('/items/')
def create_item(item: Item):
    print(item.id)
    return {"item_id": item.id, "item_name": item.name, "item_price": item.price}


@app.get("/lxy/bottomMoney/{bottom_money_id}")
def get_test(bottom_money_id):
    res = get_goods_info(bottom_money_id)
    if res == 'True':
        return {"code": 1, "msg": "商品上架成功", "time": int(time.time()), "data": res}
    return {"code": 2, "msg": "商品无法识别", "time": int(time.time()), "data": res}

# https://d.luffi.cn/#/?key=F12TlLyrFKa7q4tDMQ
# https://luckin.hqyi.net/#/?code=aDWSvnTrVWYmBpNx7H
# https://d.luffi.cn/#/?key=u45JcPg2inN7wY8QcN
@app.post('/lxy/coffee/mealCode')
def get_coffee_meal_code(data: dict):
    # 914 915
    print(data)
    result = get_order(data.get('pay_on'))
    if result:
        return {"code":1, "msg": 'success', 'data': result}
    return {"code":2, "msg": 'fail', 'data': result}


@app.get('/lxy/coffee/mealCode')
def get_coffee_meal_code(pay_on, order_id):
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
    scheduler.add_job(kf_check_main, 'interval', seconds=60*30)
    scheduler.start()


@app.post('/lxy/taobao/messagetest')
def handle_message(topic: str = Query(...), pub_time: int = Query(...), sign: str = Query(...), data: dict = Body(...)):
    # print(topic)
    # print(pub_time)
    # print(sign)
    print(data)
    tid = data.get('tid')  # 主订单ID
    oid = data.get('oid')  # 子订单ID
    type = data.get('type')  # 交易类型
    status = data.get('status')  # 交易状态
    seller_nick = data.get('seller_nick')  # 卖家昵称
    buyer_nick = data.get('buyer_nick')  # 买家昵称
    buyer_open_uid = data.get('buyer_open_uid')  # 买家OpenUid
    payment = data.get('payment')  # 实付金额



    return {'code': 1000, 'data': '成功'}


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














