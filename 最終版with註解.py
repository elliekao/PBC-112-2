import requests  # 用於發送HTTP請求的模組
from bs4 import BeautifulSoup  # 用於解析HTML和XML的模組
import re  # 用於正則表達式操作的模組

# 設置HTTP請求的HEADERS，模擬瀏覽器
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
}

# 定義函數以獲取新聞列表，參數page_num設定要抓取的頁數，默認為5頁


def get_news_list(page_num=5):
    base_url = "https://udn.com/api/more"  # 基礎API網址
    news_list = []  # 存儲各新聞清單的LIST

    for page in range(page_num):
        channelId = 2
        type_ = 'cate_latest_news'
        cate_id = 6645
        query = f"page={page+1}&channelId={channelId}&type={type_}&cate_id={cate_id}&totalRecNo="
        news_list_url = f"{base_url}?{query}"  # 完整的API請求URL

        r = requests.get(news_list_url, headers=HEADERS)  # 發送HTTP GET請求
        news_data = r.json()  # 將回應轉換為JSON格式
        if 'lists' in news_data:  # 檢查回應中是否包含所需清單
            news_list.extend(news_data['lists'])

    return news_list  # 返回獲取的各新聞相關清單

# 定義函數以過濾新聞標題，根據特定關鍵字篩選


def filter_news(news_list):
    keywords = ["台積", "AI", "鴻海", "ETF", "大立光", "台塑", "中華電信", "聯發科", "長榮", "輝達",
                "萬海", "台灣大", "國泰金", "台灣高鐵", "半導體", "科技", "製造", "上市", "合併", "收購"]

    filtered_news = []  # 存儲過濾後的新聞標題與連結
    for news_item in news_list:
        title = news_item.get('title', '')  # 獲取新聞標題
        url = "https://udn.com" + news_item.get('titleLink', '')  # 組合新聞的完整URL
        for keyword in keywords:  # 檢查所有關鍵字
            if keyword in title:  # 如果標題中包含關鍵字
                # 添加新聞標題與URL到過濾的清單
                filtered_news.append({'title': title, 'url': url})
                break
    return filtered_news  # 返回過濾後的新聞清單

# 定義函數以獲得內文內容


def get_article_word_count(url):
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

# 定義函數以計算內文中包含多少關鍵字


def count_keywords(article, keywords):
    keyword_set = set()  # 使用集合來存儲出現過的關鍵字

    for keyword in keywords:
        if keyword in article and keyword not in keyword_set:  # 如果關鍵字在文章中並且未被記錄
            re.findall(re.escape(keyword), article)  # 使用正則表達式查找關鍵字
            keyword_set.add(keyword)  # 將關鍵字添加到集合中
    keyword_count = len(keyword_set)  # 計算不同關鍵字的數量

    return keyword_count  # 返回關鍵字數量

# 定義函數以找到內文包含最多關鍵字的前幾篇文章


def find_top_articles(filtered_news, keywords, top_n=3):
    news_with_keyword_count = []  # 存儲帶有關鍵字計數的新聞列表

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

    # 根據內文關鍵字數量和文章字數排序以篩選出三篇文章
    sorted_news = sorted(news_with_keyword_count,
                         key=lambda x: (-x['keyword_count'], -x['word_count']))

    return sorted_news[:top_n]  # 返回前top_n篇新聞


# 主程式包含三階段篩選，分別是新聞標題關鍵字、新聞內文關鍵字，以及新聞內文字數
if __name__ == "__main__":
    news_list = get_news_list(page_num=5)  # 獲取新聞列表
    filtered_news = filter_news(news_list)  # 用標題內的關鍵字過濾新聞
    keywords = ["台積", "AI", "鴻海", "ETF", "大立光", "台塑", "中華電信", "聯發科", "長榮", "輝達",
                "萬海", "台灣大", "國泰金", "台灣高鐵", "半導體", "科技", "製造", "上市", "合併", "收購"]

    # 再從裡面找到前3篇包含最多關鍵字的新聞，若關鍵字數重複則以文章內容字數來做第三階段篩選
    top_news = find_top_articles(filtered_news, keywords, top_n=3)

    for news in top_news:
        print("標題：", news['title'])
        print("新聞連結：", news['url'])
        print()
