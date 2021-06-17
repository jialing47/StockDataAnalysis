import pandas as pd
import matplotlib.pyplot as plt
from pandas.core.tools import numeric

#計算KD線
'''
Step1:計算RSV:(今日收盤價-最近9天的最低價)/(最近9天的最高價-最近9天的最低價)
Step2:計算K: K = 2/3 X (昨日K值) + 1/3 X (今日RSV)
Step3:計算D: D = 2/3 X (昨日D值) + 1/3 X (今日K值)
'''
def KD(data):
    data_df = data.copy()
    data_df['min'] = data_df['最低價'].rolling(9).min()
    data_df['max'] = data_df['最高價'].rolling(9).max()
    data_df['RSV'] = (data_df['收盤價'] - data_df['min'])*100/(data_df['max'] - data_df['min'])
    data_df = data_df.dropna()
    # 計算K
    # K的初始值定為50
    K_list = [50]
    for num,rsv in enumerate(list(data_df['RSV'])):
        K_yestarday = K_list[num]
        K_today = 2/3 * K_yestarday + 1/3 * rsv
        K_list.append(K_today)
    data_df['K'] = K_list[1:]
    # 計算D
    # D的初始值定為50
    D_list = [50]
    for num,K in enumerate(list(data_df['K'])):
        D_yestarday = D_list[num]
        D_today = 2/3 * D_yestarday + 1/3 * K
        D_list.append(D_today)
    data_df['D'] = D_list[1:]
    use_df = pd.merge(data,data_df[['K','D']],left_index=True,right_index=True,how='left')
    return use_df

data = pd.read_csv('D:/StockDataAnalysis/stockdata/Stocks.csv')
df = pd.DataFrame(data)
df['日期'] =pd.to_datetime(df['日期'],format='%Y/%m/%d')
df.set_index(df['日期'],inplace=True)
df['開盤價'] = df['開盤價'].str.replace('--', '')
df['最高價'] = df['最高價'].str.replace('--', '')
df['最低價'] = df['最低價'].str.replace('--', '')
df['收盤價'] = df['收盤價'].str.replace('--', '')
df['開盤價'] = pd.to_numeric(df['開盤價'])
df['最高價'] = pd.to_numeric(df['最高價'])
df['最低價'] = pd.to_numeric(df['最低價'])
df['收盤價'] = pd.to_numeric(df['收盤價'])
#df = KD(df)     <----KD函式如果放在這裡，method後同日會有三種不同的KD值

stocknum = eval(input("請輸入股票代號："))    #int
df = df[df['股票代號'] == stocknum]    #篩選資料

date = input("請輸入日期(例：2016-01-04)：")    #str
method = eval(input("單日資訊請輸入：1  設定開始日期輸出折現圖請輸入：2 \n您想要："))
if method == 1:
    df = KD(df)
    df = df[df['日期'] == date]
    print("股票代號%d 於 %s資訊：" %(stocknum, date))
    print("成交股數 = %d" %df.iloc[0]['成交股數'])
    print("成交金額 = %d" %df.iloc[0]['成交金額'])
    print("開盤價 = %f" %df.iloc[0]['開盤價'])
    print("最高價 = %f" %df.iloc[0]['最高價'])
    print("最低價 = %f" %df.iloc[0]['最低價'])
    print("K = %f" %df.iloc[0]['K'])
    print("D = %f" %df.iloc[0]['D'])



elif method == 2:
    df = KD(df)
    df = df[df['日期'] >= date]
    print(df)   
    #繪圖
    plt.figure(1)
    df['K'].plot(figsize=(16, 8), label='K')
    df['D'].plot(figsize=(16, 8), label='D')
    plt.legend(loc='upper right', shadow=True, fontsize='x-large')
    plt.title('KD_modify')
    plt.show()

    plt.figure(2)
    df['收盤價'].plot()
    plt.title('stockprice')
    plt.show()
     
else:
    print("系統尚未新增其他功能")