# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
import time
import time
import configparser
from concurrent.futures import ThreadPoolExecutor


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

def inValidLinkFilter(url):
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
        if inValidLinkFilter(target) == False:
            continue
        with open("spiderInfo.txt", "a+", encoding="utf-8") as file:
            # 写入字符串
            target = "https://muchong.com" + target
            file.write(target)
            file.write("\n")

    return 0, url

def getPageData(config):
    filePath = config.get('Process', 'filePath')
    count = int(config.get('Process', 'count'))
    url = config.get('Process', 'url')
    other = config.get('Process', 'other')
    if os.path.exists(filePath):
        os.remove(filePath)
    fatherUrlList = []
    for pageNum in range(0, count):
        fatherUrl = url + str(pageNum + 1) + other
        print(fatherUrl)
        fatherUrlList.append(fatherUrl)
        # getSonLinks(fatherUrl)
    return fatherUrlList

def single_threads(fatherURLList):
    for _, sonUrl in enumerate(fatherURLList):
        getSonLinks(sonUrl)
    
def main():
    # 创建配置解析器对象
    config = configparser.ConfigParser()

    # 读取配置文件
    config.read('conf.ini')
    
    fatherURLList = getPageData(config)
    start = time.time()
    # create_threads(fatherURLList)  # 多线程

    maxPoolNum = int(config.get('Process', 'maxPoolNum'))

    ThreadPool(maxPoolNum, fatherURLList) # 线程池
    # single_threads(fatherURLList)  # 单线程
    # getDataInfo(dataList,pages,url_) # 单线程
    # outputCSV(dataList, path)
    end = time.time()
    print('时间:'+str(end - start))


def ThreadPool(maxPoolNum, urlList):
    # 创建一个线程池，最大线程数为10
    with ThreadPoolExecutor(max_workers=maxPoolNum) as executor:
        # 提交任务并获取处理结果
        results = list(executor.map(getSonLinks, urlList))

if __name__ == "__main__":
    main()
