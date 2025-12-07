REM === venv を有効化 ===
call "%~dp0venv\Scripts\activate.bat"
REM === Python スクリプトを引数付きで起動 ===
python "%~dp0mvConcatinate.py" %*
