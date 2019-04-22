from bs4 import BeautifulSoup
import requests
from pyquery import PyQuery as pq
import re

source_url = 'http://www.dianping.com/shop/92906666/review_all'
start_position = 67
pages = 115

# 伪装浏览器
headers = {
    'Host': 'www.dianping.com',
    'Accept-Encoding': 'gzip',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"
}


# 克隆cookie
def get_cookie():
    with open('dianping_cookie.txt', 'r') as f:
        cookies = {}
        for line in f.read().split(';'):
            name, value = line.strip().split('=', 1)
            cookies[name] = value
        print(cookies)
        return cookies


def read_source_txt():
    with open('source.txt', 'r') as f:
        source = {}
        for i in f.read().split('}'):
            name = i[1:7]
            value = i[19:-1]
            source[name] = value
        return source


def read_source_svg():
    with open('source.svg', 'rb') as f:
        soup = BeautifulSoup(f.read(), "lxml-xml")
        y_position = soup.find_all("path")
        x_position = soup.find_all("textPath")
        return x_position, y_position


def css_decode(pinglun_html):
    """
    :param css_html: css 的HTML源码
    :param svg_dict: svg加密字库的字典
    :param svg_list: svg加密字库对应的坐标数组[x, y]
    :param pinglun_html: 评论的HTML源码，对应0-详情页的评论，在此处理
    :return: 最终合成的评论
    """
    review = BeautifulSoup(pinglun_html, "lxml")
    pinglun_str = ''
    # print(review.body.children)
    if review.body.p is None:
        iteator = review.body.children
    else:
        iteator = review.body.p.children
    for j in iteator:
        if str(j)[:5] == '<span':
            key = BeautifulSoup(str(j), 'lxml').span['class']
            position = source_position[key[0]].split()
            x_position, y_position = read_source_svg()
            y = int(abs(float(position[1][:-2])))
            x = int(abs(float(position[0][:-2])))
            count = 0
            for i in y_position:
                if y < int(str(i).split()[2]):  # [4:-3]
                    break
                count += 1
            id = str(y_position[count]).split()[4][4:-3]
            word = x_position[int(id) - 1]
            password = BeautifulSoup(str(word), "lxml").text
            pinglun_str += password[x // 14]
        elif str(j)[0] == '<' and str(j)[-1] == '>':
            continue
        else:
            pinglun_str += j

    pinglun_str = pinglun_str.replace('\n', '').replace(' ', '').replace('\t', '')
    # pinglun_str.append(msg.replace("\n", ""))
    str_pinglun = ""
    for x in pinglun_str:
        str_pinglun += x
    # 处理特殊标签
    dr = re.compile(r'</?\w+[^>]*>', re.S)
    dr2 = re.compile(r'<img+[^;]*', re.S)
    dr3 = re.compile(r'&(.*?);', re.S)
    dd = dr.sub('', str_pinglun)
    dd2 = dr2.sub('', dd)
    pinglun_str = dr3.sub('', dd2)
    return pinglun_str


for i in range(start_position, pages):
    url = source_url
    if i != 0:
        back_str = '/p' + str(i + 1)
        url = source_url +back_str
    # print(url)
    s = requests.Session()
    response = s.get(url, headers=headers, cookies=get_cookie())
    print("1 ===> STATUS", response.status_code)
    # print(response.text)
    soup = BeautifulSoup(response.text, 'lxml')
    a = soup.find_all("div", attrs={"class": "review-truncated-words"})
    comments = []
    comment = ''
    # print(a)
    source_position = read_source_txt()
    # print(source_position)
    doc = pq(response.text)
    pinglunLi = doc("div.reviews-items > ul > li").items()
    # print(pinglunLi)
    try:
        for data in pinglunLi:
            # 用户名
            userName = data("div.main-review > div.dper-info > a").text()
            # 用户ID链接
            userID = "http://www.dianping.com" + data("div.main-review > div.dper-info > a").attr("href")
            # 用户评分星级[10-50]
            startShop = str(data("div.review-rank > span").attr("class")).split(" ")[1].replace("sml-str", "")
            # 用户描述：机器：非常好 环境：非常好 服务：非常好 人均：0元
            describeShop = data("div.review-rank > span.score").text()
            # 关键部分，评论HTML,待处理，评论包含隐藏部分和直接展示部分，默认从隐藏部分获取数据，没有则取默认部分。（查看更多）
            pinglun = data("div.review-words.Hide").html()
            try:
                len(pinglun)
            except:
                pinglun = data("div.review-words").html()
            # 该用户喜欢的美食
            loveFood = data("div.main-review > div.review-recommend").text()
            # 发表评论的时间
            pinglunTime = data("div.main-review > div.misc-info.clearfix > span.time").text()
            with open('./result/' + url.split('/')[-2] + '_' + str(i) + '.txt', 'a+', encoding='utf-8') as f:
                print("userName:", userName)
                f.write("userName:" + userName + '\r\n')

                print("userName:", userID)
                f.write("userName:" + userID + '\r\n')

                print("startShop:", startShop)
                f.write("startShop:" + startShop + '\r\n')

                print("describeShop:", describeShop)
                f.write("describeShop:" + describeShop + '\r\n')

                print("loveFood:", loveFood)
                f.write("loveFood:" + loveFood + '\r\n')

                print("commentTime:", pinglunTime)
                f.write("commentTime:" + pinglunTime + '\r\n')

                # print(pinglun)
                print(css_decode(pinglun))
                f.write(css_decode(pinglun) + '\r\n')
                # print("pinglun:", css_decode(dict_css_x_y, dict_svg_text, list_svg_y, pinglun))
                print("*" * 100)
    except:
        continue
