import base64
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import collections
from eunjeon import Mecab
from wordcloud import WordCloud
from IPython.display import set_matplotlib_formats

matplotlib.rc('font',family = 'Malgun Gothic')
matplotlib.rc('axes', unicode_minus=False)
set_matplotlib_formats('retina')

def node_encode(x):
    result = x
    result = str(x)
    print(base64.b64encode(result.encode('utf-8')))

def run():
    # 데이터 로드
    data = pd.read_csv('instagram.csv')

    data = data.dropna()
    data.index = range(len(data))

    # 데이터 전처리
    text = ''
    for i in range(len(data)):
        text = text + data.iloc[i]

    tagger = Mecab()

    words = tagger.morphs(text[0].replace('따릉이', ''))
    morphs = tagger.pos(text[0].replace('따릉이', ''))

    words_list = []  # NNP, NNG, SL
    for word, tag in morphs:
        if((tag in 'NNP') | (tag in 'NNG') | (tag in 'SL')):
            words_list.append(word)

    count = collections.Counter(words_list)

    count['라이딩'] = count['라이']
    del count['그램'], count['스타'], count['라이'], count['딩']
    del count['반사'], count['소통'], count['데일리']

    # 워드클라우드
    wordcloud = WordCloud(font_path='C:/Windows/Fonts/malgun.ttf', background_color='white',
                      colormap="Accent_r", width=1500, height=1000).generate_from_frequencies(count)
    fig1 = plt.figure(figsize=(20, 16))
    plt.imshow(wordcloud)
    plt.axis('off')
    # plt.show()

    fig1.savefig('./data/img/wordcloud.png')


    places = ['뚝섬', '여의도', '반포', '중랑천', '서울숲',' 마곡', '안양천', '잠원', '남산', '도림천', '잠수교', '마포',
        '마포대교', '양화대교', '노들섬', '강남', '영동대교', '면목', '상암', '반포대교', '동호대교', '성수대교', '청담대교',
        '연남동', '탄천', '불광천', '청계천', '사당', '잠실대교', '홍대', '한강대교', '압구정', '경복궁', '원효대교',
        '여의나루', '고대', '명동', ' 성산대교', '마포구', '왕십리', '용산', '노원', '삼성동', '양재천', '우이천', '오목교',
        '가양대교', '송파', '강변', '노들', '신촌', '방이동', '건대', '석촌', '망원동', '독립', '한남동', '이촌동', '상도동']

    hot_place = {}
    for key, value in dict(count.most_common()).items():
        if key in places:
            hot_place[key] = value

    hot_place = sorted(hot_place.items(), key=(lambda x : x[1]), reverse=True)

    top_10 = []
    for i, key in enumerate(hot_place):
        node_encode('%d.'%(i+1), key[0])
        top_10.append(key[0])
        if(i+1 == 10):
            break

    # df = pd.DataFrame(top_10, columns=['따릉이 핫플레이스'])
    # df.to_csv('따릉이 명소.csv', index=False)



if __name__ == '__main__':
    run()
