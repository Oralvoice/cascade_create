# 説明
発音を評価するための分類器を作成する。<br>

# 実行環境
windows10<br>
python3.8.1<br>
OpenCV 3.4.10

# インストール方法
[python3.8.1](https://www.python.org/downloads/release/python-381/)
[OpenCV 3.4.10](https://github.com/opencv/opencv/archive/3.4.10.zip)


# 実行方法
Ⅰ. cascade_createフォルダを任意のフォルダにコピーする。<br>
Ⅱ. [メインプログラム](/data_create.py) の7行目にある cd="D:\\cascade_create\\" をⅠで張り付けたフォルダパスに書き換える。<br>
Ⅲ. [/WORDLIST/任意の単語/video](/WORDLIST/ask/video) フォルダ内に分類器に学習させる動画(mp4形式)を張り付ける。動画ファイルの名前は 単語名_動画番号.mp4 にすること。<br>
Ⅳ. [/negativeData/customizeSamples](/negativeData/customizeSamples) フォルダ内に任意の不正解画像を入れる（この操作はしなくてもよい）。入れる場合は、名前をcustomize_番号.jpgとすること。<br>
Ⅴ. [メインプログラム](/data_create.py) を実行し、学習させる単語とデータの水増しをするかどうかを入力する。<br>
Ⅵ. プログラムの終了後、[command.txt](/WORDLIST/ask/command.txt) が生成されているので、command.txt内の文字をコマンドプロンプトへ入力する。<br>
Ⅶ. コマンドの終了後、[/WORDLIST/単語/positive/cascade](/WORDLIST/ask/positive/cascade0) 内にcascade.xml が生成されている。<br>
Ⅷ. 各cascadeフォルダ内のcascade.xmlをアプリ(OralVoice)に組み込む。<br>


