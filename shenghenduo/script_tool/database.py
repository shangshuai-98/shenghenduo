
import pymysql





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