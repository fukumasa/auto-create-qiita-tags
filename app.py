import sys
import collections
import dbm
from janome.tokenizer import Tokenizer
import termextract.janome
import termextract.core
import requests
from bs4 import BeautifulSoup
import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)

# termextractが抽出した専門用語情報を格納
ai_dict = {}

# タグ情報を格納するDB
db_name = "./database/tags.db"



"""
Qiitaの記事からタグを自動生成する
"""
def createTags(text):
    # Qiitaの記事から専門用語を抽出
    t = Tokenizer()
    tokenize_text = t.tokenize(text)
    frequency = termextract.janome.cmp_noun_dict(tokenize_text)
    lr = termextract.core.score_lr(
        frequency,
        ignore_words=termextract.janome.IGNORE_WORDS,
        lr_mode=1, average_rate=1)
    data = termextract.core.term_importance(frequency, lr)
    data_collection = collections.Counter(data)

    # Qiitaのタグ情報を格納したDBに接続
    sql = 'SELECT * FROM tags WHERE id=?'
    con = sqlite3.connect(db_name)
    cursor = con.cursor()

    sum_followers = 0
    sum_value = 0
    count = 1
    dict_auto = []

    # 抽出した専門用語からQiita登録済みタグを抽出
    print("■自動生成したタグ情報")
    print("タグ名", "フォロワー数", "重要度", sep="\t")
    for cmp_noun, value in data_collection.most_common():
        word = termextract.core.modify_agglutinative_lang(cmp_noun)
        ai_dict[word] = value

        # 抽出するタグ情報は上位5つまで
        if count <= 5:
            rows = cursor.execute(sql,(word,))
            res = cursor.fetchone()

            if res:
                print(res[0], res[1], value, sep="\t")
                sum_followers += int(res[1])
                sum_value += value
                obj = {}
                obj["id"] = res[0]
                obj["count"] = int(res[1])
                obj["value"] = value
                dict_auto.append(obj)
                count += 1
    print("***SUM(VALUES) : " + str(sum_value))
    print("***SUM(FOLLOWERS) : " + str(sum_followers))
    obj = {}
    obj["id"] = "合計"
    obj["count"] = sum_followers
    obj["value"] = sum_value
    dict_auto.append(obj)
    
    return dict_auto


"""
Qiitaの記事から内容を抽出する
"""
def extractText(url):
    text = ""

    r = requests.get(url) 
    soup = BeautifulSoup(r.text, "lxml")

    #記事内容を抽出（コードは除去）
    for tag in soup.find_all("div",{"class":"code-frame"}):
        tag.decompose()
    for tag in soup.find_all('section'):
        text += tag.getText()

    return text


"""
Qiitaの記事から現在登録されているタグを抽出する
"""
def extractTags(url):
    r = requests.get(url) 
    soup = BeautifulSoup(r.text, "lxml")

    # Qiitaのタグ情報を格納したDBに接続
    sql = 'SELECT * FROM tags WHERE id=?'    
    con = sqlite3.connect(db_name)
    cursor = con.cursor()

    sum_follower_now = 0
    sum_value_now = 0
    dict = []

    print("■現在登録されているタグ情報")
    print("タグ名", "フォロワー数", "重要度", sep="\t")
    for keyword in soup.find("meta", attrs={"name":"keywords"}).get("content").split(","):
        rows = cursor.execute(sql,(keyword,))
        res = cursor.fetchone()

        count = int(res[1]) if res else 0
        value = ai_dict[keyword] if keyword in ai_dict else 0
        print(keyword, count, value, sep="\t")
        sum_follower_now += count
        sum_value_now += value
        obj = {}
        obj["id"] = keyword
        obj["value"] = value
        obj["count"] = count
        dict.append(obj)

    print("***SUM(VALUES) : " + str(sum_value_now))
    print("***SUM(FOLLOWERS) : " + str(sum_follower_now))
    obj = {}
    obj["id"] = "合計"
    obj["value"] = sum_value_now
    obj["count"] = sum_follower_now
    dict.append(obj)

    return dict


"""
画面を表示する
"""
@app.route('/', methods=['GET', 'POST'])
def showApp():
    url = ''
    if request.method == 'POST':
        url = request.form['url']
    elif request.method == 'GET':
        return render_template('index.html', title='Qiitaタグ自動生成')

    text = extractText(url)
    dict_auto = createTags(text)
    print("------------------------------------")
    dict = extractTags(url)
    return render_template('index.html', title='Qiitaタグ自動生成', items=dict, items2=dict_auto)


"""
メイン
"""
if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)  
