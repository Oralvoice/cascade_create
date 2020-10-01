# 説明
発音評価するための分類器を作成する。<br>

# 実行方法
Ⅰ. cascade_createフォルダを任意のフォルダにコピーする。<br>
Ⅱ. [メインプログラム](/data_create.py) の7行目にある cd="D:\\cascade_create\\" をⅠで張り付けたフォルダパスに書き換える。<br>
Ⅲ. /WORDLIST/任意の単語/video フォルダ内に分類器に学習させる動画(mp4形式)を張り付ける。動画ファイルの名前は 単語名_動画番号.mp4 にすること。
Ⅳ. data_create.py を実行し、学習させる単語とデータの水増しをするかどうかを入力する。
Ⅴ. プログラムの終了後、/command.txt が生成されているので、command.txt内の文字をコマンドプロンプトへ入力する。
Ⅵ. コマンドの終了後、/WORDLIST/単語/positive/cascade 内にcascade.xml が生成されている。
Ⅶ. 各cascade内のcascade.xmlをアプリ(OralVoice)に組み込む

# 実行環境
windows10
python3.8.1
OpenCV 3.4.8

# インストール方法
