import streamlit as st
import pandas as pd
from PIL import Image
import random
import urllib.request
import msgpack
import io
import json

num_top = 3
labels = ['redpoint_-3','redpoint_-2','redpoint_-1','redpoint_0',
              'redpoint_1','redpoint_2','redpoint_3']

label_text = ['黄色3点以上','黄色2点','黄色1点','ドロー',
            '赤1点','赤2点','赤3点以上']

random.sample(labels,3)

class predictor():
    def __init__(self) -> None:
        pass

    def pred(self,image,ends,red_diff,last_stone_is_red):
        print(type(image),type(ends),type(red_diff),type(last_stone_is_red))
        remain_ends = 8-ends
        if remain_ends < 0:
            remain_ends = 0
        data = {
            "remain_ends":remain_ends,
            "last_stone_is_red":last_stone_is_red,
            "red_postion":red_diff,
        }
        ## 画像はストリームに変換して送る
        buffer = io.BytesIO()
        image.save(buffer, format="PNG") 
        data['img'] = buffer.getvalue()
        payload = msgpack.packb(data, use_bin_type=True)

        headers = {
            "Content-Type": "application/x-msgpack",
        }
        url = "https://subjet2024-api.onrender.com/predict"
        ##url = "http://127.0.0.1:8000/predict"
        req = urllib.request.Request( url, payload, headers)
        with urllib.request.urlopen(req) as res:
            response = json.load(res)
            print(response)
        ## sample
        ##[{'class': 2, 'acc': 0.3981827199459076}, {'class': 1, 'acc': 0.24624960124492645}, {'class': 4, 'acc': 0.19462589919567108}]
        return response
    
def scale_to_height(img, height):
    width = round(img.width * height / img.height)
    return img.resize((width, height))

def main():
    
    labelDf = pd.DataFrame([ labels , label_text]).T
    labelDf.columns = ['label','text']
    curPredictor = predictor()

    st.title('カーリングのエンド得点を予測')

    st.sidebar.title("概要")
    st.sidebar.write("画像認識モデルを使ってエンド最終投で")
    st.sidebar.write("獲得される得点を予測します。")
    st.sidebar.write("分類モデルでラベルは以下になります。")
    st.sidebar.table(labelDf['text'])
        
    st.sidebar.write("")

    #img_source = st.sidebar.radio("画像のソースを選択してください",
    #                              ("画像をアップロード","サンプルを選択"))
    img_source = "画像をアップロード"
    if img_source == "画像をアップロード":
        img_file = st.sidebar.file_uploader("画像を選択してください。", type=["png"])
    if img_source == "サンプルを選択":
        img_file = None
        st.sidebar.write("TBD")

    if img_file is not None:
        left_column, right_column = st.columns(2)
        with left_column:
            img = Image.open(img_file)
            displayimg = scale_to_height(img,200)
            st.image(displayimg, caption="対象画像")
        with right_column:
            ends = st.number_input('エンド数は?',min_value=1,max_value=8,value=1)
            red_diff = st.slider('赤チームは黄色チームと何点差ですか?',min_value=-5,max_value=5,value=0)
            last_stone_is_red = st.checkbox('赤色チームが最後の一投ですか?', value=False, help=None, on_change=None)
            pass
        st.write("")
        isExecute = st.button('予測')
        if isExecute :
            with st.spinner('Wait for it...'):
                results = curPredictor.pred(img,ends,red_diff,last_stone_is_red)
                
                st.subheader("判定結果")
                for result in results[:num_top]:
                    n =  result['class']
                    acc = result['acc']
                    display = label_text[n]
                    st.write(str(round(acc * 100, 2)) + "%の確率で" + display + "です。")

if __name__ == "__main__":
    main()
