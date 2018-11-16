#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os

# 取得有效交易月的List


def GetMonthList(StartDate, EndDate):
    sDate = []
    fdttime = datetime.strptime(StartDate, '%Y%m')
    tdttime = datetime.strptime(EndDate, '%Y%m')
    if fdttime != tdttime:
        while tdttime >= fdttime:
            sDate.append(fdttime.strftime('%Y%m'))
            fdttime = fdttime + relativedelta(months=1)
    else:
        sDate.append(fdttime.strftime('%Y%m'))
    DateList = pd.DataFrame(sDate, columns=['Month'])
    return DateList

# 取得有效交易日


def GetTradeDate(TradeYear, TradeMonth):
    url = 'http://www.twse.com.tw/ch/trading/exchange/FMTQIK/genpage/Report{}/{}_F3_1_2.php?STK_NO=&myear={}&mmon={}'
    url = url.format(TradeYear+TradeMonth, TradeYear +
                     TradeMonth, TradeYear, TradeMonth)
    res = requests.get(url)
    res.encoding = 'BIG5'
    soup = bs(res.text)
    tb = soup.select('#contentblock > td > table.board_trad')[0]
    df = pd.read_html(tb.prettify('utf-8'), encoding='utf-8',
                      skiprows=[0], header=0)
    df = df[0]
    return df[u'日期']

# 取得有效交易日期


def GetTradeDateList(StartDate, EndDate):
    sDate = []
    fdttime = datetime.strptime(StartDate, '%Y%m%d')
    tdttime = datetime.strptime(EndDate, '%Y%m%d')
    MonthList = GetMonthList(StartDate[:6], EndDate[:6])
    for idx, row in MonthList.iterrows():
        TradeDateList = GetTradeDate(row['Month'][:4], row['Month'][4:])
        for date in TradeDateList:
            Date = datetime.strptime(
                str(int(date[0:3])+1911)+date[3:], '%Y/%m/%d')
            if fdttime <= Date and Date <= tdttime:
                sDate.append(Date.strftime('%Y/%m/%d'))
    DateList = pd.DataFrame(sDate, columns=['Month'])
    return DateList

# 取得加權指數(TWSE)的交易金額


def GetTWSETradeAmount(TradeYear, TradeMonth, TradeDay):
    url = 'http://www.twse.com.tw/ch/trading/exchange/MI_5MINS/genpage/Report{}/A125{}.php?chk_date={}/{}/{}'
    url = url.format(TradeYear+TradeMonth, TradeYear+TradeMonth +
                     TradeDay, str(int(TradeYear)-1911), TradeMonth, TradeDay)
    #url = url.format('201606', '20160617', '105', '06', '17')
    res = requests.get(url)
    res.encoding = 'BIG5'
    soup = bs(res.text)
    tb = soup.select('#tbl-container > table')[0]
    df = pd.read_html(tb.prettify('utf-8'), encoding='utf-8')
    TWSE = df[0].iloc[:, [0, 7]]
    TWSE.columns = [u'Time', u'累積成交金額']
    # TWSE[u'累積成交金額'] - TWSE[u'累積成交金額'].shift(1)
    TWSE.loc[:, u'Volume'] = TWSE[u'累積成交金額'].diff()*100
    TWSE.drop([0], inplace=True)
    TWSEAmount = TWSE.loc[:, [u'Time', u'Volume']]
    TWSEAmount[u'Volume'] = TWSEAmount[u'Volume'].astype(int)
    return TWSEAmount

# 取得加權指數(TWSE)的交易價格 2016/07/15網址已變更


def GetTWSETradePrice(TradeYear, TradeMonth, TradeDay):
    url = 'http://www.twse.com.tw/ch/trading/exchange/MI_5MINS_INDEX/MI_5MINS_INDEX.php'
    qdate = '{}/{}/{}'
    qdate = qdate.format(str(int(TradeYear)-1911), TradeMonth, TradeDay)
    payload = {
        'qdate': qdate
    }
    res = requests.post(url, data=payload)
    # res.encoding='utf-8'
    soup = bs(res.text)
    tb = soup.select('#main-content > table')[0]
    df = pd.read_html(tb.prettify('utf-8'), encoding='utf-8', skiprows=[0])
    TWSEPrice = df[0].iloc[:, [0, 1]]
    TWSEPrice.columns = [u'Time', u'Price']
    return TWSEPrice

# 將加權指數(TWSE)交易價格與交易金額整合成同一份並輸出成TXT


def MergeDataFrametoTXT(StartDate, EndDate):
    Current_Dir = os.getcwd()
    TWSE_Dir = os.path.join(Current_Dir, "TWSE")
    Daily_Dir = os.path.join(Current_Dir, "TWSE\Daily_Date")
    All_Dir = os.path.join(Current_Dir, "TWSE\All_Date")
    if not os.path.exists(TWSE_Dir):
        os.makedirs(TWSE_Dir)
    if not os.path.exists(Daily_Dir):
        os.makedirs(Daily_Dir)
    if not os.path.exists(All_Dir):
        os.makedirs(All_Dir)

    TradeDateList = GetTradeDateList(StartDate, EndDate)
    for idx, row in TradeDateList.iterrows():
        #TWSETradePrice = GetTWSETradePrice('2016', '06', '17')
        TWSETradePrice = GetTWSETradePrice(
            row['Month'][:4], row['Month'][5:-3], row['Month'][8:])
        #TWSETradeAmount = GetTWSETradeAmount('2016', '06', '17')
        TWSETradeAmount = GetTWSETradeAmount(
            row['Month'][:4], row['Month'][5:-3], row['Month'][8:])
        df = pd.merge(TWSETradePrice, TWSETradeAmount)
        df.insert(0, 'Date', pd.Timestamp(
            row['Month'][:4]+'/'+row['Month'][5:-3]+'/'+row['Month'][8:]).strftime('%Y/%m/%d'))
        File_path = os.path.join(
            Daily_Dir, 'TWSE_Tick_' + row['Month'][:4]+row['Month'][5:-3]+row['Month'][8:]+'.txt')
        df.to_csv(File_path, index=False)
        print row['Month'][:4]+row['Month'][5:-3]+row['Month'][8:]+'.txt 完成....'

# 整合多天的TWSE Tick的資料到同一份TXT


def DataIntegration(StartTime, EndTime):
    File_paths = []
    Current_Dir = os.getcwd()
    TWSE_Dir = os.path.join(Current_Dir, "TWSE")
    Daily_Dir = os.path.join(Current_Dir, "TWSE\Daily_Date")
    All_Dir = os.path.join(Current_Dir, "TWSE\All_Date")
    if not os.path.exists(TWSE_Dir):
        os.makedirs(TWSE_Dir)
    if not os.path.exists(Daily_Dir):
        os.makedirs(Daily_Dir)
    if not os.path.exists(All_Dir):
        os.makedirs(All_Dir)

    TradeDateList = GetTradeDateList(StartTime, EndTime)

    for idx, row in TradeDateList.iterrows():
        File_path = os.path.join(
            Daily_Dir, 'TWSE_Tick_' + row['Month'][:4]+row['Month'][5:-3]+row['Month'][8:]+'.txt')
        File_paths.append(File_path)

    frames = [pd.read_csv(f) for f in File_paths]
    df = pd.concat(frames, ignore_index=True)
    File_path = os.path.join(All_Dir, StartTime + '_' + EndTime + '.txt')
    df.to_csv(File_path, index=False)
    print 'TWSE_Tick_' + StartTime + '_' + EndTime + ' 整合完成....'


def main():
    StartYear = '2016'
    StartMonth = '06'
    StartDay = '13'
    EndYear = '2016'
    EndMonth = '06'
    EndDay = '17'
    StartDate = StartYear+StartMonth+StartDay
    EndDate = EndYear+EndMonth+EndDay
    MergeDataFrametoTXT(StartDate, EndDate)
    DataIntegration(StartDate, EndDate)


if __name__ == "__main__":
    main()
