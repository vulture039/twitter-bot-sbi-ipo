# coding: UTF-8

import urllib.request
from bs4 import BeautifulSoup
import datetime
import twitter
import key
import re

def main():
    ipo_list = sbi_scraping('https://site3.sbisec.co.jp/ETGate/WPLETmgR001Control?&burl=search_foreign&cat1=foreign&dir=info&file=foreign_info200123_02.html')
    text_ls = arrange_text(ipo_list)
    tweet(text_ls)

    """
    for i in text_ls:
        print('\n'.join(i))
    """

def sbi_scraping(url):
    ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) '\
        'AppleWebKit/537.36 (KHTML, like Gecko) '\
        'Chrome/55.0.2883.95 Safari/537.36 '

    req = urllib.request.Request(url, headers={'User-Agent': ua})
    html = urllib.request.urlopen(req)
    soup = BeautifulSoup(html, "html.parser")
    # soup = BeautifulSoup(open('外国株式・海外ETF｜SBI証券.html'), "html.parser")
    table = soup.find('table', attrs={'class': 'md-l-table-01'})
    rows = table.find_all('tr')
    header = [v.text for v in rows[0].find_all('th')]
    header[0], header[1] = header[1], header[0] # データ抽出の都合のため要素を交換
    header.append('上場予定日(date型)')
    data=[header]
    today = datetime.date.today()

    for i in range(1,len(rows)): # 各レコードを取得
        tmp=[]
        brand=rows[i].find('th')
        tmp.append(brand.get_text())
        for cell in rows[i].find_all('td'):
            if cell.find('p', attrs={'class': 'alC'}) != None:
                # 銘柄名['英語', '日本語']のうち、英語のみ取得
                # 全角スペースを削除
                tmp.append(cell.get_text(',').replace('\u3000', '').split(',')[0]) 
            else:
                tmp.append(cell.get_text())
        
        # ソート用にdate型の上場予定日を追加
        try:
            date_str = str(today.year)+ '年' + tmp[1]
            date_format = '%Y年%m月%d日'
            dt_tm = datetime.datetime.strptime(date_str, date_format)
        except ValueError:
            date_str = str(today.year)+ '年' + '12月31日'
            date_format = '%Y年%m月%d日'
            dt_tm = datetime.datetime.strptime(date_str, date_format)
        dt = datetime.date(dt_tm.year, dt_tm.month, dt_tm.day)
        tmp.append(dt)
        data.append(tmp)
    
    # 上場予定日順でソート
    sorted_data = [data[0]]
    sorted_data+=sorted(data[1:len(data)], key=lambda s: s[5])

    # 何日後に上場か算出
    """
    today = datetime.date.today()
    date_str = str(today.year)+ '年' + data[1][1]
    date_format = '%Y年%m月%d日'
    dt_tm = datetime.datetime.strptime(date_str, date_format)
    dt = datetime.date(dt_tm.year, dt_tm.month, dt_tm.day)
    td = dt - today
    print(today, dt, td.days)
    
    for i in sorted_data:
        print(i)
    """

    return sorted_data

def arrange_text(ipo_list):
    day_ls=[ipo_list[i][1] for i in range(1,len(ipo_list))]
    day=sorted(set(day_ls), key=day_ls.index) # 順序をそのままに日付の重複を削除
    text_ls=[['【' + i + '】'] for i in day]

    for i in range(len(text_ls)): # 日付別にまとめる
        for j in range(1,len(ipo_list)):
            if re.findall("(?<=【).+?(?=】)", text_ls[i][0])[0] == ipo_list[j][1]: # 【】以外の文字列で比較
                text_ls[i].append('<' + ipo_list[j][2] + '>')
                text_ls[i].append(ipo_list[j][3] + '\n')
    
    return text_ls

def tweet(text_ls):
    auth = twitter.OAuth(
        consumer_key=key.consumer_key,
        consumer_secret=key.consumer_secret,
        token=key.token,
        token_secret=key.token_secret
    )
    t = twitter.Twitter(auth=auth)
    
    tweet_id=None
    for i in range(3):
        tweet = '\n'.join(text_ls[i])
        statusUpdate = t.statuses.update(status=tweet,in_reply_to_status_id=tweet_id) # Twitterに投稿
        tweet_id = statusUpdate['id_str']
        # print("id:", statusUpdate['user']['screen_name'])
        # print("user_name:", statusUpdate['user']['name'])
        print("tweet:", statusUpdate['text'])

if __name__ == "__main__":
    main()