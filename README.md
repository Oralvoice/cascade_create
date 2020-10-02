# 説明
発音を評価するための分類器(口)を作成する。<br>

# 実行環境
windows10<br>
python3.8.1<br>
OpenCV 3.4.10

# インストール方法
[python3.8.1](https://www.python.org/downloads/release/python-381/)<br>
[OpenCV 3.4.10](https://sourceforge.net/projects/opencvlibrary/files/3.4.10/opencv-3.4.10-vc14_vc15.exe/download)<br>
pip3 install opencv-python==3.4.9.33　←コマンドプロンプトで実行 <br>
pip install numpy　←コマンドプロンプトで実行 <br>


# 実行方法
Ⅰ. cascade_createフォルダを任意のフォルダにコピーする。<br>
Ⅱ. インストールしたopencv-3.4.10-vc14_vc15.exeを実行すると、ダウンロードフォルダの中にopencvフォルダが生成される。opencv->build->x64->vc15->bin->opencv_world3410.dll ファイルをcascade_createフォルダに張り付ける。<br>
Ⅲ. [メインプログラム](/data_create.py) の7行目にある cd="D:\\cascade_create\\" をⅠで張り付けたフォルダパスに書き換える。<br>
Ⅳ. [/WORDLIST/任意の単語/video](/WORDLIST/ask/video) フォルダ内に分類器に学習させる動画(mp4形式)を張り付ける。動画ファイルの名前は 単語名_動画番号.mp4 にすること。<br>
Ⅴ. [/negativeData/customizeSamples](/negativeData/customizeSamples) フォルダ内に任意の不正解画像を入れる（この操作はしなくてもよい）。入れる場合は、名前をcustomize_番号.jpgとすること。<br>
Ⅵ. [メインプログラム](/data_create.py) を実行し、学習させる単語とデータの水増しをするかどうかを入力する。<br>
Ⅶ. プログラムの終了後、[command.txt](/WORDLIST/ask/command.txt) が生成されているので、command.txt内の文字をコマンドプロンプトへ入力する。<br>
Ⅷ. コマンドの終了後、[/WORDLIST/単語/positive/cascade](/WORDLIST/ask/positive/cascade0) 内にcascade.xml が生成されている。<br>
Ⅸ. 各cascadeフォルダ内のcascade.xmlをアプリ(OralVoice)に組み込む。<br>


