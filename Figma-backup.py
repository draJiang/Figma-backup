# from curses import pair_number
# from matplotlib.pyplot import pink
import string
import requests
import json
from pykeyboard import *
from pymouse import *
import time
import os
import webbrowser

import datetime

#============================================================

# 【敏感信息】FIGMA 官方的 TOKEN，用于获取团队文件信息
FIGMA_TOKEN = ''

# Figma 团队空间的 ID，可以用浏览器打开团队主页，从 URL 中获取
TEAM_ID = ['1111111111']

# .fig 文件的保存地址，注意浏览器文件下载的默认保存地址也需要成一样的
DOWNLOADED_PATH = '/Figma备份/CC20220803'

# 只备份最近 X 天有编辑过的文件，若为 0 则备份所有文件
DAYS = 0

# Figma 中左上角 Figma LOGO 的坐标
COORD_1_X = 1975.5703125
COORD_1_Y = 314.9296875
# Figma 中 File 的坐标
COORD_2_X = COORD_1_X+120       # Chrome 浏览器中 File 按钮的相对位置
COORD_2_Y = COORD_1_Y+150
# Figma 中 File - Save local copy… 的坐标
COORD_3_X = COORD_1_X+381
COORD_3_Y = COORD_1_Y+287

# 浏览器标签的坐标
COORD_4_X = 3578.8203125
COORD_4_Y = 230.9921875
# 浏览器关闭其他标签按钮的坐标
COORD_5_X = COORD_4_X+95
COORD_5_Y = COORD_4_Y+259

#============================================================

def get_figma_file(team_id):
    '''
    获取团队内的 Figma 文件链接
    '''

    figma_url_list = []

    # 根据 Team ID 获取 Figma 项目 ID
    url = 'https://api.figma.com/v1/teams/'+team_id+'/projects'
    headers = {
        'x-figma-token': FIGMA_TOKEN
    }
    req = requests.get(url=url, headers=headers)
    projectInfo = json.loads(req.text)
    projects = projectInfo['projects']
    
    file_count = 0

    # 遍历项目，获取项目下的文件
    for item in projects:

        url = 'https://api.figma.com/v1/projects/'+item['id']+'/files'
        headers = {
            'x-figma-token': FIGMA_TOKEN
        }
        req = requests.get(url=url, headers=headers)
        filesInfo = json.loads(req.text)
        files = filesInfo['files']

        time.sleep(0.2)
        file_count +=len(files)
        for f in files:
            name = f['name']
            key = f['key']

            # 最近编辑时间
            if(DAYS>0):
                UTC_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
                last_modified = datetime.datetime.strptime(f['last_modified'],UTC_FORMAT)
                today = datetime.date.today()
                d1 = datetime.datetime(last_modified.year,last_modified.month,last_modified.day)
                d2 = datetime.datetime(today.year,today.month,today.day)
                d = d2-d1

                if(d.days>DAYS):
                    # 最近 X 天未编辑，则忽略
                    continue

            url = "https://www.figma.com/file/" + key +'/'+name+"\n"
            
            data_temp = {'key':key,'name':name}
            figma_url_list.append(data_temp)

        print(filesInfo['name'])

    return figma_url_list

def close_tab():
    '''
    关闭浏览器已打开的标签，避免内存爆满造成死机
    '''
    time.sleep(20)

    # 右键点击浏览器标签
    time.sleep(1)
    m.click(COORD_4_X, COORD_4_Y,2,1)
    # 点击关闭其他标签
    time.sleep(1)
    m.click(COORD_5_X, COORD_5_Y,1,1)

    time.sleep(10)

def check_str(str):
    '''
    去除字符串中的特殊字符
    '''
    str = str.replace('.fig','')
    str = str.replace('/','')
    str = str.replace(' ','')
    str = str.replace('_','')
    str = str.replace('"','')
    str = str.replace('“','')
    str = str.replace('”','')
    str = str.replace('：','')
    str = str.replace(':','')

    str.translate(str.maketrans('', '', string.punctuation))

    return str

def get_need_download_list(figma_url_list):
    '''
    排除已下载的 Figma 文件，获取需要下载的文件
    figma_url_list：预计要操作的 FIgma URL 列表
    '''
    need_download = []

    # 获取本地目录下的所有已下载文件，已下载则不需要再下载
    downloaded = []
    for i,j,k in os.walk(DOWNLOADED_PATH):
        downloaded = k

    for index in range(len(figma_url_list)):
        
        new_name = check_str(figma_url_list[index]['name'])

        is_bingo = False

        for file in downloaded:

            new_file = check_str(file)

            if(new_name == new_file):
                # 已存在
                is_bingo = True
                print(str(index)+'：此文件已下载：'+file)
                break
        
        if(is_bingo):
            # 已下载
            continue
        else:
            need_download.append(figma_url_list[index])
    
    return need_download


m = PyMouse() #建立鼠标对象
k = PyKeyboard() #建立键盘对象

# 获取窗口坐标
# print('开始获取坐标，请将鼠标移动到目标位置（若已配置坐标，请忽略）')
time.sleep(6)
print(m.position())
time.sleep(4)
print(m.position())
# print('坐标获取完毕，请将坐标值填入 COORD 变量中（若已配置坐标，请忽略）')


for item in TEAM_ID:

    # 获取 Figma 文件链接
    print('正在获取项目文件：'+item)
    figma_url_list = get_figma_file(item)

    need_download = get_need_download_list(figma_url_list)
    
    print('总文件数：')
    print(len(figma_url_list))
    
    print('待备份文件：')
    for item in need_download:
        print(item)

    print('待备份文件数：')
    print(len(need_download))

    cout = 0

    for index in range(len(need_download)):
        
        # 打开网址(剔除链接中的中文名称，避免浏览器无法打开)
        webbrowser.open('https://www.figma.com/file/'+need_download[index]['key'], new=0, autoraise=True) 
        # 等待文件加载
        time.sleep(14)

        time.sleep(0.5)
        # Figma 中点击左上角 Figma LOGO
        m.click(COORD_1_X, COORD_1_Y)
        time.sleep(0.5)
        # Figma 中点击 File
        m.click(COORD_2_X, COORD_2_Y)
        time.sleep(0.5)
        # Figma 中点击 File - Save local copy…
        m.click(COORD_3_X, COORD_3_Y)
        
        time.sleep(20)

        # 下载记录
        cout= cout+1
        print(str(index+1)+"：已操作文件数："+str(cout)+'/'+str(len(figma_url_list)))
        print('https://www.figma.com/file/'+need_download[index]['key'])

        # 判断是否要清理浏览器标签
        if(cout%20==0):
            # 每下载 x 个文件清理一次
            print('清理浏览器标签……')
            close_tab()

print('结束备份')