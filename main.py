import time, asyncio

from fastapi import FastAPI
from models import Item
from script_tool.shangpinshangjia import get_goods_info
from script_tool.celery_worker import celery_app as celery_app

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "wwwwww"}

@app.post('/items/')
def create_item(item: Item):
    print(item.id)
    return {"item_id": item.id, "item_name": item.name, "item_price": item.price}


@app.get("/bottomMoney/{bottom_money_id}")
def get_test(bottom_money_id):
    res = get_goods_info(bottom_money_id)
    if res:
        return {"code": 1, "msg": "商品上架成功", "time": int(time.time()), "data": res}

    return {"code": 2, "msg": "商品无法识别", "time": int(time.time()), "data": res}




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














