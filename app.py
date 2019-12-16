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

# タグ情報を格納するDB
db_name = "./database/tags.db"


'''
Qiitaの記事からタグを自動生成する
'''
def createTags(text):
    all_tags = []

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
    
    # 抽出した専門用語を1つずつ取得
    for cmp_noun, value in data_collection.most_common():
        word = termextract.core.modify_agglutinative_lang(cmp_noun).lower()
        
        # Qiitaに登録済みのタグか確認
        rows = cursor.execute(sql,(word,))
        res = cursor.fetchone()

        # Qiitaに登録済みのタグのみに絞る
        if res:
            print(word)
            tag = {}
            tag['name'] = word
            tag['value'] = value
            tag['followers'] = res[1]
            tag['counts'] = res[2]
            all_tags.append(tag)

    return all_tags


'''
Qiitaの記事から内容を抽出する
'''
def extractText(url):
    text = ''

    r = requests.get(url) 
    soup = BeautifulSoup(r.text, 'lxml')

    #プログラムのコードは除去
    for tag in soup.find_all('div',{'class':'code-frame'}):
        tag.decompose()
    
    #記事内容を抽出
    for tag in soup.find_all('section'):
        text += tag.getText()
        
    return text


'''
Qiitaの記事から現在登録されているタグを抽出する
'''
def extractTags(url, all_tags):
    tags = []
    
    r = requests.get(url) 
    soup = BeautifulSoup(r.text, 'lxml')

    # Qiitaのタグ情報を格納したDBに接続
    sql = 'SELECT * FROM tags WHERE id=?'    
    con = sqlite3.connect(db_name)
    cursor = con.cursor()
    
    # 生成したタグ情報よりタグ名のリストを取得
    t_name = [t.get('name') for t in all_tags]
    
    # Qiitaの記事に現在登録されているタグを取得
    for keyword in soup.find('meta', attrs={'name':'keywords'}).get('content').split(','):
        #タグの情報を取得
        keyword = keyword.lower()
        rows = cursor.execute(sql,(keyword,))
        res = cursor.fetchone()
        followers = int(res[1]) if res else 0
        items = int(res[2]) if res else 0
        value = all_tags[t_name.index(keyword)]["value"] if keyword in t_name else 0
        
        tag = {}
        tag['name'] = keyword
        tag['value'] = value
        tag['followers'] = followers
        tag['counts'] = items
        tags.append(tag)
    
    return tags


"""
画面を表示する
"""
@app.route('/', methods=['GET', 'POST'])
def showApp():
    url = ''
    if request.method == 'POST':
        url = request.form['url']
        if not url.startswith('https://qiita.com'):
            return render_template('index.html', title='Qiitaタグ自動生成', error_msg='QiitaのURLを指定してね')
    elif request.method == 'GET':
        return render_template('index.html', title='Qiitaタグ自動生成')

    text = extractText(url)
    all_tags = createTags(text)
    tags_auto_value = sorted(all_tags, key=lambda tag: tag['value'], reverse=True)[0:5]
    tags_auto_followers = sorted(all_tags, key=lambda tag: tag['followers'], reverse=True)[0:5]
    tags_auto_counts = sorted(all_tags, key=lambda tag: tag['counts'], reverse=True)[0:5]    
    tags_now = extractTags(url, all_tags)
    return render_template('index.html', title='Qiitaタグ自動生成', tags1=tags_auto_value, tags2=tags_auto_followers, tags3 = tags_auto_counts, tags4=tags_now)


"""
メイン
"""
if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', threaded=True)  
