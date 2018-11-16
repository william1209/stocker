import requests
from pyquery import PyQuery as pq
from util import conv_to_roc


def get_institutions_trading_daily(date):
    # get three major institutions trading: buy and sell separately.

    roc = conv_to_roc(date)
    # http://www.twse.com.tw/ch/trading/fund/BFI82U/BFI82U.php
    url = ('http://www.twse.com.tw/ch/trading/fund/BFI82U/BFI82U.php?' +
           'input_date={year}/{month}/{day}').format(
        year=roc.year,
        month=roc.month,
        day=roc.day)

    html = requests.get(url, headers=headers)
    html = html.content.decode('big5')

    pqd = pq(html)
    trs = pqd('tr.basic2[bgcolor="#FFFFFF"]')

    three_major = {}

    def get_data_title_text(dom):
        return pq(dom).find('div').eq(0).text()

    for i in trs:
        # after 2014/12/01, 自營商多了自行買賣與避險
        if get_data_title_text(i) == '自營商(自行買賣)':
            three_major['dealers_buy'] = pq(i).find('td').eq(1).text()
            three_major['dealers_sell'] = pq(i).find('td').eq(2).text()
        if get_data_title_text(i) == '投信':
            three_major['trustees_buy'] = pq(i).find('td').eq(1).text()
            three_major['trustees_sell'] = pq(i).find('td').eq(2).text()
        if get_data_title_text(i).startswith('外資'):
            three_major['fi_buy'] = pq(i).find('td').eq(1).text()
            three_major['fi_sell'] = pq(i).find('td').eq(2).text()

    for k, v in three_major.items():
        three_major[k] = int(v.replace(',', ''))

    assert len(three_major) == 6
    assert len(trs) == 5

    return three_major
