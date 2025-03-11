## WebpAnim2Mp4について 0.1.0
WebPのアニメーションファイルをmp4に変換します  
変換時にフレームレートとループの有無を指定できます  

![WebpAnim2Mp4-image](docs/WebpAnim2Mp4-image001.jpg)

## 特徴
- 動画生成AIなどで作成した、短いWebPアニメーションファイルの変換に便利  
- 動画の画質とかにはこだわっていない人向け  

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
アプリ上にWebPアニメーションファイルをドラッグ＆ドロップしてください  
フレームレート、Loop※を指定して変換ボタンにて変換を行います

※loopについて
0,1,2,3,4,5,6,7の8枚のアニメーションの場合にループ指定を行うと
0,1,2,3,4,5,6,7,7,6,5,4,3,2,1,0ではなく
0,1,2,3,4,5,6,7,6,5,4,3,2,1の動画を生成します

## 注意事項
- ComfyUIで作成したWebPアニメーションファイルでしかテストしていません  

## 変更履歴
- 0.1.0 初版  

以上
