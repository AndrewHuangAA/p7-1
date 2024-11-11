from django.shortcuts import render, redirect
from django.http import HttpResponse #匯入http模組
from datetime import datetime
import yfinance as yf
import pandas as pd
from django.http import JsonResponse
import time
import datetime
import numpy as np
import json
from collections import defaultdict
from django.contrib import messages
import copy

# def web(request):
#     if not request.user.is_authenticated:
#         messages.success(request, 'Sorry ! Please Log In.')
#         return redirect("http://127.0.0.1:8081/account/login")
#     return (render(request,"base.html"))

def hello_world(request):
    time = datetime.now()
    # return HttpResponse("Hello World!")
    return render(request, 'hello_world.html', locals())

def index(request):

    # df = pd.read_csv('data/hw1_output_ans.csv')
    # df = df.head(10)
    # df = df.rename(columns={"Gene_ID": "id",
    #                         "transcript_ID": "transcript",
    #                         "# of transcripts": "number",
    #                         })
    # json_string = df.to_json(orient='records')
    # genes = json.loads(json_string)
    if not request.user.is_authenticated:
        messages.success(request, 'Sorry ! Please Log In.')
        return redirect("http://127.0.0.1:8081/account/login")
    return render(request, 'index.html', locals())

def stock(stock_name, start_day, end_day):
    
    data_stock   = yf.download(stock_name, start_day, end_day)
    
    # 注意：yfinance 下载的数据中 Date 是索引，需要重置索引
    data_stock.reset_index(inplace=True)
    
    data_stock   = data_stock[['Date', 'Adj Close']]
    date_strings = data_stock['Date'].astype(str)
    date_list    = []
    
    for date_str in date_strings:
        timestamp = int(time.mktime(datetime.datetime.strptime(date_str, "%Y-%m-%d").timetuple())) * 1000
        date_list.append(timestamp)
    adj_close_list = data_stock['Adj Close'].tolist()
    combined_list  = [[date, adj_close] for date, adj_close in zip(date_list, adj_close_list)]

    # 列表 轉成 NumPy 数组
    combined_array = np.array(combined_list)

    data_stock     = combined_array.tolist()

    return data_stock

def load(stock_name, sub_stock_name, start_day, end_day):
    
    #圖一
    trading_signals = defaultdict(list)
    spread = None  
    rolling_mean = None
    rolling_std = None  
    upper_line = None
    lower_line = None
    upper_status = 0
    lower_status = 0
    close_prices = {}
    #圖二
    exe_trading_signals = None
    profit_loss_val = 0
    oper_value = 10000
    daily_profits = []
    total_values = []
    entry_point = []
    exit_point = []

    # -----------------------------------------------------------------------------------------第一張圖(三角)開始-----------------------------------------------------------------------------------------
    #下載數據
    data1 = yf.download(stock_name, start_day, end_day)
    data2 = yf.download(sub_stock_name, start_day, end_day)
    close_prices[stock_name] = data1['Adj Close']
    close_prices[sub_stock_name] = data2['Adj Close']
    
    # print('stock_name',stock_name)
    
    normalized_price1 = pd.Series(np.log(close_prices[stock_name]))
    normalized_price2 = pd.Series(np.log(close_prices[sub_stock_name]))  
    
    # 將兩組標準化後的數組相減並計算移動標準差與移動平均值
    spread = normalized_price1 - normalized_price2    #算出spread
    rolling_mean = spread.rolling(window=200).mean()
    rolling_std = spread.rolling(window=200).std() 
    upper_line = rolling_mean + 2 * rolling_std
    lower_line = rolling_mean - 2 * rolling_std

    trading_signals = defaultdict(list)
    for ind, val in enumerate(spread):
        
        if np.isnan(float(val)):
            continue
        
        date = spread.index[ind]
        target_spread = spread[ind]  
        
        adj_close_stock = close_prices[stock_name].loc[date]  # 主股票的调整后收盘价
        adj_close_sub_stock = close_prices[sub_stock_name].loc[date]  # 次股票的调整后收盘价

        
        if target_spread >= upper_line[ind] and (upper_status == 0):
            trading_signals[f'upper'].append([date, target_spread, 'SELL', "Open", adj_close_stock, adj_close_sub_stock])
            upper_status = 1

        if target_spread <= rolling_mean[ind] and (upper_status == 1):
            trading_signals[f'upper'].append([date, target_spread, 'BUY', "Close", adj_close_stock, adj_close_sub_stock])
            upper_status = 0


        if target_spread <= lower_line[ind] and (lower_status == 0):
            trading_signals[f'lower'].append([date, target_spread, 'BUY', "Open", adj_close_stock, adj_close_sub_stock])
            lower_status = 1

        if target_spread >= rolling_mean[ind] and (lower_status == 1):
            trading_signals[f'lower'].append([date, target_spread, 'SELL', "Close", adj_close_stock, adj_close_sub_stock])
            lower_status = 0

    # print('trading_signals:',trading_signals)
    # 轉成普通字典
    trading_signals_dict = dict(trading_signals)

    #去掉 defaultdict 和 np.float64()
    data = {
        key: [
            [
                int(values[0].timestamp()),  # 转换为时间戳
                float(values[1]) if isinstance(values[1], np.float64) else values[1],  # 检查并转换
                values[2],  # 直接获取 'SELL' 或 'BUY'
                values[3],  # 直接获取 'Open' 或 'Close'
                float(values[4]) if isinstance(values[4], np.float64) else values[4],  # 检查并转换
                float(values[5]) if isinstance(values[5], np.float64) else values[5]   # 检查并转换
            ]
            for values in trading_signals_dict[key]  # 遍历每个值列表
        ]
        for key in trading_signals_dict  # 遍历字典的每个键
    }
    
    for category in data:
        for entry in data[category]:
            entry[0] *= 1000
    
    
    upper = data['upper']
    lower = data['lower']
    


    stock_name_red       = [(item[0], item[4]) for item in upper if item[3] == 'Open' ] + [(item[0], item[4]) for item in lower if item[3] == 'Close']
    stock_name_green     = [(item[0], item[4]) for item in upper if item[3] == 'Close'] + [(item[0], item[4]) for item in lower if item[3] == 'Open' ]
    sub_stock_name_red   = [(item[0], item[5]) for item in upper if item[3] == 'Close'] + [(item[0], item[5]) for item in lower if item[3] == 'Open' ]
    sub_stock_name_green = [(item[0], item[5]) for item in upper if item[3] == 'Open' ] + [(item[0], item[5]) for item in lower if item[3] == 'Close']


    # print('data',data)
    # print(upper)
    # print(lower)
    # -----------------------------------------------------------------------------------------第一張圖(三角)結束-----------------------------------------------------------------------------------------
    
    # -----------------------------------------------------------------------------------------第二張圖(損益)開始-----------------------------------------------------------------------------------------
    
    # 計算實際交易日
    tmp_result = []
    unique_trades = set()
    for trade in [item for sublist in trading_signals.values() for item in sublist]:
        trade_tuple = tuple(trade[1:])
        if trade_tuple not in unique_trades:
            tmp_result.append(copy.deepcopy(trade))
            unique_trades.add(trade_tuple)
            
    exe_trading_signals = sorted(tmp_result, key=lambda x: x[0])
    
    for ele in exe_trading_signals:
        date = ele[0]
        next_date = close_prices[stock_name].index[close_prices[stock_name].index.get_loc(date) + 1]  
        ele[0] = next_date       
        
    #初始變量設定
    all_qty1 = 0
    all_qty2 = 0
    qty1 = 0
    qty2 = 0
    stock1_type = None
    stock2_type = None
    
    for ind, val in enumerate(close_prices[stock_name]):
        date = close_prices[stock_name].index[ind]
        price1 = close_prices[stock_name][ind]
        price2 = close_prices[sub_stock_name][ind]
        daily_profit = 0

        # 檢查是否有開倉信號
        matching_entry = list(filter(lambda x: x[0] == date and x[3] == 'Open', exe_trading_signals))
        if matching_entry:
            qty1 = (oper_value / 2) / price1
            qty2 = (oper_value / 2) / price2

            if stock1_type == "BUY" and stock2_type == "SELL":
                daily_profit = (all_qty1 * price1) - (all_qty2 * price2)
            elif stock1_type == "SELL" and stock2_type == "BUY":
                daily_profit = -(all_qty1 * price1) + (all_qty2 * price2)
            
            if matching_entry[0][2] == "BUY":
                entry_profit = -(qty1 * price1) + (qty2 * price2)
                stock1_type = "BUY"
                stock2_type = "SELL"
            elif matching_entry[0][2] == "SELL":
                entry_profit = (qty1 * price1) - (qty2 * price2)
                stock1_type = "SELL"
                stock2_type = "BUY"
            profit_loss_val += entry_profit

            all_qty1 += qty1
            all_qty2 += qty2
            
            # 計算當前總收益百分比
            entry_percentage = ((profit_loss_val+daily_profit) / oper_value) * 100
            entry_point.append((date, entry_percentage))
        
        # 檢查是否有平倉信號
        matching_exits = list(filter(lambda x: x[0] == date and x[3] == 'Close', exe_trading_signals))
        if matching_exits:
            if matching_exits[0][2] == "BUY":
                daily_profit = -(all_qty1 * price1) + (all_qty2 * price2)
            elif matching_exits[0][2] == "SELL":
                daily_profit = (all_qty1 * price1) - (all_qty2 * price2)
        
            profit_loss_val += daily_profit
            
            # 計算當前總收益百分比
            exit_percentage = (profit_loss_val / oper_value) * 100
            exit_point.append((date, exit_percentage))
            
            # initialize
            all_qty1 = 0
            all_qty2 = 0
            stock1_type = None
            stock2_type = None
            
        # 根據持有的倉位記錄每日的獲利
        if not matching_exits and not matching_entry:
            if stock1_type == "BUY" and stock2_type == "SELL":
                daily_profit = (all_qty1 * price1) - (all_qty2 * price2)
            elif stock1_type == "SELL" and stock2_type == "BUY":
                daily_profit = -(all_qty1 * price1) + (all_qty2 * price2)
            
            # 計算當前總收益百分比
            daily_percentage = ((profit_loss_val + daily_profit) / oper_value) * 100
            daily_profits.append((date, daily_percentage))

        # 記錄總值百分比
        total_percentage = (profit_loss_val / oper_value) * 100
        total_values.append((date, total_percentage))
        
    pl_daily_profits = [[int(date.timestamp() * 1000), val] for date, val in daily_profits]
    pl_total_values  = [[int(date.timestamp() * 1000), val] for date, val in total_values ]
    pl_entry_point   = [[int(date.timestamp() * 1000), val] for date, val in entry_point  ]
    pl_exit_point    = [[int(date.timestamp() * 1000), val] for date, val in exit_point   ]
    
    # -----------------------------------------------------------------------------------------第二張圖(損益)結束-------------------------------------------------------------------------------------------
    
    # -----------------------------------------------------------------------------------------第三張圖(布林帶)開始-----------------------------------------------------------------------------------------
    
    sorted_list        = sorted((trading_signals['upper'] + trading_signals['lower']), key=lambda x: x[0])
    spread             = spread.dropna()
    spread             = spread.reset_index()
    spread             = spread.values.tolist()
    spread             = [[int(date.timestamp() * 1000), val] for date, val in spread]
    middle_line        = rolling_mean.dropna()
    middle_line        = middle_line.reset_index()
    middle_line        = middle_line.values.tolist()
    middle_line        = [[int(date.timestamp() * 1000), val] for date, val in middle_line]
    upper_line         = upper_line.dropna()
    upper_line         = upper_line.reset_index()
    upper_line         = upper_line.values.tolist()
    upper_line         = [[int(date.timestamp() * 1000), val] for date, val in upper_line]
    lower_line         = lower_line.dropna()
    lower_line         = lower_line.reset_index()
    lower_line         = lower_line.values.tolist()
    lower_line         = [[int(date.timestamp() * 1000), val] for date, val in lower_line]
    bands_signals_sell = [[int(ele[0].timestamp() * 1000), ele[1]] for ele in sorted_list if ele[2]=='SELL']
    bands_signals_buy  = [[int(ele[0].timestamp() * 1000) , ele[1]] for ele in sorted_list if ele[2]=='BUY']
    
    # -----------------------------------------------------------------------------------------第三張圖(布林帶)結束-----------------------------------------------------------------------------------------
    
    # -----------------------------------------------------------------------------------------  DataTable1  開始-----------------------------------------------------------------------------------------
    
    # stock price data
    all_price = pd.DataFrame({
        'date': data1.index,
        stock_name: data1['Close'],
        sub_stock_name: data2['Close']
    })
    
    sorted_list = sorted((trading_signals['upper'] + trading_signals['lower']), key=lambda x: x[0])
    
    table_signals = []
    for row in sorted_list:
        stock1_price1 = round(all_price.loc[row[0].strftime("%Y-%m-%d"), stock_name], 2)
        stock2_price1 = round(all_price.loc[row[0].strftime("%Y-%m-%d"), sub_stock_name], 2)     
        if row[2]=="BUY":
            table_signals.append({"date":row[0], "stock_name_action": "BUY", "stock_name_price":stock1_price1, "sub_stock_name_action":"SELL", "sub_stock_name_price":stock2_price1, "type":row[3]})
        elif row[2]=="SELL":
            table_signals.append({"date":row[0].strftime("%Y-%m-%d"), "stock_name_action":"SELL", "stock_name_price":stock1_price1, "sub_stock_name_action":"BUY", "sub_stock_name_price":stock2_price1, "type":row[3]})

    # -----------------------------------------------------------------------------------------  DataTable1  結束-----------------------------------------------------------------------------------------
    
    # -----------------------------------------------------------------------------------------  DataTable2  開始-----------------------------------------------------------------------------------------
    
     
    exit_date = [ele[0] for ele in copy.deepcopy(exit_point)]    
    tmp_data = [item[1] for item in copy.deepcopy(total_values) if item[0] in exit_date]
    percentage = []
    # print(tmp_data)
    for i in range(0, len(tmp_data)):
        if i != 0:
            subtraction = tmp_data[i] - tmp_data[(i-1)]
        else:
            subtraction = tmp_data[i]
        percentage.append(round(subtraction,2))
    
    n=0
    exe_table_signals = []
    for row in exe_trading_signals:
        stock1_price1 = round(all_price.loc[row[0].strftime("%Y-%m-%d"), stock_name], 2)
        stock2_price1 = round(all_price.loc[row[0].strftime("%Y-%m-%d"), sub_stock_name], 2)     
        if row[2]=="BUY":
            if row[3] =="Open":
                exe_table_signals.append({"date":row[0].strftime("%Y-%m-%d"), "stock_name_action": "BUY", "stock_name_price":stock1_price1, "sub_stock_name_action":"SELL", "sub_stock_name_price":stock2_price1, "type":row[3], "percentage": None})
            else:
                exe_table_signals.append({"date":row[0].strftime("%Y-%m-%d"), "stock_name_action": "BUY", "stock_name_price":stock1_price1, "sub_stock_name_action":"SELL", "sub_stock_name_price":stock2_price1, "type":row[3], "percentage": percentage[n]})
                n+=1
        elif row[2]=="SELL":
            if row[3] =="Open":
                exe_table_signals.append({"date":row[0].strftime("%Y-%m-%d"), "stock_name_action":"SELL", "stock_name_price":stock1_price1, "sub_stock_name_action":"BUY", "sub_stock_name_price":stock2_price1, "type":row[3], "percentage": None})
            else:
                exe_table_signals.append({"date":row[0].strftime("%Y-%m-%d"), "stock_name_action": "BUY", "stock_name_price":stock1_price1, "sub_stock_name_action":"SELL", "sub_stock_name_price":stock2_price1, "type":row[3], "percentage": percentage[n]})
                n+=1
    
    return (stock_name_red, stock_name_green, sub_stock_name_red, sub_stock_name_green, 
            pl_daily_profits, pl_total_values, pl_entry_point, pl_exit_point, 
            spread, upper_line, middle_line, lower_line, bands_signals_sell, bands_signals_buy,
            table_signals, exe_table_signals)

def ajax_data(request):
    
    if request.method == 'POST':
        print(1)
        action = request.POST.get('action', '')
        print(2)
        if action == 'search_stock':
            print(3)
            try:
                stock_name     = request.POST.get('name'     , '' )
                sub_stock_name = request.POST.get('sub_name' , '' )
                start_day      = request.POST.get('start_day', '' )
                end_day        = request.POST.get('end_day'  , '' )
                
                '''
                原來不用API的method
                
                start_day = datetime.strptime(start_day, "%Y/%m/%d")
                # 将 datetime 对象转换为新的字符串格式
                start_day = start_day.strftime("%Y-%m-%d")
                
                end_day = datetime.strptime(end_day, "%Y/%m/%d")
                # 将 datetime 对象转换为新的字符串格式
                end_day = end_day.strftime("%Y-%m-%d")
                
                print(start_day)
                print(end_day)
                
                message = stock(stock_name, start_day, end_day)
                sub_message = stock(sub_stock_name, start_day, end_day)
                # message = stock(stock_name)
                # sub_message = stock(sub_stock_name)
                
                (
                stock_name_red, stock_name_green, sub_stock_name_red, sub_stock_name_green, 
                pl_daily_profits, pl_total_values, pl_entry_point, pl_exit_point, 
                spread, upper_line, middle_line, lower_line, bands_signals_sell, bands_signals_buy,
                table_signals,exe_table_signals
                ) = load(stock_name, sub_stock_name, start_day, end_day)    
                
                response = {
                    'data_stock'          : [message,sub_message]       ,
                    'stock_name'          : [stock_name,sub_stock_name] ,
                    'stock_name_red'      : stock_name_red              ,
                    'stock_name_green'    : stock_name_green            ,
                    'sub_stock_name_red'  : sub_stock_name_red          ,
                    'sub_stock_name_green': sub_stock_name_green        ,
                    'pl_daily_profits'    : pl_daily_profits            ,
                    'pl_total_values'     : pl_total_values             ,
                    'pl_entry_point'      : pl_entry_point              ,
                    'pl_exit_point'       : pl_exit_point               ,
                    'spread'              : spread                      ,
                    'middle_line'         : middle_line                 ,
                    'upper_line'          : upper_line                  ,
                    'lower_line'          : lower_line                  ,
                    'bands_signals_sell'  : bands_signals_sell          ,
                    'bands_signals_buy'   : bands_signals_buy           ,
                    'table_signals'       : table_signals               ,
                    'exe_table_signals'   : exe_table_signals           ,
                }
                '''
                
                # ------ API ------
                # Communicate with function api
                from common.func_client import FuncClient
                
                #实例化 FuncClient 对象，赋值给 fc,fc 实例将用于调用 FuncClient 中的方法
                fc = FuncClient()
                
                #包含配对交易回测所需参数的字典
                params = {
                    'stock_name' : str(stock_name),
                    'sub_stock_name' : str(sub_stock_name),
                    'start_day' : str(start_day),
                    'end_day' : str(end_day),
                    # 'window_size' : int(window_sizes),
                    # 'n_times' : int(std)
                }
                
                #通过 fc 对象调用 pairtrading_backtesting 方法，并传入 params 字典作为参数，指定 method 为 "distance"。pairtrading_backtesting 执行配对交易的回测逻辑，并返回结果 res。
                res = fc.pairtrading_backtesting(params=params, method="distance")
                
                response = {
                    'data_stock'          : [res['message'],res['sub_message']],
                    'stock_name'          : [stock_name,sub_stock_name]        ,
                    'stock_name_red'      : res['stock_name_red']              ,
                    'stock_name_green'    : res['stock_name_green']            ,
                    'sub_stock_name_red'  : res['sub_stock_name_red']          ,
                    'sub_stock_name_green': res['sub_stock_name_green']        ,
                    'pl_daily_profits'    : res['pl_daily_profits']            ,
                    'pl_total_values'     : res['pl_total_values']             ,
                    'pl_entry_point'      : res['pl_entry_point']              ,
                    'pl_exit_point'       : res['pl_exit_point']               ,
                    'spread'              : res['spread']                      ,
                    'middle_line'         : res['middle_line']                 ,
                    'upper_line'          : res['upper_line']                  ,
                    'lower_line'          : res['lower_line']                  ,
                    'bands_signals_sell'  : res['bands_signals_sell']          ,
                    'bands_signals_buy'   : res['bands_signals_buy']           ,
                    'table_signals'       : res['table_signals']               ,
                    'exe_table_signals'   : res['exe_table_signals']           ,
                }
                                
                return JsonResponse(response, safe=False)            
            except:
                message = 'Something wrong, please check again.'
                return JsonResponse(message, safe=False)
        else:
            return JsonResponse({'message': 'Invalid action.'})
        
    return JsonResponse({'message': 'Invalid request method.'})


