"""闲鱼脚本
"""





import time

import requests
import hashlib


headers = {
    "accept": "application/json",
    "accept-language": "zh-CN,zh;q=0.9",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://www.goofish.com",
    "priority": "u=1, i",
    "referer": "https://www.goofish.com/",
    "sec-ch-ua": "Google Chrome;v=131, Chromium;v=131, Not_A Brand;v=24",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}
cookies = {
    "cna": "fs//H6rWEE4BASQJikWkTZs/",
    "cookie2": "1c4e46b3e3564236fb8f85fd603d4f4f",
    "xlly_s": "1",
    "mtop_partitioned_detect": "1",
    "_m_h5_tk": "3959d763edd58aab1954b5e95b6badd7_1736046153394",
    "_m_h5_tk_enc": "b76976f11f738f7c12f3b9545fa13daf",
    "_samesite_flag_": "true",
    "t": "2ee8129c2e20fdfcb45797b9d5a70e39",
    "_tb_token_": "5543e496e8d75",
    "tracknick": "%E6%94%B6%E6%8B%BE%E6%94%B6%E6%8B%BE%E5%90%A7s",
    "unb": "2733974492",
    "sgcookie": "E100aHLQ%2FCWniYMyDmvCaBxzRVVZLZz1MZepwcBybuhuwXerYxLo8muwuYnRck6XtLh4BRCMUUmsqiIrhnFVFkedJs1juonn55gMuqUTN6tQBEI%3D",
    "csg": "9eb02c9d",
    "isg": "BP39nqI9RmV8OeKJ-Niq_r3iDFn3mjHsXdItpL9CsdSD9hgogOvtvbOloCqw9kmk",
    "tfstk": "gVYiCAxVehS6xkv8Bp7sVs6RpAnLC5_fvKUAHZBqY9WQBRU9g-vDLLdTWEdVnKvddj6O6FFcgNTpXrBtCZA2eZD-e43J1C_5uYHJQIPfAa5z0PyAbMWFksVrvq3B1C_bOWeq2HR_nCE7fC723wSFG_bV_OzZtk5lLP547syEts6FusSN0kzFG1zabPJ2TXffLt7VbvSzuTY2RekhBuoSpsKB-1jGUBm7orydg8Bv_74zrexhjTkRKrz2-1ApYcD3rmByVOIRxpuLSZAFipjJjY4MnIRW0MY0QfpygdTh5amzjLJMCF1BAxqcEnR9VejQgrJlSKjy7MV4uNb1CwfezjE5peX93FjEwzjA8UIP7HnIBiQGZK86IS42UBdJ5MTmEJWXX__FiEGzmtjV4krU4Dcbl6lv8oZfb61hela5fbGf_H4xtXqSfG5C6YhntoZfb61heXc3V-sNO1HR."
}

url = "https://h5api.m.goofish.com/h5/mtop.taobao.idlemtopsearch.pc.search/1.0/"

data = {
    "data": '{"pageNumber":1,"keyword":"苹果16","fromFilter":false,"rowsPerPage":30,"sortValue":"","sortField":"","customDistance":"","gps":"","propValueStr":{},"customGps":"","searchReqFromPage":"pcSearch","extraFilterValue":"{}","userPositionJson":"{}"}'
}
# print(data.get('data'))

token = cookies.get('_m_h5_tk').split('_')[0]
sign = f'{token}&{int(time.time() * 1000)}&{34839810}&{data.get('data')}'
# print(sign)
def md5_encryption(data):
    md5 = hashlib.md5()  # 创建一个md5对象
    md5.update(data.encode('utf-8'))  # 使用utf-8编码数据
    return md5.hexdigest()  # 返回加密后的十六进制字符串
md5_sign = md5_encryption(sign)
print(md5_sign)
params = {
    "jsv": "2.7.2",
    "appKey": "34839810",
    "t": str(int(time.time() * 1000)),
    "sign": md5_sign, # f'{token}&{int(time.time())&{appKey}&{data}}'
    "v": "1.0",
    "type": "originaljson",
    "accountSite": "xianyu",
    "dataType": "json",
    "timeout": "20000",
    "api": "mtop.taobao.idlemtopsearch.pc.search",
    "sessionOption": "AutoLoginOnly",
    "spm_cnt": "a21ybx.search.0.0",
    "spm_pre": "a21ybx.home.categories.412.4c053da6T8mG57",
    "log_id": "4c053da6T8mG57"
}


response = requests.post(url, headers=headers, cookies=cookies, params=params, data=data)

print(response.text)



















