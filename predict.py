import sys
import base64
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
# from IPython.display import clear_output
from IPython.display import set_matplotlib_formats
from sklearn.metrics.pairwise import euclidean_distances
import tensorflow as tf
from tensorflow.keras.utils import to_categorical
from tensorflow.keras import  Model

matplotlib.rc('font',family = 'Malgun Gothic')
matplotlib.rc('axes', unicode_minus=False)
set_matplotlib_formats('retina')


data = pd.read_csv('./data/서울특별시 공공자전거 대여정보_2018_2019.csv', engine='python')
columns = data.columns.values
columns[0] = '대여소번호'
data.columns = list(columns)

date = data.copy()
for i in range(1, len(date.columns)):
    if((date.columns[i][5:7] == '03') | (date.columns[i][5:7] == '04') | (date.columns[i][5:7] == '05')):
        date[[date.columns[i]]] = 0
    elif((date.columns[i][5:7] == '06') | (date.columns[i][5:7] == '07') | (date.columns[i][5:7] == '08')):
        date[[date.columns[i]]] = 1
    elif((date.columns[i][5:7] == '09') | (date.columns[i][5:7] == '10') | (date.columns[i][5:7] == '11')):
        date[[date.columns[i]]] = 2
    elif((date.columns[i][5:7] == '12') | (date.columns[i][5:7] == '01') | (date.columns[i][5:7] == '02')):
        date[[date.columns[i]]] = 3
    else:
        print('error')


model = tf.keras.models.load_model('./model/lstm_seasonal_model.h5')

df = pd.read_csv('./data/서울특별시 공공자전거 대여소 정보_20191209_csv.csv', engine='python')
df = df.dropna(axis=0)
df = df[['대여소ID', '대여소명', '대여소주소', '위도', '경도']]
df['대여소ID'] = df['대여소ID'].astype('object')

def get_incode(x):
    if(x == 0):
        return np.array((1, 0, 0, 0)).reshape(1, 4, 1)
    if(x == 1):
        return np.array((0, 1, 0, 0)).reshape(1, 4, 1)
    if(x == 2):
        return np.array((0, 0, 1, 0)).reshape(1, 4, 1)
    if(x == 3):
        return np.array((0, 0, 0, 1)).reshape(1, 4, 1)

def node_encode(x):
    result = x
    result = str(x)
    print(base64.b64encode(result.encode('utf-8')))

def run():
#     key = int(sys.argv[1])
    key = int(sys.argv[1])

    name = df[df['대여소ID'] == key]['대여소명'].values[0]
    address = df[df['대여소ID'] == key]['대여소주소'].values[0]
    node_encode(name.split('.')[1].lstrip() if '.' in name else name)
    node_encode('주소 -'+ address)

    new_X = data[data['대여소번호'] == str(key)].iloc[0, -30:].values.reshape(1, 1, 30).astype('float64')
    new_date = date[date['대여소번호'] == str(key)].iloc[0, -30:].values
    new_date = np.concatenate(list(map(get_incode, new_date)), axis=-1)
    new_X = np.concatenate([new_X, new_date], axis=1)

    for i in range(367):
        pred = round(model.predict(new_X[:, :, -30:])[0, 0, -1])
        if((i >= 0) & (i < 91)):
            pred = np.concatenate([pred.reshape(1, 1, 1), get_incode(3)], axis=1)
        elif((i >= 91) & (i < 183)):
            pred = np.concatenate([pred.reshape(1, 1, 1), get_incode(0)], axis=1)
        elif((i >= 183) & (i < 275)):
            pred = np.concatenate([pred.reshape(1, 1, 1), get_incode(1)], axis=1)
        else:
            pred = np.concatenate([pred.reshape(1, 1, 1), get_incode(2)], axis=1)
        new_X = np.concatenate([new_X, pred], axis=-1)


    distances = euclidean_distances(df[df['대여소ID'] == key][['위도', '경도']], df[df['대여소ID'] != key][['위도', '경도']])
    distances = distances.reshape(-1)
    id_num = df[df['대여소ID'] != key]['대여소ID'].values
    id_name = df[df['대여소ID'] != key]['대여소명'].values
    id_address = df[df['대여소ID'] != key]['대여소주소'].values

    node_encode('가까운 대여소')
    for i in range(5):
        node_encode(str(i+1) + ':' + id_name[np.argsort(distances)[i]].split('.')[1].lstrip() \
              if '.' in id_name[np.argsort(distances)[i]] else id_name[np.argsort(distances)[i]])
        node_encode('ID -'+ str(int(id_num[np.argsort(distances)[i]])))
        node_encode('주소 -'+ id_address[np.argsort(distances)[i]])
        node_encode('일주일 평균 대여량 -'+
                  str(int(data[data['대여소번호'] == str(int(id_num[np.argsort(distances)[i]]))].iloc[:, -7:].mean(axis=1).values[0])))


    total = np.r_[data[data['대여소번호'] == '1001'].iloc[0, 1:-30].values, new_X[0, 0, :62]]
    ticks = [columns[i] for i in np.arange(1, len(columns), 30)] + ['2019-12-23']

    fig1 = plt.figure(figsize=(10, 8));
    # plt.plot(total);
    plt.plot(np.arange(0, len(total[:-30])), total[:-30], color='b');
    plt.plot(np.arange(len(total[:-30]), len(total)), total[-30:], color='r')
    plt.xticks(np.arange(0, len(total), 30), ticks, rotation=45);
    plt.title('추후 30일간 대여횟수 예측')
    plt.xlabel('날짜');
    plt.ylabel('대여횟수');
    fig1.savefig('./data/img/predict.png');


if __name__ == '__main__':
    run()
