#爬取地图瓦片数据
from urllib import request
import re
import urllib.request
import os
import random
import math
import configparser

# 配置文件读取
config = configparser.ConfigParser()
config.read('config.ini')

# 下载目录
rootDir = config.get('dir',"rootDir")
# 是否下载道路图
ifRoad = bool(int(config.get('map', "ifRoad")))
# 下载级别
zoom = int(config.get('layer',"zoom"))
# 是否只下载当前层级，不是则从0下载
single = bool(int(config.get('layer',"single")))
# 下载范围左上角经度
leftLon = float(config.get('layer',"leftLon"))
# 下载范围左上角纬度
leftLat = float(config.get('layer',"leftLat"))
# 下载范围右下角经度
rightLon = float(config.get('layer',"rightLon"))
# 下载范围左上角纬度
rightLat = float(config.get('layer',"rightLat"))

agents = [
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.5 (KHTML, like Gecko) Chrome/4.0.249.0 Safari/532.5',
    'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/532.9 (KHTML, like Gecko) Chrome/5.0.310.0 Safari/532.9',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.514.0 Safari/534.7',
    'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/534.14 (KHTML, like Gecko) Chrome/9.0.601.0 Safari/534.14',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.14 (KHTML, like Gecko) Chrome/10.0.601.0 Safari/534.14',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.20 (KHTML, like Gecko) Chrome/11.0.672.2 Safari/534.20',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.27 (KHTML, like Gecko) Chrome/12.0.712.0 Safari/534.27',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.24 Safari/535.1']
print("begin...")

# 经纬度反算切片行列号 使用谷歌
def deg2num(lon_deg, lat_deg, zoom):
    n = 2.0 ** (zoom - 1)
    xtile = int((lon_deg / 180.0 + 1) * n)
    lat_cal = math.tan(lat_deg * math.pi / 180) + (1 / math.cos(lat_deg * math.pi / 180))
    if lat_cal < 0:
        lat_cal = - lat_cal
    ytile = int((1.0 - math.log(lat_cal) / math.pi) * n)
    return (xtile, ytile)


# 下载图片
def getimg(Tpath, Spath, x, y):
    f = open(Spath, 'wb')
    req = urllib.request.Request(Tpath)
    req.add_header('User-Agent', random.choice(agents))  # 换用随机的请求头
    pic = urllib.request.urlopen(req, timeout=60)
    f.write(pic.read())
    f.close()

# 单级别瓦片获取
def singleGet(zoom):
    lefttop = deg2num(leftLon, leftLat ,zoom)  # 下载切片的左上角角点
    rightbottom = deg2num(rightLon, rightLat, zoom)
    nums = (rightbottom[0] - lefttop[0] + 1)*(lefttop[1] - rightbottom[1] + 1)
    print("\n当前下载级别:%d"%zoom + ",共有%d"%nums + "张")
    count = 0 # 进度计数
    # 为了包括两边，加1
    for x in range(lefttop[0] , rightbottom[0] + 1):
        for y in range(rightbottom[1], lefttop[1] + 1):
            #Google影像瓦片
            tilepath = 'http://mt1.google.cn/vt/lyrs=s&hl=zh-CN&x='+ str(x)+'&y='+str(y)+'&z='+str(zoom)+'&s=Gali'
            if(ifRoad):
                #Google地图瓦片
                tilepath = 'http://mt2.google.cn/vt/lyrs=m@167000000&hl=zh-CN&gl=cn&x='+ str(x)+'&y='+str(y)+'&z='+str(zoom)
            path = rootDir + str(zoom) + "\\" + str(x)
            if not os.path.exists(path):
                os.makedirs(path)
            try:
                getimg(tilepath, os.path.join(path, str(y) + ".png"), x, y)
                count += 1
                print('\r'+ str(zoom) + '/' + str(x) + '/' + str(y) + '下载成功，当前第'+ str(count) + '|'+str(nums)+'张['+str(format(count/nums*100 , '.3f'))+'%]', end="")
            except Exception:
                print('\r'+ str(zoom) + '/' + str(x) + '/' + str(y) + '下载失败, 重试。若无需重试，Ctrl+C 结束', end="")
                getimg(tilepath, os.path.join(path, str(y) + ".png"), x, y)

if(single):
    singleGet(zoom)
else:
    for z in range(0, zoom + 1):
        singleGet(z)

print('\n下载完成，输入任意内容回车结束！')
input()
print('over')
