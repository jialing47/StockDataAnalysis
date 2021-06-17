import gspread
from oauth2client.service_account import ServiceAccountCredentials
from bs4 import BeautifulSoup
import requests
from openpyxl.styles import Font
from requests.models import codes
import time
import io
import csv
import re
import random
import datetime


class Stock:
    def __init__(self, *stock_numbers):
        self.stock_numbers = stock_numbers

    def scrape(self):
        result = list()
        for stock_number in self.stock_numbers:

            response = requests.get(
                "https://tw.stock.yahoo.com/q/q?s=" + stock_number)
            soup = BeautifulSoup(response.text.replace("加到投資組合", ""), "lxml")

            stock_date = soup.find(
                "font", {"class": "tt"}).getText().strip()[-9:]  # 資料日期

            tables = soup.find_all("table")[2]  # 取得網頁中第三個表格
            tds = tables.find_all("td")[0:11]  # 取得表格中1到10格

            result.append((stock_date,) +
                          tuple(td.getText().strip() for td in tds))

        return result

    def gsheet(self, stocks, sheetname):
        scopes = ["https://spreadsheets.google.com/feeds"]

        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            "credentials.json", scopes)

        client = gspread.authorize(credentials)

        # sheet = client.open_by_key(
        #     "1dJBqrpvFdhT5o_MoYOBgPHwnx0bfFyPBOUfQbsID9nA").sheet1

        sheet = client.open_by_key(
            "1dJBqrpvFdhT5o_MoYOBgPHwnx0bfFyPBOUfQbsID9nA").worksheet(sheetname)
        # titles = ('股票代號', '日期', '成交股數', '成交金額', '開盤價', '最高價', '最低價', '收盤價')
        # sheet.append_row(titles, 1)
        for stock in stocks:
            print(stock)
            time.sleep(0.5)
            sheet.append_row(stock)

    def history(self, year, month):
        result = list()
        for code in self.stock_numbers:
            date = f'{year}{month:02}01'
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
            resp = requests.get(
                f'https://www.twse.com.tw/exchangeReport/STOCK_DAY?' +
                f'response=csv&date={date}&stockNo={code}', headers=headers)
            # 取出 CSV 內容，並去除第一行及最後 5 行
            lines = io.StringIO(resp.text).readlines()
            lines = lines[1:-5]
            # 透過 CSV 讀取器載入
            reader = csv.DictReader(io.StringIO('\n'.join(lines)))
            # 依序取出每筆資料行
            for row in reader:
                # 取出日期欄位值
                date = row['日期'].strip()
                parts = date.split('/')
                date = str(datetime.date(
                    int(parts[0]) + 1911, int(parts[1]), int(parts[2])))
                # 取出成交股數欄位值
                totalShare = row['成交股數'].replace(',', '').strip()
                # 取出成交金額欄位值
                totalTurnover = row['成交金額'].replace(',', '').strip()
                # 取出開盤價欄位值
                openPrice = row['開盤價']
                # 取出最高價欄位值
                highestPrice = row['最高價']
                # 取出最低價欄位值
                lowestPrice = row['最低價']
                # 取出收盤價欄位值
                closePrice = row['收盤價']

                values = (code, date, totalShare, totalTurnover,
                          openPrice, highestPrice, lowestPrice, closePrice)
                result.append(values)
        return result


def today():
    scopes = ["https://spreadsheets.google.com/feeds"]

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json", scopes)

    client = gspread.authorize(credentials)
    sheet = client.open_by_key(
        "1dJBqrpvFdhT5o_MoYOBgPHwnx0bfFyPBOUfQbsID9nA").worksheet('今日資料')
    resp = requests.get(
        f'https://www.twse.com.tw/exchangeReport/MI_INDEX?' +
        f'response=json&' +
        f'type=ALLBUT0999' +
        f'&date={datetime.date.today():%Y%m%d}'
    )
    body = resp.json()
    records = body['data9']
    result = list()
    for record in records:
        code = record[0].strip()
        if re.match(r'^[1-9][0-9][0-9][0-9]$', code) is not None:
            # name = record[1].strip()
            totalShare = record[2].replace(',', '').strip()
            totalTurnover = record[4].replace(',', '').strip()
            openPrice = record[5].replace(',', '').strip()
            highestPrice = record[6].replace(',', '').strip()
            lowestPrice = record[7].replace(',', '').strip()
            closePrice = record[8].replace(',', '').strip()
            values = (code, str(datetime.date.today()), totalShare, totalTurnover,
                      openPrice, highestPrice, lowestPrice, closePrice)
            result.append(values)
            time.sleep(1)
            sheet.append_row(values)
            print(values)


def writePastFiveYears(code):
    for year in range(2016, 2021):
        for month in range(1, 13):
            stock = Stock(code)
            s = random.randrange(5, 10)
            print(s)
            print(year, month)
            stock.gsheet(stock.history(year, month), '歷史資料1')
            time.sleep(1)


def writeThisYears(code):
    year = 2021
    for month in range(1, 7):
        stock = Stock(code)
        print(year, month)
        stock.gsheet(stock.history(year, month), '歷史資料2')
        time.sleep(1)


if __name__ == '__main__':
    # file = open('stockCode.txt')
    # today()
    # writePastFiveYears('1104')
    # writeThisYears('1104')
    writeThisYears('1108')
