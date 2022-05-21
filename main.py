
import numpy as np
import pandas as pd

#读取数据
data_Amount = pd.read_csv('Amount.csv').set_index('Unnamed: 0')
data_Close = pd.read_csv('Close.csv').set_index('Unnamed: 0')
data_index = pd.read_csv('index.csv').set_index('Unnamed: 0')
#获得股票池
Amount_values = pd.DataFrame(data_Amount.values.T,index=data_Amount.columns,columns=data_Amount.index)
df = pd.DataFrame(columns=Amount_values.columns)
Close_values =  pd.DataFrame(data_Close.values.T,index=data_Close.columns,columns=data_Close.index)

pocket = []
for column in Amount_values.columns:
      pocket.append(Amount_values.sort_values(column).index[:300].tolist())

dates = data_Close.index.tolist()

df = pd.DataFrame(columns=data_Close.index)

close = []
for i in range(300):
    close.append(Close_values.loc[pocket[i]])

#资金库
total = 0
ret = pd.DataFrame(columns=Close_values.columns,index=Close_values.index)
case = ret.loc[pocket[0]]
case.iloc[:,0] = 1
rebalance = [300]
for i in range(1,300):
    # 平仓股票
    unchange = list(set(pocket[i - 1]).intersection(set(pocket[i])))
    change1 = list(set(pocket[i - 1]).difference(set(unchange)))
    w = (close[i-1].loc[change1].iloc[:, i] - close[i - 1].loc[change1].iloc[:, i - 1]) / close[i - 1].loc[change1].iloc[:, i - 1]

    case_change1 = case.loc[change1]
    case_change1.iloc[:,i] = case_change1.iloc[:,i-1] * (1+w)
    total = case_change1.loc[change1].sum()[i]
    mean = total/len(change1)

    #不变的股票
    unchange = list(set(pocket[i-1]).intersection(set(pocket[i])))
    w = (close[i].loc[unchange].iloc[:,i] - close[i-1].loc[unchange].iloc[:,i-1])/close[i-1].loc[unchange].iloc[:,i-1]

    case.drop(index=change1, inplace=True)
    case.iloc[:, i] = case.iloc[:, i - 1] * (1+w)

    #增加股票
    change2 = list(set(pocket[i]).difference(set(unchange)))
    case_change2 = ret.loc[change2]
    case_change2.iloc[:,i] = mean
    case = case.append(case_change2.loc[change2])
    rebalance.append(case.sum()[i])

#计算超额收益
price = pd.DataFrame(rebalance,index=Close_values.columns).apply(np.log)
ret = price - price.shift(1)
ret = pd.DataFrame(ret.values - data_index.values,index=Close_values.columns)
ret.fillna(0)
ret_log = ret.cumsum()
ret_log.fillna(0)


