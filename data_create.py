import os
import sys
import numpy as np
import cv2
import itertools

cd = "D:\\cascade_create\\"

print("学習させる単語を入力してください>")
learningWord = input()
print("正解画像の水増しをしますか？ yes or no >>")
hoge = input()
if hoge == 'yes':
    flag0 = True
else:
    flag0 = False

# 画像から顔を検出し、顔の下3分の1を切り取って返す関数
def cutUnderFaceFromImage(image):
    # カスケードファイルを利用した検出器(顔検出)を定義
    faceCascade = cv2.CascadeClassifier(cd + "haarcascade_frontalface_default.xml")
    # グレースケールに変換
    grayImg = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 複数の顔が検出されるのを防ぐため、minSizeに与えるサイズを変化させる
    for i in range(20, 40):
        # 顔があると判断された箇所を取得する
        faceList = faceCascade.detectMultiScale(grayImg, scaleFactor=1.1, minNeighbors=5, minSize = (i*5, i*5))
        # 顔が1つだけ検出された
        if len(faceList) == 1:
            x,y,w,h = faceList[0]
            height = image.shape[0]
            # 顎を検出しないときがあるのでy+h+30をして、余分に切り取る（顎が入っていないと後に口検出したときに口が検出されないときがある）
            # また、顔の上半分は口検出に関係ないので切り取る
            return image[y+int(h/2): min(y+h+30, height), x: x+w]
    # このelseに入るということは顔が検出されなかったor複数検出された
    else:
        # 顔が検出されなかった
        if len(faceList) == 0:
            return image
        # 顔が複数検出された
        else:
            # 検出された顔の中で最も面積が大きいものを顔と判断することにする
            height= image.shape[0]
            maxArea = 0
            for (x,y,w,h) in faceList:
                if maxArea < w*h:
                    maxArea = w*h
                    # 顎を検出しないときがあるのでy+h+30をして、余分に切り取る
                    ans = image[y+int(h/2): min(y+h+30, height), x: x+w]
            return ans

    # ここへは普通到達しない
    return image

# 画像から口を検出して切り取って返す関数
def cutMouthFromImage(image):
    # カスケードファイルを利用した検出器(口検出)を定義
    mouthCascade = cv2.CascadeClassifier(cd + "haarcascade_mcs_mouth.xml")
    # グレースケールに変換
    grayImg = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 複数の口が検出されるのを防ぐため、minSizeに与えるサイズを変化させる
    for i in range(10, 25):
        # 口があると判断された箇所を取得する
        mouthList = mouthCascade.detectMultiScale(grayImg, scaleFactor=1.1, minNeighbors=4, minSize = (i*5, i*5))
        # 口が1つだけ検出された
        if len(mouthList) == 1:
            x,y,w,h = mouthList[0]
            # 口を切り取って返す
            return image[y: y+h, x: x+w]
    # このelseに入るということは口が検出されなかったor複数検出された
    else:
        # 口が検出されなかった
        if len(mouthList) == 0:
            return image
        # 口が複数検出された
        else:
            # 検出された口の中で最も面積が大きいものを口と判断することにする
            maxArea = 0
            for (x,y,w,h) in mouthList:
                if maxArea < w*h:
                    maxArea = w*h
                    ans = image[y: y+h, x: x+w]
            return ans
    
    # ここへは普通到達しない
    return image

# 口周辺の余分な部分を切り取る関数
def cutMouthExtraPart(image):
    # エッジ検出
    edge = cv2.Canny(image, 40, 80, L2gradient=True)
    # モルフォロジー変換(クロージング)
    # エッジの縦成分を消去する。このとき唇のエッジは横成分が多いので消去されない
    kernel = np.array([[0,0,0],[1,1,1],[0,0,0]], dtype="uint8")
    opening = cv2.morphologyEx(edge, cv2.MORPH_OPEN, kernel)
    # モルフォロジー変換(オープニング)
    # エッジの横成分を拡張する。このとき唇は横成分のエッジが多いのでよく拡張される
    kernel = np.array([[0,1,0],[0,1,0],[0,1,0]], dtype="uint8")
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)


    height, width = image.shape[:2]
    centerX, centerY = int(width/2), int(height/2)

    # 唇の左端を探す
    maxNum = -1
    for vct in (-2, -1, 0, 1, 2):
        # y座標を少しずつ変えながら探す
        y = centerY + vct*int(height/17)

        # x座標を少しずつ変えながら探す
        for x in range(0, int(width/4), 4):
            rect = (x, y-int(height/13), int(width/15), int(height/13)*2)
            # rect内の白色画素の数を取得する
            whitePixelNum = getWhitePixelNum(closing, rect)
            if maxNum < whitePixelNum:
                maxNum = whitePixelNum
                # ずらしながら探した先で最も白の数が多かった位置を唇の左端とする
                leftX = x
                # そのときのy座標を口の中心y座標として保存する
                mouthCenterY = set([y])
    if maxNum < 1:
        # 白色画素が少ない場合、正確に唇の左端が判定できないとし、leftX=0とする
        leftX = 0
    
    # 唇の右端を探す
    maxNum = -1
    for vct in (-2, -1, 0, 1, 2):
        # y座標を少しずつ変えながら探す
        y = centerY + vct*int(height/17)

        # x座標を少しずつ変えながら探す
        for x in range(width-1, int(3*width/4), -4):
            rect = (x-int(width/15), y-int(height/13), int(width/15), int(height/13)*2)
            # rect内の白色画素の数を取得する
            whitePixelNum = getWhitePixelNum(closing, rect)
            if maxNum < whitePixelNum:
                maxNum = whitePixelNum
                # ずらしながら探した先で最も白の数が多かった位置を唇の右端とする
                rightX = x
                temp = y
    if maxNum < 1:
        # 白色画素が少ない場合、正確に唇の右端が判定できないとし、rightX=0とする
        rightX = width
    
    # 右端を探して得られた口の中心y座標も保存する
    mouthCenterY.add(temp)

    # 上唇を探す
    maxNum = -1
    for cY in mouthCenterY:
        # y座標を少しずつ変えながら探す（口の中心x座標はcenterXであることがほとんどなので変える必要はない）
        for y in range(0, int(1*cY/5), 4):
            rect = (centerX-int(width/15), y, int(width/15)*2, int(height/13))
            # rect内の白色画素の数を取得する
            whitePixelNum = getWhitePixelNum(closing, rect)
            if maxNum < whitePixelNum:
                maxNum = whitePixelNum
                # ずらしながら探した先で最も白の数が多かった位置を上唇とする
                topY = y
    if maxNum < 1:
        # 白色画素が少ない場合、正確に上唇が判定できないとし、topY=0とする
        topY = 0
    
    # 下唇を探す
    maxNum = -1
    for cY in mouthCenterY:
        # y座標を少しずつ変えながら探す（口の中心x座標はcenterXであることがほとんどなので変える必要はない）
        for y in range(height-1, int(7*cY/5), -4):
            rect = (centerX-int(width/15), y-int(height/13), int(width/15)*2, int(height/13))
            # rect内の白色画素の数を取得する
            whitePixelNum = getWhitePixelNum(closing, rect)
            if maxNum < whitePixelNum:
                maxNum = whitePixelNum
                # ずらしながら探した先で最も白の数が多かった位置を下唇とする
                bottomY = y
    if maxNum < 1:
        # 白色画素が少ない場合、正確に下唇が判定できないとし、bottomY=0とする
        bottomY = height
    
    # 切り取って返す
    return image[topY: bottomY, leftX: rightX]

# コントラスト調整
def adjust(image, contrast = 1.0, brightness = 0.0):
    newImage = contrast * image + brightness
    return np.clip(newImage, 0, 255).astype(np.uint8)

# 画像中の四角形の中にある白の数を返す関数（画像は2値化してあること）Rectは(左上x座標,　左上y座標,　幅,　高さ)
def getWhitePixelNum(image, rect):
    x,y,w,h = rect
    whitePixelNum = 0
    for width in range(w):
        for height in range(h):
            if image[y+height][x+width] == 255:
                whitePixelNum += 1
    
    return whitePixelNum

# 動画の全フレームを指定されたフォルダに保存する関数。返り値はフレーム数
def saveAllFrames(videoPath, dirPath, basename):
    # 動画ファイルを読み込み
    cap = cv2.VideoCapture(videoPath)
    # 動画ファイルを読み込めたか確認
    if not cap.isOpened():
        print(videoPath + " cant open")
        return

    # dirPathに新たなファイルを作成
    os.makedirs(dirPath, exist_ok=True)
    # dirPathとbasenameを結合
    basePath = os.path.join(dirPath, basename)

    n = 0

    while True:
        # 動画を1フレーム読み込む
        ret, frame = cap.read()
        if ret:
            # 画像(frame)を保存
            cv2.imwrite('{}_{}.{}'.format(basePath, str(n), 'jpg'), frame)

            n += 1
        else:
            # フレーム数を返す
            return n

# 正解画像を作成し、指定されたフォルダに保存する関数
def createSamplesAndSave(imagePath, dirPath, basename, infoDat, increaseFlag = False):
    # 画像ファイルを読み込み
    img = cv2.imread(imagePath)
    # 画像ファイルを読み込めたか確認
    if img is None:
        print(imagePath + " cant read")
        return

    # img内から顔を検出して顔下半分のみの画像にする
    face = cutUnderFaceFromImage(img)
    # faceから口を切り取る
    mouth = cutMouthFromImage(face)
    # 口周りのひげやしわを切り取る
    cleanMouth = cutMouthExtraPart(mouth)

    # DirPathに新たなファイルを作成
    os.makedirs(dirPath, exist_ok=True)
    # DirPathとBaseNameを結合
    basePath = os.path.join(dirPath, basename)

    # 画像の水増しをしない
    if not increaseFlag:
        height, width = cleanMouth.shape[:2]
        cv2.imwrite(basePath + ".jpg", cleanMouth)
        infoDat.write(basename + ".jpg 1 0 0 " + str(width) + " " + str(height)+"\n")
    # 画像の水増しをする
    else:
        # imgを左右反転
        flipCleanMouth = cv2.flip(cleanMouth, 1)

        # 水増しのベースとなる画像リストに格納
        baseImgs = []
        baseImgs.append(cleanMouth)
        baseImgs.append(flipCleanMouth)

        # リサイズの倍率
        resizeVector = (0.9, 1.0, 1.2)
        # 回転角
        angles = (350, 355, 0, 5, 10)
        # コントラストの倍率
        contrast = (1.2, 1.5, 1.7)

        # このiは水増しによって生成された画像の数を表す
        i = 0
        for baseImg in baseImgs:
            height, width = baseImg.shape[:2]

            # ベース画像をリサイズする
            for vx, vy in list(itertools.product(resizeVector, repeat=2)):
                newImg = cv2.resize(baseImg, (int(width*vx), int(height*vy)))
                
                newHeight, newWidth = newImg.shape[:2]

                # 回転の中心を指定
                center = (newWidth//2, newHeight//2)
                # 画像を回転させる
                for angle in angles:
                    trans = cv2.getRotationMatrix2D(center, angle, 1.0)

                    newImgRotated = cv2.warpAffine(newImg, trans, (newWidth, newHeight))
                    newRotatedHeight, newRotatedWidth = newImgRotated.shape[:2]

                    # 回転させた画像を保存
                    cv2.imwrite('{}{}.{}'.format(basePath, str(i), 'jpg'), newImgRotated)                
                    # info.datにvecファイルを生成するのに必要なデータを書きこむ
                    infoDat.write(basename + str(i)+ ".jpg 1 0 0 " + str(newRotatedWidth) + " " + str(newRotatedHeight)+"\n")
            
                    i += 1

                # コントラストを調整する
                for k in contrast:
                    newImgContrast = adjust(newImg, contrast=k)
                    newContrastHeight, newContrastWidth = newImgContrast.shape[:2]

                    # コントラスト調整した画像を保存
                    cv2.imwrite('{}{}.{}'.format(basePath, str(i), 'jpg'), newImgContrast)
                    # info.txtにdatファイルを生成するのに必要なデータを書きこむ
                    infoDat.write(basename + str(i)+ ".jpg 1 0 0 " + str(newContrastWidth) + " " + str(newContrastHeight)+"\n")
                    
                    i += 1

# negativeDataフォルダから不正解画像をとってくる
def saveNegativeData(limit = 1e11):
    defaultNegativeDataFolderPath = cd + "negativeData/defaultSamples"
    customizeNegativeDataFolderPath = cd + "negativeData/customizeSamples"
    saveFolderPath = cd + "WORDLIST/" + learningWord +"/negative"
    
    os.makedirs(saveFolderPath, exist_ok=True)

    f = open(saveFolderPath + "/bg.dat", mode='w')

    saveDataNum = 0
    i = 0
    while saveDataNum < limit:
        basename = "default_" + str(i) + ".jpg"
        imgPath = defaultNegativeDataFolderPath + "/" + basename
        if os.path.exists(imgPath):
             # 画像ファイルを読み込み
            img = cv2.imread(imgPath)
            # 画像ファイルを読み込めたか確認
            if img is None:
                print(defaultNegativeDataFolderPath + "/" + basename + "cant read")
                return

            cv2.imwrite(saveFolderPath + "/" + basename, img)
            f.write(saveFolderPath + "/" + basename + "\n")
            saveDataNum += 1
        else:
            break
        i += 1

    
    j = 0
    while saveDataNum < limit:
        basename = "customize_" + str(j) + ".jpg"
        imgPath = customizeNegativeDataFolderPath + "/" + basename
        if os.path.exists(imgPath):
            # 画像ファイルを読み込み
            img = cv2.imread(imgPath)
            # 画像ファイルを読み込めたか確認
            if img is None:
                print(customizeNegativeDataFolderPath + "/" + basename + "cant read")
                return

            cv2.imwrite(saveFolderPath + "/" + basename, img)
            f.write(saveFolderPath + "/" + basename + "\n")
            saveDataNum += 1
        else:
            break
        j += 1

# コマンドプロンプトで実行する文を生成する
def command_create(cascadeNum):
    negative_num = 0
    if(os.path.exists(cd + "WORDLIST/" + learningWord + "/negative/bg.dat")):
        negative_file = open(cd + "WORDLIST/" + learningWord + "/negative/bg.dat", mode='r')
        negative_num = len([s.replace("\n", "") for s in negative_file.readlines()])
        negative_file.close()
    else:
        print(cd + "WORDLIST/" + learningWord + "/negative/bg.dat not exist\n")
        print("This program finished by exit()")
        exit()

    f = open(cd + "WORDLIST/" + learningWord +"/command.txt", mode='w')
    f.write("copy /y " + cd + "opencv_createsamples.exe D:\\purokonOld\\" + "WORDLIST\\" + learningWord + "\\positive\n")
    f.write("copy /y " + cd + "opencv_traincascade.exe D:\\purokonOld\\" + "WORDLIST\\" + learningWord + "\\positive\n")
    f.write("copy /y " + cd + "opencv_world3410.dll D:\\purokonOld\\" + "WORDLIST\\" + learningWord + "\\positive\n")
    f.write("cd/d " + cd + "WORDLIST/" + learningWord + "/positive\n")

    for i in range(cascadeNum):
        positive_file = open(cd + "WORDLIST/" + learningWord + "/positive/cascade" + str(i) + "/info.dat", mode='r')
        positive_num = len([s.replace("\n", "") for s in positive_file.readlines()])
        
        f.write("opencv_createsamples -info cascade" + str(i) + "/info.dat -vec " + str(i) + ".vec -num " + str(positive_num) + "\n")
        f.write("opencv_traincascade -data cascade" + str(i) + "/ -vec " + str(i) + ".vec -bg " + cd + "WORDLIST/" + learningWord + "/negative/bg.dat -numPos " + str(int(positive_num * 0.85)) + " -numNeg " + str(negative_num) + " -featureType HAAR\n")
    positive_file.close()
    f.close()

def main():
    
    # 動画から切り取った画像の枚数を格納する
    frameNums = []

    # このiは何番目の動画かを表す
    i = 0
    # cd + "WORDLIST/" + learningWord + "/video に用意された動画のフレームをすべて切り出す
    while True:
        videoPath = cd + "WORDLIST/" + learningWord + "/video/" + learningWord + "_" + str(i) + ".mp4"
        dirPath = cd + "WORDLIST/" + learningWord + "/all_video_frames/" + "video_" + str(i) + "_frames"
        basename = "frame"

        # videoPathが存在する
        if os.path.exists(videoPath):
            temp = saveAllFrames(videoPath, dirPath, basename)
            # frameNumの末尾に動画のフレーム数を格納
            frameNums.append(temp)
            print("video_" + str(i) + " cut frame complete")
        # videoPathが存在しない
        else:
            # iが0のとき動画は１つも用意されていないので、プログラムを終了する
            if i == 0:
                print(cd + "WORDLIST/" + learningWord + "/video not have video. Please have any video.")
                print("This program finished by exit()")
                exit()
            break

        i += 1

    # 用意された発音動画の数
    materialNum = i

    # この単語で作る分類器の数は(全動画中最小フレーム÷2)とする
    cascadeNum = int(min(frameNums)/2)
    # 分類器数の上限は20とする
    if cascadeNum > 20:
        cascadeNum = 20


    # 各分類器作成に使用するフレームを選ぶ
    # 選んだフレームを正解画像として使えるように処理する
    # 正解画像をcd + "WORDLIST/" + learningWord + "/positive/cascade 内に保存する
    for i in range(materialNum):
        # フレーム数と分類器数との差
        diff = frameNums[i] - cascadeNum
        # useEveryFrameフレーム毎に正解画像として使う
        useEveryFrame = int(frameNums[i] / diff)
        # 何枚捨てたか記憶する変数
        throwAwayNum = 0

        # i番目の動画フレームの中から分類器作成に使用するフレームを選ぶ
        for j in range(1, frameNums[i] + 1):

            # 分類器作成に使用しないフレーム
            if (j-throwAwayNum > cascadeNum) or (j % (useEveryFrame+1) == 0):
                # 一枚捨てる
                throwAwayNum += 1
            # 分類器作成に使用するフレーム
            else:
                # 分類器作成に使用するフレームのパス
                imagePath = cd + "WORDLIST/" + learningWord + "/" + "all_video_frames/" + "video_" + str(i) + "_frames/frame_" + str(j-1) + ".jpg"
                # フレームを処理した後に保存するフォルダのパス
                dirPath = cd + "WORDLIST/" + learningWord + "/positive/cascade" + str(j-1-throwAwayNum)
                # フレームを処理した後の画像の名前
                basename = "No" + str(i) + "_"

                # DirPathに新たなファイルを作成
                os.makedirs(dirPath, exist_ok=True)
                # 0番目のときはinfo.datを書き込み専用でopenする
                if(i == 0):
                    f = open(dirPath + "/info.dat", mode='w')
                # それ以外は追加書き込み専用でopen
                else:
                    f = open(dirPath + "/info.dat", mode='a')
                
                # フレームを処理して指定フォルダに書き込む
                createSamplesAndSave(imagePath, dirPath, basename, f, increaseFlag=flag0)
                print("video_" + str(i) + " set data for cascade" + str(j-1-throwAwayNum) + " complete")

                f.close()
    
    # saveNegativeDataの引数には任意の値を入れる
    saveNegativeData(400)
    print("negative data saved")
    command_create(cascadeNum)
    print("command created")


if __name__ == "__main__":
    main()
