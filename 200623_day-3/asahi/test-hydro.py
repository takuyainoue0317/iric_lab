# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 10:19:09 2020

@author: river801 modify takahashi,takahashi
"""

import csv
import time
from datetime import datetime
from datetime import timedelta
import requests
from bs4 import BeautifulSoup
import numpy as np

#####↓関数を定義########################################################

#時間を、文字列←→日付型に相互に変換。どちらへ変換かは型で判別。
def time_tyconv(time):
    if isinstance(time,str):return datetime.strptime(time,'%Y%m%d')
    elif isinstance(time,datetime):return time.strftime("%Y%m%d")
    else:raise TypeError('type-err!')


#日付からステップ数を算出。
#一回にスクレイピングする期間の限度が７日間。次のステップは８日後。
def step_number(start_date, end_date):
    s = time_tyconv(start_date)
    e = time_tyconv(end_date)
    return int(((e-s).days + 1)//8)

#●日後の日付データを求める（start_dateの文字列をdatetime形式変換して７日足す→文字列に戻す）
def date_after_days(time,days):
    day_after = time_tyconv(time) + timedelta(days=days)#ここは日付型
    return time_tyconv(day_after)#ここで文字列になる。


#任意期間のデータを水水DBからスクレイピングする関数。
def scrp_DB(start_date, end_date, location_id,result_list):
    base_url = 'http://www1.river.go.jp'
#    url = "http://www1.river.go.jp/cgi-bin/DspWaterData.exe"
    url = "http://www1.river.go.jp/cgi-bin/DspDamData.exe"
    params = {
        "KIND":1,
        "ID":location_id,
        "BGNDATE":start_date,
        "ENDDATE":end_date,
        "KAWABOU":"NO"
    }
    #iframeのhtmlからsrcURLを取得
    resp = requests.get(url,params=params)
    temp_soup = BeautifulSoup(resp.text,'html.parser')
    resp_iframe = requests.get(base_url+temp_soup.iframe['src'])

    #srcURLのhtmlを取得
    #テーブル内のデータは、iframeにある。iframeのデータは別のhtmlに記述されている。
    #tableが２つあり、border = "●"で区別可能。border = "1"が目的の表。
    soup = BeautifulSoup(resp_iframe.text,'html.parser')
    soup = soup.select_one("table[border='0']")
    tr_list = soup.find_all("tr")
    tr_list.pop(0)
    #ヘッダー分をpop(0)で削除。

    for tr in tr_list:
        result_row = []
        td_list = tr.find_all('td')
        for td in td_list:
            cell = td.get_text()
            if(cell=="-"):              ####欠損値（文字列）をnanに変換
                cell=np.nan
            if(cell=="欠測"):
                cell=np.nan
            result_row.append(cell)
        result_list.append(result_row)

    return result_list

#######↓メインの流れ###################################################

#取得期間、地点番号（おそらく４から始まるほう）、保存ファイル名を設定
start_date = "20060101"
end_date = "20061231"
#csvfile_name = "result_TokachiDam2018.csv"
#location_id = "1368010829060"
#csvfile_name = "result_KyoeiQ2011.csv"
#location_id = "301081281107020"
csvfile_name = "SatsunaiDam2006.csv"
location_id = "1368010829410"

n_step = step_number(start_date, end_date)

result_list = []

#８の倍数回scrp_DBを実行
for n in range(n_step):
    result_list = scrp_DB(start_date, date_after_days(start_date,7), location_id,result_list)
    #start_dateに8日足して、次のループへ
    start_date = date_after_days(start_date,8)
    time.sleep(3)#サーバーへの負荷を考慮し、2秒置く

#８の倍数で余った期間でscrp_DBを実行
result = scrp_DB(start_date, end_date,location_id,result_list)

#CSVとして出力
with open(csvfile_name, 'w') as file:
    writer = csv.writer(file, lineterminator='\n')
    writer.writerows(result)