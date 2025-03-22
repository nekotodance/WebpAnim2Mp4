import sys
import os
import imageio.v2 as imageio
import cv2
import numpy as np
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QIcon, QColor
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog,
    QSpinBox, QCheckBox, QListWidget, QHBoxLayout, QStatusBar, QMainWindow,
    QMessageBox
)
from PyQt5.QtCore import Qt, QEvent
import pvsubfunc
import math

WINDOW_TITLE = "WebP Anim to MP4 Converter"
SETTINGS_FILE = "WebpAnim2Mp4.json"
GEOMETRY_X = "geometry-x"
GEOMETRY_Y = "geometry-y"
GEOMETRY_W = "geometry-w"
GEOMETRY_H = "geometry-h"
REVERSE_CHECKED = "reverse-checked"
LOOP_CHECKED = "loop-checked"
DROP_CHECKED = "drop-checked"
FRAME_RATE = "frame-rate"
APP_WIDTH = 480
APP_HEIGHT = 320
DEF_FRAME_RATE = 15
MOVIE_TOOLONG = 1200    #このframe数を超える動画が入力された場合警告を行う

SUPPORT_INPUT_EXT = (".png", ".jpg", ".webp", ".mp4")
SUPPORT_MOVIE_EXT = (".webp", ".mp4")

#良く使いそうなフレームレートをボタンで選択可能としておく
FRAME_LIST = (10,15,30,60)

class WebpAnim2Mp4(QMainWindow):
    def __init__(self):
        super().__init__()

        # ウィンドウ設定
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(100, 100, APP_WIDTH, APP_HEIGHT)
        #self.setWindowIcon(QIcon("res/WebpAnim2Mp4.ico"))
        self.setAcceptDrops(True)

        # UIレイアウト
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setStyleSheet("color: white; font-size: 14px; background-color: #202224;")
        self.layout = QVBoxLayout(self.centralWidget)
        self.listLayout = QHBoxLayout()
        self.file_list = QListWidget(self)  # ファイルリスト
        self.listLayout.addWidget(self.file_list)
        self.listBtnLayout = QVBoxLayout()
        self.button_up = QPushButton("↑", self)
        self.button_up.setFixedSize(40,40)
        self.listBtnLayout.addWidget(self.button_up)
        self.button_down = QPushButton("↓", self)
        self.button_down.setFixedSize(40,40)
        self.listBtnLayout.addWidget(self.button_down)
        self.listBtnLayout.addStretch()
        self.button_delete = QPushButton("del", self)
        self.button_delete.setFixedSize(40,40)
        self.listBtnLayout.addWidget(self.button_delete)
        self.listBtnLayout.addStretch()
        self.button_flip = QPushButton("flp", self)
        self.button_flip.setFixedSize(40,40)
        self.listBtnLayout.addWidget(self.button_flip)
        self.listBtnLayout.addStretch()
        self.button_clear = QPushButton('clr')
        self.button_clear.setFixedSize(40,40)
        self.listBtnLayout.addWidget(self.button_clear)
        self.listBtnLayout.addStretch()
        self.listLayout.addLayout(self.listBtnLayout)
        self.layout.addLayout(self.listLayout)

        self.settingLayout1 = QHBoxLayout()
        self.settingLayout1.addStretch()
        self.settingLayout1.addWidget(QLabel("frame:", self))
        self.convertBtns = []
        for i in range(len(FRAME_LIST)):
            self.convertBtns.append(QPushButton(str(FRAME_LIST[i])))
            self.convertBtns[i].setFixedWidth(32)
            self.settingLayout1.addWidget(self.convertBtns[i])
        self.fps_spinbox = QSpinBox(self)
        self.fps_spinbox.setRange(1, 240)
        self.fps_spinbox.setValue(DEF_FRAME_RATE)
        self.fps_spinbox.setFixedWidth(64)
        self.settingLayout1.addWidget(self.fps_spinbox)
        self.layout.addLayout(self.settingLayout1)

        self.settingLayout2 = QHBoxLayout()
        self.drop_checkbox = QCheckBox("drop first frame", self)
        self.settingLayout2.addWidget(self.drop_checkbox)
        self.settingLayout2.addStretch()
        self.reverse_checkbox = QCheckBox("reverse", self)
        self.settingLayout2.addWidget(self.reverse_checkbox)
        self.loop_checkbox = QCheckBox("loop", self)
        self.settingLayout2.addWidget(self.loop_checkbox)
        self.layout.addLayout(self.settingLayout2)

        self.buttonLayout = QHBoxLayout()
        self.button_concatinate = QPushButton("結合", self)
        self.button_concatinate.setFixedHeight(40)
        self.button_concatinate.setStyleSheet(
            """
            QPushButton {
                background-color: #DD2200;  /* 背景色 */
                color: black;  /* 文字色 */
            }
            QPushButton:disabled {
                background-color: lightgray;  /* 無効状態の背景色 */
                color: #222222;  /* 無効状態の文字色 */
            }
            """
        )
        self.buttonLayout.addWidget(self.button_concatinate)
        self.button_lastpic = QPushButton('画像化')
        self.button_lastpic.setFixedHeight(40)  # ボタンの高さを調整
        self.buttonLayout.addWidget(self.button_lastpic)
        self.buttonLayout.addStretch()
        self.button_convert = QPushButton("変換", self)
        self.button_convert.setFixedHeight(40)
        self.button_convert.setStyleSheet(
            """
            QPushButton {
                background-color: #22DD00;  /* 背景色 */
                color: black;  /* 文字色 */
            }
            QPushButton:disabled {
                background-color: lightgray;  /* 無効状態の背景色 */
                color: #222222;  /* 無効状態の文字色 */
            }
            """
        )
        self.buttonLayout.addWidget(self.button_convert)
        self.layout.addLayout(self.buttonLayout)
        self.setLayout(self.layout)

        self.file_list.installEventFilter(self)
        self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.file_list.itemSelectionChanged.connect(self.change_selection_color)

        self.button_up.clicked.connect(self.list_item_moveup)
        self.button_down.clicked.connect(self.list_item_movedown)
        self.button_delete.clicked.connect(self.list_item_delete)
        self.button_flip.clicked.connect(self.list_item_flip)
        self.button_concatinate.clicked.connect(self.concatinate_files)
        self.button_lastpic.clicked.connect(self.to_picfile)
        self.button_convert.clicked.connect(self.convert_files)
        self.button_clear.clicked.connect(self.clear_lists)
        for i in range(len(FRAME_LIST)):
            self.convertBtns[i].clicked.connect(lambda _, i=i: self.fps_spinbox.setValue(FRAME_LIST[i]))

        self.statusBar = QStatusBar()
        self.statusBar.setStyleSheet("color: white; font-size: 14px; background-color: #31363b;")
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage(f"動画や画像ファイルをドラッグドロップしてください")

        #設定ファイルがあれば読み込み
        if os.path.exists(SETTINGS_FILE):
            self.load_settings()

        self.file_paths = []  # ファイルパスのリスト

    def closeEvent(self, event):
        self.save_settings()
        super().closeEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        listnum = len(event.mimeData().urls())
        dropnum = 0
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith(SUPPORT_INPUT_EXT):
                self.file_paths.append(file_path)
                self.file_list.addItem(os.path.basename(file_path))
                dropnum += 1
        self.file_list.scrollToItem(self.file_list.item(self.file_list.count() - 1))

        mes = f"{dropnum}ファイルがドロップされました"
        if dropnum == 0:
            exts = ""
            for ext in SUPPORT_INPUT_EXT:
                exts += ext.replace(".","") + ","
            mes = f"エラー: {exts[:-1]}ファイル以外は対応していません"
        elif dropnum != listnum:
            mes += f"（{listnum-dropnum}ファイルは対象外）"
        self.statusBar.showMessage(mes)

    def list_item_moveup(self):
        selected_items = self.file_list.selectedItems()
        if not selected_items: return

        selected_rows = sorted([self.file_list.row(item) for item in selected_items])
        if selected_rows[0] == 0: return

        old_position = self.file_list.verticalScrollBar().value()
        for row in selected_rows:
            item = self.file_list.takeItem(row)
            self.file_list.insertItem(row - 1, item)
            self.file_list.setCurrentRow(row - 1)
            item = self.file_paths.pop(row)
            self.file_paths.insert(row - 1, item)

        #上移動の場合は2行の余白を残してリスト表示
        top_position = self.file_list.verticalScrollBar().value()
        row = selected_rows[0] - 1 - 2
        if row < top_position:
            self.file_list.verticalScrollBar().setValue(max(0,row))
        else:
            self.file_list.verticalScrollBar().setValue(old_position)

    def list_item_movedown(self):
        selected_items = self.file_list.selectedItems()
        if not selected_items: return

        selected_rows = sorted([self.file_list.row(item) for item in selected_items], reverse=True)
        if selected_rows[0] == self.file_list.count() - 1: return

        old_position = self.file_list.verticalScrollBar().value()
        for row in selected_rows:
            item = self.file_list.takeItem(row)
            self.file_list.insertItem(row + 1, item)
            self.file_list.setCurrentRow(row + 1)
            item = self.file_paths.pop(row)
            self.file_paths.insert(row + 1, item)

        #下移動の場合は2行の余白を残してリスト表示
        top_position = old_position
        list_range = self.file_list.viewport().height() // self.file_list.sizeHintForRow(0)
        if (self.file_list.viewport().height() % self.file_list.sizeHintForRow(0)) != 0:
            list_range = list_range - 1
        row = selected_rows[0] + 1 + 2
        if row > top_position + list_range:
            self.file_list.verticalScrollBar().setValue(min(self.file_list.verticalScrollBar().maximum(),row - list_range))
        else:
            self.file_list.verticalScrollBar().setValue(old_position)

    def list_item_delete(self):
        selected_items = self.file_list.selectedItems()
        if not selected_items: return

        selected_rows = sorted([self.file_list.row(item) for item in selected_items], reverse=True)
        for row in selected_rows:
            self.file_list.takeItem(row)
            self.file_paths.pop(row)

        #削除の場合は削除した先頭した行が画面内に収まるようにしてリスト表示
        row = row - 2
        if row < 0:
            row = 0
        self.file_list.scrollToItem(self.file_list.item(row))

        self.statusBar.showMessage(f"{len(selected_rows)}ファイルをリストから削除しました")

    def list_item_flip(self):
        selected_items = self.file_list.selectedItems()
        if not selected_items or len(selected_items) == 1:
            self.statusBar.showMessage(f"2つ以上の連続した項目を選択してください")
            return
        #選択している項目が連続していない場合も何もしない
        selected_indexes = sorted(self.file_list.row(item) for item in selected_items)
        if selected_indexes != list(range(selected_indexes[0], selected_indexes[-1] + 1)):
            self.statusBar.showMessage(f"選択している項目が連続していません")
            return

        position = self.file_list.verticalScrollBar().value()

        start_row = selected_indexes[0]
        reversed_items = [self.file_list.takeItem(i) for i in reversed(selected_indexes)]
        for i, item in enumerate(reversed_items):
            self.file_list.insertItem(start_row + i, item)
            item.setSelected(True)
        start_row = selected_indexes[0]
        reversed_paths = [self.file_paths.pop(i) for i in reversed(selected_indexes)]
        for i, item in enumerate(reversed_paths):
            self.file_paths.insert(start_row + i, item)

        self.file_list.verticalScrollBar().setValue(position)
        self.statusBar.showMessage(f"{len(selected_items)}ファイルの順序を入れ替えました")

    def error_check(self):
        result = False
        if not self.file_paths:
            self.statusBar.showMessage(f"エラー: ファイルが選択されていません")
            return True

    #リスト選択中のキーイベントフック処理
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            keyid = event.key()
            self.key_press_func(keyid)
            return True #常にKeyEventを消費に変更
        return super().eventFilter(obj, event)

    #通常のキーイベント処理
    def keyPressEvent(self, event):
        keyid = event.key()
        self.key_press_func(keyid)
        super().keyPressEvent(event)

    #実際のキー処理
    def key_press_func(self, keyid):
        if keyid in (Qt.Key_Delete, Qt.Key_Backspace, Qt.Key_R):
            self.list_item_delete()
        elif keyid in (Qt.Key_Up, Qt.Key_W):
            self.list_item_moveup()
        elif keyid in (Qt.Key_Down, Qt.Key_S):
            self.list_item_movedown()
        elif keyid== Qt.Key_F:
            self.list_item_flip()
        elif keyid == Qt.Key_C:
            self.clear_lists()

    def change_selection_color(self):
        # すべてのアイテムの色をリセット
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            item.setBackground(QColor("#202224"))

        # 選択されたアイテムの色を変更
        selected_items = self.file_list.selectedItems()
        for item in selected_items:
            item.setBackground(QColor("202280"))

    def proc_start(self):
        self.setEnabled(False)
        QApplication.processEvents()

    def proc_end(self, mes):
        self.setEnabled(True)
        self.statusBar.showMessage(mes)

    def convert_files(self):
        if self.error_check(): return
        if self.cansel_movie_toolong(self.file_paths): return
        self.proc_start()
        fps = self.fps_spinbox.value()
        filenum = len(self.file_paths)
        count = 0 
        for file_path in self.file_paths:
            self.statusBar.showMessage(f"{os.path.basename(file_path)}の変換中({count+1}/{filenum})")
            QApplication.processEvents()
            if self.convert_webp_to_mp4(file_path, fps):
                count += 1
        mes = f"変換完了！({count}ファイル)"
        if count == 0:
            mes = f"エラー: webpファイルが存在しません"
        elif count != filenum:
            mes = f"{filenum}ファイル中、{count}ファイルを変換しました"
        self.proc_end(mes)

    def convert_webp_to_mp4(self, file_path, fps):
        #WebPだけじゃなく、画質は落ちるけどmp4もサポート
        if not file_path.lower().endswith(SUPPORT_MOVIE_EXT): return False
        frames = imageio.mimread(file_path, memtest=False)
        if not frames: return False

        sloop = ""
        # リバース処理: 0,1,2...30 → 30,29,28...2,1,0 に変換
        if self.reverse_checkbox.isChecked():
            frames.reverse()
            sloop += "_rev"
        # ループ処理: 0,1,2...30 → 0,1,2...30,29,28...2,1 に変換
        if self.loop_checkbox.isChecked():
            frames += frames[len(frames)-2:1:-1] #上記の指定だと最後に0フレーム目が被ってる
            sloop += "_loop"

        height, width, _ = frames[0].shape
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        output_file = os.path.splitext(file_path)[0] + f"_{fps}fps{sloop}.mp4"
        out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

        for frame in frames:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
            out.write(frame)
        out.release()
        return True

    def clear_lists(self):
        self.file_list.clear()
        self.file_paths = []
        self.statusBar.showMessage(f"リストをクリアしました")

    def concatinate_files(self):
        if self.error_check(): return
        if self.cansel_movie_toolong(self.file_paths): return
        self.proc_start()
        fps = self.fps_spinbox.value()
        sdrop = ""
        if self.drop_checkbox.isChecked():
            sdrop = "_drop"

        #動画サイズは先頭ファイルで決定し、他は全て同じとする
        file_path = self.file_paths[0]
        if file_path.lower().endswith(SUPPORT_MOVIE_EXT):
            frames = imageio.mimread(file_path, memtest=False)
            height, width, _ = frames[0].shape
        else:
            frame = cv2.imread(file_path)
            height, width, _ = frame.shape

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        output_file = os.path.splitext(file_path)[0] + f"_concati_{fps}fps{sdrop}.mp4"
        out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

        filenum = len(self.file_paths)
        count = 0 
        isFirstFile = True
        for file_path in self.file_paths:
            self.statusBar.showMessage(f"{os.path.basename(file_path)}の結合中({count+1}/{filenum})")
            QApplication.processEvents()

            if file_path.lower().endswith(SUPPORT_MOVIE_EXT):
                frames = imageio.mimread(file_path, memtest=False)
                if not frames: continue # 動画でないファイルであればスキップ（最低でも1frameはあるはず）

                count += 1
                isFirstFrame = True
                for frame in frames:
                    if not isFirstFile and isFirstFrame:
                        isFirstFrame = False
                        continue
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
                    out.write(frame)
            else:
                frame = cv2.imread(file_path)
                out.write(frame)

            isFirstFile = False
        out.release()
        self.proc_end(f"結合完了！({count}ファイル)")

    def to_picfile(self):
        if self.error_check(): return
        if self.cansel_movie_toolong(self.file_paths): return
        self.proc_start()
        filenum = len(self.file_paths)
        count = 0 
        for file_path in self.file_paths:
            self.statusBar.showMessage(f"{os.path.basename(file_path)}の処理中({count+1}/{filenum})")
            QApplication.processEvents()
            if self.convert_movie_to_png(file_path):
                count += 1
        mes = f"処理完了！({count}ファイル)"
        if count == 0:
            mes = f"エラー: webp,mp4ファイルが存在しません"
        elif count != filenum:
            mes = f"{filenum}ファイル中、{count}ファイルを処理しました"
        self.proc_end(mes)

    def cansel_movie_toolong(self, file_paths):
        result = False
        self.statusBar.showMessage(f"入力ファイルをチェック中")
        QApplication.processEvents()
        for file_path in self.file_paths:
            if not file_path.lower().endswith(SUPPORT_MOVIE_EXT): continue
            #framenum = len(imageio.mimread(file_path, memtest=False))
            reader = imageio.get_reader(file_path)
            framenum = reader.get_length()
            #ファイルによってinfが返ってくるので、ちょっと時間がかかるがちゃんとカウントする
            if math.isinf(framenum):
                framenum = sum(1 for _ in reader)
            #print(f"{framenum} frame")
            if framenum > MOVIE_TOOLONG:
                self.statusBar.showMessage(f"デカいファイルあり！中断するのをお勧めします！！")
                QApplication.processEvents()
                result = True
                break
        if result:
            msg01 = f"{MOVIE_TOOLONG}frameを超える動画が含まれます。処理を継続しますか？"
            msg02 = f"長い動画を扱う設計ではないのでメモリを大量に使用しますし、"
            msg03 = f"尋常ではない時間がかかる可能性があります。警告しましたよ？"
            msg04 = f"（4000フレーム程度でもメモリを数GB使用、数分かかります）"
            response = QMessageBox.warning(self, "警告", f"{msg01}\n\n{msg02}\n{msg03}\n{msg04}", QMessageBox.Yes | QMessageBox.No)
            if response != QMessageBox.Yes:
                self.statusBar.showMessage(f"キャンセルしました")
                return True

        return False

    def convert_movie_to_png(self, file_path):
        #画像化はwebpで複数フレームを保持する場合のみ
        if not file_path.lower().endswith(SUPPORT_MOVIE_EXT): return False
        frames = imageio.mimread(file_path, memtest=False)
        if not frames: return False

        padding = len(str(len(frames)))
        if padding < 3: padding = 3
        fbase = os.path.splitext(file_path)[0]
        fext = (os.path.splitext(os.path.basename(file_path))[1]).replace(".", "_")
        picdir = f"{fbase}{fext}_pics"
        if not os.path.exists(picdir):
            os.mkdir(picdir)
        flameno = 0
        picname = f"{os.path.splitext(os.path.basename(file_path))[0]}"
        picname = f"{picdir}/{picname}_frame"
        for frame in frames:
            output_file = f"{picname}{str(flameno).zfill(padding)}.png"
            imageio.imwrite(output_file, frame)
            flameno += 1
        return True

    def load_settings(self):
        geox = pvsubfunc.read_value_from_config(SETTINGS_FILE, GEOMETRY_X)
        geoy = pvsubfunc.read_value_from_config(SETTINGS_FILE, GEOMETRY_Y)
        geow = pvsubfunc.read_value_from_config(SETTINGS_FILE, GEOMETRY_W)
        geoh = pvsubfunc.read_value_from_config(SETTINGS_FILE, GEOMETRY_H)
        if not any(val is None for val in [geox, geoy, geow, geoh]):
            self.setGeometry(geox, geoy, geow, geoh)
        dropchecked = pvsubfunc.read_value_from_config(SETTINGS_FILE, DROP_CHECKED)
        if dropchecked != None:
            self.drop_checkbox.setChecked(dropchecked)
        reversechecked = pvsubfunc.read_value_from_config(SETTINGS_FILE, REVERSE_CHECKED)
        if reversechecked != None:
            self.reverse_checkbox.setChecked(reversechecked)
        loopchecked = pvsubfunc.read_value_from_config(SETTINGS_FILE, LOOP_CHECKED)
        if loopchecked != None:
            self.loop_checkbox.setChecked(loopchecked)
        framerate = pvsubfunc.read_value_from_config(SETTINGS_FILE, FRAME_RATE)
        if framerate != None:
            self.fps_spinbox.setValue(framerate)

    def save_settings(self):
        pvsubfunc.write_value_to_config(SETTINGS_FILE, GEOMETRY_X, self.geometry().x())
        pvsubfunc.write_value_to_config(SETTINGS_FILE, GEOMETRY_Y, self.geometry().y())
        pvsubfunc.write_value_to_config(SETTINGS_FILE, GEOMETRY_W, self.geometry().width())
        pvsubfunc.write_value_to_config(SETTINGS_FILE, GEOMETRY_H, self.geometry().height())
        pvsubfunc.write_value_to_config(SETTINGS_FILE, DROP_CHECKED, self.drop_checkbox.isChecked())
        pvsubfunc.write_value_to_config(SETTINGS_FILE, REVERSE_CHECKED, self.reverse_checkbox.isChecked())
        pvsubfunc.write_value_to_config(SETTINGS_FILE, LOOP_CHECKED, self.loop_checkbox.isChecked())
        pvsubfunc.write_value_to_config(SETTINGS_FILE, FRAME_RATE, self.fps_spinbox.value())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WebpAnim2Mp4()
    window.show()
    sys.exit(app.exec_())
