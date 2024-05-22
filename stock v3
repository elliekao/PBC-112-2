import requests
from bs4 import BeautifulSoup
import re

# 以內文關鍵字篩選

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
}


def get_news_list(page_num=5):
    base_url = "https://udn.com/api/more"
    news_list = []

    for page in range(page_num):
        channelId = 2
        type_ = 'cate_latest_news'
        cate_id = 6645
        query = f"page={page+1}&channelId={channelId}&type={type_}&cate_id={cate_id}&totalRecNo="
        news_list_url = f"{base_url}?{query}"

        r = requests.get(news_list_url, headers=HEADERS)
        news_data = r.json()
        if 'lists' in news_data:
            news_list.extend(news_data['lists'])

    return news_list


def filter_news(news_list):
    keywords = ["台積", "AI", "鴻海", "ETF", "大立光", "台塑", "中華電信", "聯發科", "長榮", "輝達",
                "萬海", "台灣大", "國泰金", "台灣高鐵", "半導體", "科技", "製造", "上市", "合併", "收購"]

    filtered_news = []
    for news_item in news_list:
        title = news_item.get('title', '')
        url = "https://udn.com" + news_item.get('titleLink', '')
        for keyword in keywords:
            if keyword in title:
                filtered_news.append({'title': title, 'url': url})
                break
    return filtered_news


def get_article_word_count(url):
    try:
        r = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        section = soup.find('section', class_='article-content__editor')

        if section:
            paragraphs = section.find_all('p')
            text_list = [p.get_text().strip()
                         for p in paragraphs if p.get_text().strip()]
            article = '\n'.join(text_list)

            chinese_char_pattern = r'[\u4e00-\u9fff]'
            word_count = len(re.findall(chinese_char_pattern, article))

            return word_count, article
        else:
            return 0, ""

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch article from {url}: {e}")
        return 0, ""


def count_keywords(article, keywords):
    keyword_set = set()

    for keyword in keywords:
        if keyword in article and keyword not in keyword_set:
            re.findall(re.escape(keyword), article)
            keyword_set.add(keyword)
    keyword_count = len(keyword_set)

    return keyword_count


def find_top_articles(filtered_news, keywords, top_n=3):
    news_with_keyword_count = []

    for news in filtered_news:
        url = news['url']
        word_count, article = get_article_word_count(url)
        if word_count > 0:
            keyword_count = count_keywords(article, keywords)
            news_with_keyword_count.append({
                'title': news['title'],
                'url': news['url'],
                'keyword_count': keyword_count,
                'word_count': word_count
            })

    # Sort by keyword_count descending and then by word_count descending
    sorted_news = sorted(news_with_keyword_count,
                         key=lambda x: (-x['keyword_count'], -x['word_count']))

    return sorted_news[:top_n]


if __name__ == "__main__":
    news_list = get_news_list(page_num=5)
    filtered_news = filter_news(news_list)
    keywords = ["台積", "AI", "鴻海", "ETF", "大立光", "台塑", "中華電信", "聯發科", "長榮", "輝達",
                "萬海", "台灣大", "國泰金", "台灣高鐵", "半導體", "科技", "製造", "上市", "合併", "收購"]

    top_news = find_top_articles(filtered_news, keywords, top_n=3)

    for news in top_news:
        print("標題：", news['title'])
        print("新聞連結：", news['url'])
        print("關鍵詞數量：", news['keyword_count'])
        print("字數：", news['word_count'])
        print()
