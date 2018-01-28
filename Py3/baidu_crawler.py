# coding:utf-8
import requests
from lxml import etree
import random
import ip_pool
from bs4 import BeautifulSoup
import time


"""
================================================
 Extract text from the result of BaiDu search

 For Python 3.6+
================================================
"""


def download_html(keywords,proxy):
    """
    抓取网页
    """
    # 抓取参数 https://www.baidu.com/s?wd=testRequest
    key = {'wd': keywords,'pn':0,'rn': 50}

    # 请求Header
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0 cb) like Gecko'}

    proxy = {'http': 'http://'+proxy}

    # 抓取数据内容
    web_content = requests.get("https://www.baidu.com/s?", params=key, headers=headers, proxies=proxy, timeout=4)

    return web_content.text


def html_parser(html):
    """
    解析html
    """
    # 设置提取数据正则
    path_cn = "//div[@id='content_left']//h3[@class='t']/text()"
    path_en = "//div[@id='content_left']//h3[@class='t']/text()"

    # 提取数据
    tree = etree.HTML(html)
    results_cn = tree.xpath(path_cn)
    results_en = tree.xpath(path_en)
    text_cn = [line.strip() for line in results_cn]
    text_en = [line.strip() for line in results_en]

    print(text_cn)

    # 设置返回结果
    text_str = ''

    # 提取数据
    if len(text_cn) != 0 or len(text_en) != 0:
        # 提取中文
        if len(text_cn):
            for i in text_cn:
                text_str += (i.strip())
        # 提取英文
        if len(text_en) != 0:
            for i in text_en:
                text_str += (i.strip())
    # 返回结果
    return text_str


def extract_all_text(keyword_dict, keyword_text, ip_factory):
    """
    存储结果
    """
    useful_proxies = {}
    max_failure_times = 3
    try:
        # 获取代理IP数据
        for ip in ip_factory.get_proxies():
            useful_proxies[ip] = 0
        print ("总共：" + str(len(useful_proxies)) + 'IP可用')
    except OSError:
        print ("获取代理ip时出错！")

    cn = open(keyword_dict, 'r',encoding='utf8')
    for search_word in cn:  
        with open(keyword_text, 'a',encoding='utf8') as ct:  
            getBaiduUrl(useful_proxies,search_word,ct)
            ct.close()
    cn.close()

def getBaiduUrl(useful_proxies,search_word,ct):
    
    # 逐行读取关键词
    print(search_word)
    ct.write(search_word.strip()+':\n')
        
    # 设置随机代理
    proxy = random.choice(list(useful_proxies.keys()))
    print ("change proxies: " + proxy)

    # 存储返回的搜索结果内容
    content = ''

    # 发送查询并异常处理
    try:
        content = download_html(search_word.strip(), proxy)
    except OSError:
        # 超过3次则删除此proxy
        useful_proxies[proxy] += 1
        if useful_proxies[proxy] > 3:
            useful_proxies.remove(proxy)
        # 再抓一次
        proxy = random.choice(useful_proxies.keys())
        content = download_html(search_word.strip(), proxy)

    # 查询结果使用BeautifulSoup处理
    soup = BeautifulSoup(content, "lxml")

    # 按照规则过滤url,获取百度跳转url
    find_domlist = soup.find_all("div",class_="c-container")

    # 使用百度二次跳转获取源url
    link_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0 cb) like Gecko'}
    for link_container in find_domlist:
        link_a = link_container.find("a")
        
        baidu_url_encode = link_a['href']

        try:
            baidu_url_decode = requests.get(baidu_url_encode,headers=link_headers)
        
            decode_url = baidu_url_decode.url
            print(decode_url)
            ct.write(decode_url+'\n')
        
            # 休眠1秒,得考虑下网络慢的情况，我家的网巨差，时间得长些
            time.sleep(2)
        except OSError:  
            print('origin url:'+baidu_url_encode+'deconde error skip....')
            continue  

                       


def main():
    # 抓取搜索关键词
    keyword_dict = 'samples.txt'
    
    # 抓取存取结果
    keyword_text = 'results.txt'

    # 抓取数据
    extract_all_text(keyword_dict, keyword_text, ip_pool.ip_factory)

if __name__ == '__main__':
    main()