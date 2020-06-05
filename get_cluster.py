import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from IPython.display import set_matplotlib_formats

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
set_matplotlib_formats('retina')


def run():
    # 데이터 로드
    data1 = pd.read_csv('./data/도로교통공단 교통사고다발지역_20191010.csv', engine='python')
    data2 = pd.read_csv('./data/서울특별시 공공자전거 대여소 정보_20191209_csv.csv', engine='python')
    data3 = pd.read_csv('./data/서울형 지도태깅 자전거 편의시설 정보.csv', engine='python')
    data4 = pd.read_csv('./data/자전거 이용률 통계.txt', sep='\t')
    data5 = pd.read_csv('./data/자전거 도로 현황 통계.txt', sep='\t')

    print('data loading: OK')

    # 데이터 전처리
    data1_sub = data1[(data1['사고년도'] == 2018) & (data1['사고유형구분'] == '자전거')]
    data1_sub.index = range(len(data1_sub))
    
    idx = []

    for i, sido in enumerate(data1_sub['시도시군구명']):
        if '서울특별시' in sido:
            idx.append(i)

    data1_sub = data1_sub.loc[idx]
    data1_sub['구명'] = data1_sub['시도시군구명'].map(lambda x : x.split(' ')[1].rstrip('0123456789'))

    gu_accident = data1_sub.groupby('구명')['발생건수'].sum()
    gu_rental = data2.groupby('대여소_구')['대여소_구'].count()

    data2['거치대수'] = data2['거치대수'].map(lambda x : x.replace(',', ''))
    data2['거치대수'] = data2['거치대수'].astype('int')

    gu_num_bicycle = data2.groupby('대여소_구')['거치대수'].sum()
    gu_num_conv = data3.groupby('구명')['구명'].count()
    gu_rental = gu_rental[:-1]
    gu_num_bicycle = gu_num_bicycle[:-1]

    total = data4.loc[28:52, ['분류', '이동 수단으로 이용', '운동 수단으로 이용']]

    data5_sub = data5.loc[3:27, ['자치구(2)', '합계.1']]
    data5_sub.columns = ['분류', '전용도로길이']

    total = pd.merge(total, data5_sub, how='left', on='분류')
    total = total.rename(columns={'분류': '구명'})
    total = pd.merge(total, gu_accident.reset_index(), how='left', on='구명').fillna(0)

    temp = pd.DataFrame([gu_rental, gu_num_bicycle, gu_num_conv]).T
    temp.columns = ['대여소수', '자전거수', '편의시설수']
    temp['구명'] = temp.index

    total = pd.merge(total, temp, how='left', on='구명').fillna(0)
    total['발생건수'] = total['발생건수'].astype('int')

    print('data processing: OK')

    # PCA
    scaler = StandardScaler()
    total_std = scaler.fit_transform(total.iloc[:, 1:])

    pca = PCA(n_components=2)
    total_pca = pca.fit_transform(total_std)

    # 군집
    kmeans = KMeans(n_clusters=4, random_state=42)
    kmeans.fit(total_std)

    df_pca = pd.DataFrame(total_pca)
    df_pca.columns = ['PC1', 'PC2']
    df_pca['cluster'] = kmeans.predict(total_std)

    fig1 = plt.figure(figsize=(16, 10))
    sns.scatterplot('PC1', 'PC2', hue='cluster', data=df_pca, palette=sns.xkcd_palette(['windows blue', 'amber', 'faded green', 'dusty purple']));
    for i in range(0, len(total_pca)):
        plt.text(total_pca[i, 0], total_pca[i, 1], s=total['구명'][i]);

    plt.vlines(0, -3, 4, colors='r')
    plt.hlines(0, -3, 6, colors='r')
    plt.xlabel('PC1');
    plt.ylabel('PC2');

    fig1.savefig('cluster.png')

    print('save figure: OK')

if __name__ == '__main__':
    run()
