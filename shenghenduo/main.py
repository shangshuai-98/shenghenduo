import time, asyncio

from fastapi import FastAPI
from models import Item
from script_tool.shangpinshangjia_v2 import get_goods_info
from script_tool.celery_worker import celery_app as celery_app
from script_tool.ruixing_order import get_order, kf_get_coupon_goods

app = FastAPI()


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
    print(data)
    result = get_order(data.get('order_id'))
    if result:
        return {"code":1, "msg": 'success', 'data': result}
    return {"code":2, "msg": 'fail', 'data': False}


@app.post('/lxy/kf_coupon')
def get_coffee_meal_code(params: dict):
    print(params)
    # face_price = params.get('face_price')
    result = kf_get_coupon_goods(params)
    if result:
        return {"code":1, "msg": 'success', 'data': result}
    return {"code":2, "msg": 'fail', 'data': False}


@app.post("/post")
def post_test():
    return {"method": "post方法"}


@app.put("/put")
def put_test():
    return {"method": "put方法"}


@app.delete("/delete")
def delete_test():
    return {"method": "delete方法"}


@app.get('/task')
async def run_task():
    print('111')
    task = celery_app.send_task('celery_worker.run_task')
    xx = task.wait()
    print(xx)
    return {"msg": "success"}





# if __name__ == '__main__':
#     import uvicorn
#
#     uvicorn.run("main:app", host="127.0.0.1", port=8080, debug=True, reload=True)














