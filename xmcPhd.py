# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
import time
from threading import Thread
from threading import Lock
import time
import configparser


def getHTMLText(url):
    """
    获取网页
    """
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        resp.encoding = 'gbk'
        return resp.text
    except:
        return ''

def judgeValidLink(url):
    # 判断是否包含 "t-"
    if "t-" in url:
        if "https" in url:
            return False
        return True
    else:
        return False

def getSonLinks(url):
    """
    获取当前需要爬取的所有子链接
    """

    html = getHTMLText(url)
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # 关键词列表
    mustKeywords = ["北京"]
    
    # 黑名单关键词列表
    blacklistKeywords = ["化学", "生物", "材料", "纳米", "化工", "蛋白质", "物理"]

    # 查找所有的<a>标签
    a_tags = soup.find_all('a')    
    
    matching_links = [
        a['href'] for a in a_tags 
        if any(re.search(keyword, a.get_text(), re.IGNORECASE) for keyword in mustKeywords)  # 匹配必须的关键词
        and not any(re.search(keyword, a.get_text(), re.IGNORECASE) for keyword in blacklistKeywords)  # 排除黑名单关键词
    ]
    
    for target in matching_links:
        if judgeValidLink(target) == False:
            continue
        with open("spiderInfo.txt", "a+", encoding="utf-8") as file:
            # 写入字符串
            target = "https://muchong.com" + target
            file.write(target)
            file.write("\n")

    return 0, url


page = 0
lock = Lock()


def getDataInfo(infoList, pages, url):
    """
    获取数据信息
    """
    global page
    while True:
        lock.acquire()
        page += 1
        lock.release()
        if page > pages:
            break
        url = url + '&page=' + str(page)
        time.sleep(1)
        # lock.acquire()
        html = getHTMLText(url)
        soup = BeautifulSoup(html, 'html.parser')
        tbody = soup.find_all('tbody', 'forum_body_manage')[0]
        trs = tbody.find_all('tr')  # 每个学校的全部信息被tr标签包围
        for tr in trs:  # 遍历每一个学校
            dicts = {}
            href = tr.find_all('a')[0].get('href')  # 定位至a标签，提取href的属性值
            tds = tr.find_all('td')  # 每个学校的各个信息包含在td标签内
            lens = len(tds)
            for i in range(lens):
                if i == 0:
                    title = tds[i].find('a').string
                    dicts[i] = title
                else:
                    dicts[i] = tds[i].string
            dicts['href'] = href
            print(dicts)
            infoList.append(dicts)


def outputCSV(infoList, path):
    """
    输出文档
    """
    data = pd.DataFrame(infoList)
    try:

        data.columns = ['标题', '学校', '门类/专业', '招生人数', '发布时间', '链接']
        data.sort_values(by='发布时间', ascending=False, inplace=True)
        data = data.reset_index(drop=True)
    except:
        print('没有调剂信息...')
        return

    try:
        if not os.path.exists(path):
            data.to_csv(path)
            print('爬取成功')
        else:
            print('路径存在')
    except:
        print('保存失败')


def parameters(pro_='', pro_1='', pro_2='', year=''):
    """
    设定查询参数 -- 专业、年份
    """
    paramsList = [pro_, pro_1, pro_2, year]
    return paramsList


def threadingUp(count, infoList, pages, url):
    """
    启动多线程
    """
    threadList = []
    iList = []
    for i in range(count):
        iList.append(i)
        t = Thread(target=getDataInfo, args=(infoList, pages, url))
        t.start()
        threadList.append(t)
    for thread in threadList:
        thread.join()

def getPageData(config):
    filePath = config.get('Process', 'filePath')
    count = int(config.get('Process', 'count'))
    url = config.get('Process', 'url')
    other = config.get('Process', 'other')
    if os.path.exists(filePath):
        os.remove(filePath)
    for pageNum in range(0, count):
        fatherUrl = url + str(pageNum + 1) + other
        print(fatherUrl)
        getSonLinks(fatherUrl)

    
def main():
    # 创建配置解析器对象
    config = configparser.ConfigParser()

    # 读取配置文件
    config.read('conf.ini')

    getPageData(config)
    start = time.time()
    # threadingUp(count, dataList, pages, url_)  # 多线程
    # getDataInfo(dataList,pages,url_) # 单线程
    # outputCSV(dataList, path)
    end = time.time()
    print('时间:'+str(end - start))


if __name__ == "__main__":
    main()
