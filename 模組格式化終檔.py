import tkinter as tk
from tkinter import ttk
import re  # 用於正則表達式操作的模組
from bs4 import BeautifulSoup  # 用於解析HTML和XML的模組
import requests  # 用於發送HTTP請求的模組
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(to_email, body):
    # 設置郵件服務器信息
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    # 發送郵件帳號信息
    sender_email = 'shangguancheng1@gmail.com'
    sender_password = 'kknv xnvd olug tpni'

    # 建立郵件內容
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = '您想知道的新聞內容'

    # 添加郵件內容
    msg.attach(MIMEText(body, 'plain'))

    # 建立SMTP連接
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # 啟用安全傳輸層
        # 登錄到郵件帳號
        server.login(sender_email, sender_password)
        # 發送郵件
        server.sendmail(sender_email, to_email, msg.as_string())

    print("郵件已成功發送至", to_email)


# 設置HTTP請求的HEADERS，模擬瀏覽器
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
}

'''
共用函式
'''

# 函式1:獲取新聞列表


def get_news_list(cate_id, page_num=5):  # 參數page_num設定要抓取的頁數，默認為5頁
    """
    獲取新聞列表。

    參數:
        cate_id (int): 分類ID
        page_num (int): 要抓取的頁數

    返回:
        list: 包含新聞的列表
    """
    base_url = "https://udn.com/api/more"  # 基礎API網址
    news_list = []  # 儲存各新聞清單的LIST

    for page in range(page_num):
        channelId = 2
        type_ = 'cate_latest_news'
        query = f"page={page+1}&channelId={channelId}&type={type_}&cate_id={cate_id}&totalRecNo="
        news_list_url = f"{base_url}?{query}"  # 完整的API請求URL

        r = requests.get(news_list_url, headers=HEADERS)  # 發送HTTP GET請求
        news_data = r.json()  # 將回應轉換為JSON格式
        if 'lists' in news_data:  # 檢查回應中是否包含所需清單
            news_list.extend(news_data['lists'])

    return news_list  # 返回獲取的各新聞相關清單

# 函式2:以關鍵字篩選，並建立篩選後的新聞列表


def filter_news(news_list, keywords):
    """
    根據關鍵字篩選新聞。

    參數:
        news_list (list): 新聞列表
        keywords (list): 關鍵字列表

    返回:
        list: 篩選後的新聞列表
    """
    filtered_news = []  # 儲存過濾後的新聞標題與連結
    for news_item in news_list:
        title = news_item.get('title', '')  # 獲取新聞標題
        url = "https://udn.com" + news_item.get('titleLink', '')  # 組合新聞的完整URL
        for keyword in keywords:  # 檢查所有關鍵字
            if keyword in title:  # 如果標題中包含關鍵字
                # 添加新聞標題與URL到過濾的清單
                filtered_news.append({'title': title, 'url': url})
                break
    return filtered_news  # 返回過濾後的新聞清單

# 函式3:獲取文章字數及內容


def get_article_word_count(url):
    """
    獲取文章字數及內容。

    參數:
        url (str): 文章URL

    返回:
        tuple: 包含字數和文章內容的元組
    """
    try:
        r = requests.get(url, headers=HEADERS)  # 發送HTTP GET請求
        soup = BeautifulSoup(r.content, 'html.parser')  # 解析HTML內容
        section = soup.find(
            'section', class_='article-content__editor')  # 找到文章內容的主要區域

        if section:
            paragraphs = section.find_all('p')  # 找到所有段落標籤
            text_list = [p.get_text().strip()
                         for p in paragraphs if p.get_text().strip()]  # 提取並清理段落文字
            article = '\n'.join(text_list)  # 將所有段落合併成一個字符串

            chinese_char_pattern = r'[\u4e00-\u9fff]'  # 用於匹配中文字元的正則表達式模式
            word_count = len(re.findall(
                chinese_char_pattern, article))  # 計算中文字元數量

            return word_count, article  # 返回字數和文章內容
        else:
            return 0, ""  # 如果沒有找到文章內容區域，返回0和空字符串

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch article from {url}: {e}")  # 如果請求失敗，打印錯誤訊息
        return 0, ""


# 函式4:計算文章中關鍵字數量
def count_keywords(article, keywords):
    """
    計算文章中關鍵字的數量。

    參數:
        article (str): 文章內容
        keywords (list): 關鍵字列表

    返回:
        int: 關鍵字數量
    """
    keyword_set = set()  # 使用集合來存儲出現過的關鍵字

    for keyword in keywords:
        if keyword in article and keyword not in keyword_set:  # 如果關鍵字在文章中並且未被記錄
            re.findall(re.escape(keyword), article)  # 使用正則表達式查找關鍵字
            keyword_set.add(keyword)  # 將關鍵字添加到集合中
    keyword_count = len(keyword_set)  # 計算不同關鍵字的數量

    return keyword_count  # 返回關鍵字數量

# 函式5:找出關鍵字最多及字數最多的前三篇文章


def find_top_articles(filtered_news, keywords, top_n=3):
    """
    找出關鍵字數量最多的前幾篇文章。

    參數:
        filtered_news (list): 篩選後的新聞列表
        keywords (list): 關鍵字列表
        top_n (int): 要返回的文章數量

    返回:
        list: 前幾篇包含最多關鍵字的文章列表
    """
    news_with_keyword_count = []

    for news in filtered_news:
        url = news['url']
        word_count, article = get_article_word_count(url)  # 獲取文章字數和內容
        if word_count > 0:
            keyword_count = count_keywords(article, keywords)  # 計算關鍵字數量
            news_with_keyword_count.append({
                'title': news['title'],
                'url': news['url'],
                'keyword_count': keyword_count,
                'word_count': word_count
            })

    # 依關鍵字數量和字數進行排序
    sorted_news = sorted(news_with_keyword_count,
                         key=lambda x: (-x['keyword_count'], -x['word_count']))

    return sorted_news[:top_n]  # 返回前top_n篇新聞


'''
經濟、全球、股市新聞函式
'''
# 經濟新聞


def industry_economic():
    cate_id = 6644
    keywords = ['聯準會', '投資', '稅', 'CPI', '營收', 'AI', '基金', '債', '永續', '通膨', '證交所',
                '報稅', '金控', '房', '金管會', '經濟部', '內政部']

    news_list = get_news_list(cate_id, page_num=5)
    filtered_news = filter_news(news_list, keywords)
    top_news = find_top_articles(filtered_news, keywords, top_n=3)

    news_top = []
    for news in top_news:
        news_top.append("標題：" + news['title'])
        news_top.append("新聞連結：" + news['url'])
    output = '\n'.join(news_top)
    return output

# 股市新聞


def stock_market():
    cate_id = 6645
    keywords = ["台積", "AI", "鴻海", "ETF", "大立光", "台塑", "中華電信", "聯發科", "長榮", "輝達",
                "萬海", "台灣大", "國泰金", "台灣高鐵", "半導體", "科技", "製造", "上市", "合併", "收購"]

    news_list = get_news_list(cate_id, page_num=10)
    filtered_news = filter_news(news_list, keywords)
    top_news = find_top_articles(filtered_news, keywords, top_n=3)

    news_top = []
    for news in top_news:
        news_top.append("標題：" + news['title'])
        news_top.append("新聞連結：" + news['url'])
    output = '\n'.join(news_top)
    return output

# 全球新聞


def global_news():
    cate_id = 7225
    keywords = ["政府", "軍事", "聯合國", "臺灣", "中國", "美國", "蔡英文",
                "賴清德", "習近平", "拜登", "川普", "外交", "談判", "大選",
                "立法院", "總統", "國會", "議員", "歐盟", "共識", "中華民國",
                "戰爭", "兩岸", "國防"]

    news_list = get_news_list(cate_id, page_num=5)
    filtered_news = filter_news(news_list, keywords)
    top_news = find_top_articles(filtered_news, keywords, top_n=3)

    news_top = []
    for news in top_news:
        news_top.append("標題：" + news['title'])
        news_top.append("新聞連結：" + news['url'])
    output = '\n'.join(news_top)
    return output


'''
科技新聞函式
'''


def technology():
    # 定義函式：爬取文章連結
    def crawl_article_links(url, keywords):
        # 發送 HTTP 請求並獲取回應
        r = requests.get(url)

        # 如果回應狀態碼為 200 OK
        if r.status_code == requests.codes.ok:
            # 使用 BeautifulSoup 解析 HTML 文檔
            soup = BeautifulSoup(r.text, "html.parser")

            # 獲取所有 a 標籤，並篩選出指定類別的標籤
            a_tags = soup.find_all('a', class_="wrapper-body-list__cover")

            # 儲存符合條件的文章
            filtered_articles = []

            # 遍歷所有符合條件的標籤
            for tag in a_tags:
                # 獲取文章標題和連結
                title = tag.get('title')
                link = tag.get('href')

                # 獲取文章觀看次數
                view_count_div = tag.find_next(
                    'div', class_='wrapper-body-list__info').find('div', class_='pv')
                if view_count_div:
                    view_count = int(view_count_div.text.strip())
                else:
                    view_count = 0

                # 如果文章標題中包含指定關鍵字，則加入篩選後的文章列表
                if any(keyword.lower() in title.lower() for keyword in keywords):
                    filtered_articles.append((title, link, view_count))

            # 根據觀看次數排序篩選後的文章列表，並取前三個
            filtered_articles.sort(key=lambda x: x[2], reverse=True)
            return filtered_articles[:3]

    # 主函式
    def main():
        # 目標網站 URL
        url = "https://tech.udn.com/tech/rank/newest"

        # 指定關鍵字列表
        keywords = ["5G", "蘋果", "Line", "Google", "iPhone", "科技", "4G", "技術",
                    "人工智慧", "量子計算", "區塊鏈", "虛擬實境", "機器人", "物聯網",
                    "大數據", "網絡安全", "電動車", "自動駕駛", "3D列印", "雲服務",
                    "雲計算", "無人機", "擴增實境", "金融科技", "網絡攻擊", "穿戴裝置",
                    "供應鏈", "聊天機器人", "網絡犯罪", "影像識別", "隱私保護", "智慧製造",
                    "自然語言", "網絡防禦", "三星", "app", "微軟", "AI"]

# 爬取符合條件的文章列表
        filtered_articles = crawl_article_links(url, keywords)

        news_top = []
        for article in filtered_articles:
            title, link, view_count = article
            news_top.append(f"標題: {title}")
            news_top.append(f"新聞連結: {link}")
        output = '\n'.join(news_top)
        return output
    # 程式入口
    if __name__ == "__main__":
        output = main()
    return output


def start_crawling():
    to_email = email_entry.get()
    selected_category = category_combobox.get()
    if selected_category == '產經':
        body = industry_economic()
    elif selected_category == '股市':
        body = stock_market()
    elif selected_category == '全球':
        body = global_news()
    elif selected_category == '科技':
        body = technology()
    send_email(to_email, body)


root = tk.Tk()
root.title("新聞推送")

email_label = tk.Label(root, text="請輸入您的電子郵件:")
email_label.pack()
email_entry = tk.Entry(root)
email_entry.pack()

category_label = tk.Label(root, text="請選擇新聞類別:")
category_label.pack()
categories = ["產經", "全球", "科技", "股市"]
category_combobox = ttk.Combobox(root, values=categories)
category_combobox.pack()

start_button = tk.Button(root, text="開始", command=start_crawling)
start_button.pack()

root.mainloop()
