## WebpAnim2Mp4について 0.1.1
WebPのアニメーションファイルをmp4に変換します  
変換時にフレームレートとループの有無を指定できます  

![WebpAnim2Mp4-image](docs/WebpAnim2Mp4-image001.jpg)

## 特徴
- 動画生成AIなどで作成した、短いWebPアニメーションファイルをmp4に手軽に変換  
- フレームの逆再生を含むループ指定可能  
- 複数のWebPを一つのmp4に結合可能  
- 最終フレームのpng画像出力が可能  

## インストール方法（簡易）
[簡易インストール版zipのダウンロード]  
    https://github.com/nekotodance/WebpAnim2Mp4/releases/download/latest/WebpAnim2Mp4.zip  

- Pythonのインストール（SD標準の3.10.6推奨）  
- zipファイルを解凍  
- 解凍したフォルダ内の「wm-install.ps1」を右クリックして「PowerShellで実行」を選択  
> [!WARNING]
> シェルスクリプトはデフォルトでは動作しない設定となっています  
> その場合はターミナルを管理者として実行し、以下のコマンドを実行してください（比較的安全な方式）  
> Set-ExecutionPolicy Unrestricted -Scope CurrentUser -Force

- イントールの最後にデスクトップにリンクをコピーするかどうかを聞いてきます  
「"Do you want to copy the shortcut to your desktop? (y or enter/n)」  
必要があれば「y」入力後、もしくはそのまま「enter」キー  
必要なければ「n」入力後「enter」キー  
- WebpAnim2Mp4リンクが作成されます  

## インストール方法（手動）
- Pythonのインストール（SD標準の3.10.6推奨）  
- gitのインストール  
- gitでリポジトリを取得  
    git clone https://github.com/nekotodance/WebpAnim2Mp4
- 必要なライブラリ  
    pip install PyQt5 imageio opencv-python
- 実行方法  
    Python WebpAnim2Mp4.py

## 利用方法
まずはアプリ上にWebPアニメーションファイルをドラッグ＆ドロップ  
次に以下のいずれかのボタンで処理を行います

### 変換ボタン
入力したWebPファイルを順次mp4ファイルに変換します  
- フレームレート、Loop(※1)を指定して変換ボタン  
- 同じフォルダに変換後のmp4ファイル(※2)を生成  

### 結合ボタン
入力したWebPファイルを結合して1つのmp4ファイルに変換します  
- フレームレート、drop last frame(※3)を指定して結合ボタン  
- 同じフォルダに結合後の1つのmp4ファイル(※4)を生成  

### 画像化ボタン
入力したWebPファイルの最終フレームを順次PNGファイルとして出力します
- パラメータは関係なく、画像化ボタン
- 同じフォルダに変換後のpngファイル(※5)を生成  

### クリアボタン
入力中のファイルリストをクリアします  

## 注釈
※1:loopについて  
0,1,2,3の4枚のアニメーションの場合、0,1,2,3,0,1,2,3ではなく、0,1,2,3,3,2,1,0でもなく  
0,1,2,3,2,1の動画を生成します （動画をループ再生した場合にフレームが重複しないようにしています）  

※2:input.webpを入力した場合、ファイル名に設定値を付与します  
・frame:15指定の場合は、input_15fps.mp4  
・frame:60指定、loopありの場合は、input_60fps_loop.mp4  

※3:drop last frameについて  
a0,a1,a2,a3とb0,b1,b2,b3,b4,b5の二つのアニメーションファイルの場合  
dropチェックなしで、a0,a1,a2,a3,b0,b1,b2,b3,b4,b5 （全てのフレームを結合）  
dropチェックありで、a0,a1,a2,b0,b1,b2,b3,b4,b5 （最終ファイル以外の終端frameを削除して結合）  
の出力を行います  
これはa3フレームを起点として生成した別のアニメーションファイルを結合することを想定しています  

※4:input01.webp、input02.webpを入力した場合、先頭のファイル名に設定値を付与します  
・frame:15指定の場合は、input01_concati_15fps.mp4  
・frame:60指定、dropありの場合は、input01_concati_60fps_drop.mp4  

※5:input.webpを入力した場合、ファイル名に0オリジンの最終フレーム番号を付与します  
・フレーム数が8枚のWebPファイルの場合は、input_7frame.png  
・フレーム数が49枚のWebPファイルの場合は、input_48frame.png  

## 注意事項
- ComfyUIで作成したWebPアニメーションファイルでしかテストしていません  

## 変更履歴
- 0.1.1 最終フレームの画像化、結合機能を追加、他
- 0.1.0 初版  

以上
