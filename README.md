Qiitaタグ自動生成
====

自然言語処理を使ってQiitaのタグを自動で生成します


## 概要
termextractを使いQiitaの記事から専門用語（重要語）を抽出し、それをタグとして生成します。

![全体の流れ](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F206972%2F259c2216-8478-e254-c865-3ad69c45a34a.png?ixlib=rb-1.2.2&auto=compress%2Cformat&gif-q=60&s=f0b3925f775bf7d7a7f7ddf64795aa7b)

詳細はQiitaに記事としてまとめています。  
[Qiitaタグ自動ジェネレータ](https://qiita.com/fukumasa/items/7f6f69d4f6336aff3d90)



## デモ
以下で試せます。ちなみにHerokuアプリです。  
https://auto-create-qiita-tags.herokuapp.com/



## 環境
以下のいずれかが必要です。
- Docker
- Python3



## 使い方
### Dockerを使う場合
1. GitHubからソース一式をダウンロード
```
git pull https://github.com/fukumasa/auto-create-qiita-tags
```

2. Dockerビルドを実行
```
cd auto-create-qiita-tags
docker build -t auto-create-qiita-tags .
```

3. Dockerコンテナを実行
```
docker run -it -d -name app -p 5000:5000 auto-create-qiita-tags /bin/bash
```

4. ブラウザからアクセス  
http://localhost:5000



### Dockerを使わない場合
1. GitHubからソース一式をダウンロード
```
git pull https://github.com/fukumasa/auto-create-qiita-tags
```

2. Pythonプログラムを実行
```
cd auto-create-qiita-tags
python app.py
```



## Author
[fukumasa](https://github.com/fukumasa)
