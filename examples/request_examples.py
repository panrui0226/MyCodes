import requests
import os
from bs4 import BeautifulSoup
import re
import bs4
import scrapy
import webbrowser


# chrome_path = 'open -a /Applications/Google\ Chrome.app %s'
# webbrowser.get(chrome_path).open("http://www.baidu.com")

# r = requests.get('https://item.jd.com/2967929.html')
# print(r.status_code)
# print(r.encoding)
# print(r.text)

url1 = 'https://item.jd.com/2967929.html'
url3 = 'http://www.baidu.com'

# 定义头文件伪装浏览器
def one():
    url = 'https://www.amazon.cn/gp/product/B01M8L5Z3Y'
    key_value = {'user-agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers = key_value)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        print(r.status_code)
        print(r.text[:1000])
    except Exception as e:
        print(e)


# 搜索内容爬取
def two():
    url = 'http://www.baidu.com/s'
    key_value = {'wd': 'Python'}
    try:
        r = requests.get(url, headers=key_value)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        print(r.request.url)
        print(r.text[:1000])
    except Exception as e:
        print(e)


# 图片爬取
def three():
    url = 'https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1559370878398&di=803dcb6286163764be957f198f701f3d&imgtype=0&src=http%3A%2F%2Fpic37.nipic.com%2F20140113%2F8800276_184927469000_2.png'
    root = '/Users/panrui/Desktop/'
    path = root + url.split('_')[-1]

    try:
        if not os.path.exists(root):
            os.makedirs(root)
        if not os.path.exists(path):
            r = requests.get(url)
            with open(path, 'wb') as f:
                f.write(r.content)
                f.close()
        else:
            print('file is exist')
    except Exception as e:
        print('failed: %s' % e)


# ip地址归属地自动查询
def four():
    url = 'http://m.ip138.com/ip.asp?ip='
    try:
        r = requests.get(url + '202.204.80.112')
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        print(r.text[-500:])
    except Exception as e:
        print('failed')


def five():
    r = requests.get('http://python123.io/ws/demo.html')
    demo = r.text
    soup = BeautifulSoup(demo, 'html.parser')   # 解析内容和选用的解析器
    print(soup.prettify())


# BeautifulSoup类的基本类型
def six():
    r = requests.get('http://python123.io/ws/demo.html')
    demo = r.text
    soup = BeautifulSoup(demo, 'html.parser')  # 解析内容和选用的解析器
    print(soup.title)
    tag = soup.a
    print(tag)
    print(tag.attrs)
    print(tag.attrs['class'])

    print(soup.a.name)
    print(soup.a.parent.name)
    print(soup.a.parent.parent.name)
    print(type(tag.attrs))
    print(type(tag))

    print(soup.a.string)
    print(soup.p.string)
    print(type(soup.p.string))


# 基于bs4库的HTML内容遍历方法
def seven():
    r = requests.get('http://python123.io/ws/demo.html')
    demo = r.text
    soup = BeautifulSoup(demo, 'html.parser')
    print(soup.head)
    # 下行遍历
    print(soup.head.contents)
    print(soup.body.contents)
    # 上行遍历
    print(soup.title.parent)
    # 平行遍历
    print(soup.a.next_sibling)
    print(soup.a.next_sibling.next_sibling)
    print(soup.a.previous_sibling)
    print(soup.a.previous_sibling.previous_sibling)


# 基于bs4库的HTML格式化和编码
def eight():
    r = requests.get('http://python123.io/ws/demo.html')
    demo = r.text
    soup = BeautifulSoup(demo, 'html.parser')
    print(soup.prettify())


# 信息提取的一般方法
# 1. 完整解析信息的标记形式，再提取关键信息
# 2. 无视标记形式，直接搜索关键信息
# 3. 结合形式解析与搜索方法，提取关键信息
def nine():
    # 提取HTML中所有的URL链接
    # 1. 搜索到所有<a>标签
    # 2. 解析<a>标签格式，提取href后的链接内容
    r = requests.get('http://python123.io/ws/demo.html')
    demo = r.text
    soup = BeautifulSoup(demo, 'html.parser')
    for link in soup.find_all('a'):
        print(link.get('href'))


def ten():
    r = requests.get('http://python123.io/ws/demo.html')
    demo = r.text
    soup = BeautifulSoup(demo, 'html.parser')
    list_a = soup.find_all(['a','b'])
    print(list_a)

    for tag in soup.find_all(True):
        print(tag.name)

    for tag in soup.find_all(re.compile('b')):
        print(tag.name)

    # 含有course属性的p标签
    print(soup.find_all('p', 'course'))
    # 属性id的值为link1的所有标签
    print(soup.find_all(id='link1'))

    print(soup.find_all(id=re.compile('link')))


# 中国大学排名定向爬虫
def getHTMLText(url):
    try:
        r = requests.get(url, timeout = 30)
        r.raise_for_status()
        r.encoding = r. apparent_encoding
        return r.text
    except Exception as e:
        return ''


def fillUnivList(ulist, html):
    soup = BeautifulSoup(html, 'html.parser')
    for tr in soup.find('tbody').children:
        if isinstance(tr, bs4.element.Tag):
            tds = tr('td')
            ulist.append([tds[0].string, tds[1].string, tds[2].string])


def printUnivList(ulist, num=10):
    print('{:^10}\t{:^6}\t{:^10}'.format('排名','学校名称','总分'))
    for i in range(num):
        u = ulist[i]
        printUnivList('{:^10}\t{:^6}\t{:^10}'.format(u[0], u[1], u[2]))


def main():
    uinfo = []
    url = 'http://www.zuihaodaxue.cn/zuihaodaxuepaiming2016.html'
    html = getHTMLText(url)
    fillUnivList(uinfo, html)
    printUnivList(uinfo, 10)


if __name__ == '__main__':
    main()
