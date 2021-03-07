# https://note.nkmk.me/python-beautiful-soup-scraping-yahoo/
# https://qiita.com/go_honn/items/ec96c2246229e4ee2ea6
# https://qiita.com/yuki_bg/items/96a1608aa3f3225386b6
# https://developer.twitter.com/en/portal/apps/20214224/keys

# ツイートできたかわからない
# 文字数オーバー→日付別にツイート分ける？

import urllib.request
from bs4 import BeautifulSoup
import datetime
import twitter
import key

def main():
    url = 'https://site3.sbisec.co.jp/ETGate/WPLETmgR001Control?&burl=search_foreign&cat1=foreign&dir=info&file=foreign_info200123_02.html'
    ipo_list = sbi_scraping(url)
    
    text_ls=[]
    for i in range(1,len(ipo_list)):
        text_ls.append(ipo_list[i][4]) #+'：'+ipo_list[i][0]+' ('+ipo_list[i][3]+')'
        text_ls.append(ipo_list[i][1])
        text_ls.append(ipo_list[i][2]+'\n')
    text_ls.append(url+'\n')
    print('\n'.join(text_ls))
    tweet(text_ls)

def tweet(text_ls):
    auth = twitter.OAuth(
        consumer_key=key.consumer_key,
        consumer_secret=key.consumer_secret,
        token=key.token,
        token_secret=key.token_secret
    )
    t = twitter.Twitter(auth=auth)

    tweet = '\n'.join(text_ls)#改行は改行コードを入れる。
    status=tweet #投稿するツイート
    # print(t.statuses.update(status=status)) #Twitterに投稿
    """
    print("-------------------tweet_text-------------------")
    print(tweet)
    print("-------------------tweet_text-------------------")
    print("tweeted!!!")
    """

def sbi_scraping(url):
    ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) '\
        'AppleWebKit/537.36 (KHTML, like Gecko) '\
        'Chrome/55.0.2883.95 Safari/537.36 '

    req = urllib.request.Request(url, headers={'User-Agent': ua})
    html = urllib.request.urlopen(req)
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find('table', attrs={'class': 'md-l-table-01'}) # テーブルを取得
    rows = table.find_all('tr')
    data=[[v.text for v in rows[0].find_all('th')]] # カラム名を取得
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
        date_str = str(today.year)+ '年' + tmp[-1]
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
    date_str = str(today.year)+ '年' + data[1][4]
    date_format = '%Y年%m月%d日'
    dt_tm = datetime.datetime.strptime(date_str, date_format)
    dt = datetime.date(dt_tm.year, dt_tm.month, dt_tm.day)
    td = dt - today
    print(today, dt, td.days)
    
    for i in sorted_data:
        print(i)
    """
    return sorted_data

if __name__ == "__main__":
    main()