import sys
import os
import imageio.v2 as imageio
import cv2
import numpy as np
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QIcon
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog,
    QSpinBox, QCheckBox, QListWidget, QHBoxLayout, QStatusBar, QMainWindow
)
from PyQt5.QtCore import Qt
import pvsubfunc

WINDOW_TITLE = "WebP Anim to MP4 Converter"
SETTINGS_FILE = "WebpAnim2Mp4.json"
GEOMETRY_X = "geometry-x"
GEOMETRY_Y = "geometry-y"
LOOP_CHECKED = "loop-checked"
DROP_CHECKED = "drop-checked"
FRAME_RATE = "frame-rate"
APP_WIDTH = 480
APP_HEIGHT = 320
DEF_FRAME_RATE = 15

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
        self.file_list = QListWidget(self)  # ファイルリスト
        self.layout.addWidget(self.file_list)

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
        self.drop_checkbox = QCheckBox("drop last frame", self)
        self.settingLayout2.addWidget(self.drop_checkbox)
        self.settingLayout2.addStretch()
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
        self.button_clear = QPushButton('クリア')
        self.button_clear.setFixedHeight(40)  # ボタンの高さを調整
        self.buttonLayout.addWidget(self.button_clear)
        self.layout.addLayout(self.buttonLayout)
        self.setLayout(self.layout)

        self.button_concatinate.clicked.connect(self.concatinate_files)
        self.button_lastpic.clicked.connect(self.to_file_lastpic)
        self.button_convert.clicked.connect(self.convert_files)
        self.button_clear.clicked.connect(self.clear_files)
        for i in range(len(FRAME_LIST)):
            self.convertBtns[i].clicked.connect(lambda _, i=i: self.fps_spinbox.setValue(FRAME_LIST[i]))

        self.statusBar = QStatusBar()
        self.statusBar.setStyleSheet("color: white; font-size: 14px; background-color: #31363b;")
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage(f"WebPのアニメーションファイルをドラッグドロップしてください")

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
        #連結を考慮していちいちクリアするのをやめる
        #self.file_list.clear()
        #self.file_paths = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            #連結を考慮して重複チェックもやめる（同じファイルを連結する意味あるかな？）
            #if file_path.lower().endswith(".webp") and file_path not in self.file_paths:
            if file_path.lower().endswith(".webp"):
                self.file_paths.append(file_path)
                self.file_list.addItem(os.path.basename(file_path))

    def error_check(self):
        result = False
        if not self.file_paths:
            self.statusBar.showMessage(f"エラー: ファイルが選択されていません")
            return True

    def proc_start(self):
        self.setEnabled(False)
        QApplication.processEvents()

    def proc_end(self, mes):
        self.setEnabled(True)
        self.statusBar.showMessage(mes)

    def convert_files(self):
        if self.error_check(): return
        self.proc_start()
        fps = self.fps_spinbox.value()
        for file_path in self.file_paths:
            self.statusBar.showMessage(f"{os.path.basename(file_path)}の変換中")
            QApplication.processEvents()
            self.convert_webp_to_mp4(file_path, fps)
        self.proc_end(f"変換完了！")

    def convert_webp_to_mp4(self, file_path, fps):
        frames = imageio.mimread(file_path)
        if not frames: return

        sloop = ""
        # ループ処理: 0,1,2...30 → 0,1,2...30,29,28...2,1 に変換
        if self.loop_checkbox.isChecked():
            frames += frames[-2::-1]  # 逆順のフレームを追加（最後のフレームは重複しないよう -2 から）
            sloop = "_loop"

        height, width, _ = frames[0].shape
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")

        output_file = os.path.splitext(file_path)[0] + f"_{fps}fps{sloop}.mp4"
        out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

        for frame in frames:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
            out.write(frame)

        out.release()

    def clear_files(self):
        self.file_list.clear()
        self.file_paths = []
        self.statusBar.showMessage(f"リストをクリアしました")

    def concatinate_files(self):
        if self.error_check(): return
        self.proc_start()
        fourcc = None
        fps = self.fps_spinbox.value()

        sdrop = ""
        if self.drop_checkbox.isChecked():
            sdrop = "_drop"
        isLastFile = False
        i = 0
        for file_path in self.file_paths:
            if i == len(self.file_paths) - 1:
                isLastFile = True
            i += 1
            self.statusBar.showMessage(f"{os.path.basename(file_path)}の結合中")
            QApplication.processEvents()
            frames = imageio.mimread(file_path)
            if not frames: continue # 動画でないファイルであればスキップ
            if fourcc == None:
                height, width, _ = frames[0].shape
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                output_file = os.path.splitext(file_path)[0] + f"_concati_{fps}fps{sdrop}.mp4"
                out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))
            j = 0
            for frame in frames:
                if not isLastFile:
                    if self.drop_checkbox.isChecked() and j == len(frames) - 1:
                        break #最終フレームをスキップ（ただし最終ファイルは除く）
                j += 1
                frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
                out.write(frame)

        out.release()
        self.proc_end(f"結合完了！")

    def convert_webp_to_mp4(self, file_path, fps):
        frames = imageio.mimread(file_path)
        if not frames: return

        sloop = ""
        # ループ処理: 0,1,2...30 → 0,1,2...30,29,28...2,1 に変換
        if self.loop_checkbox.isChecked():
            #frames += frames[-2::-1]  # 逆順のフレームを追加（最後のフレームは重複しないよう -2 から）
            frames += frames[len(frames)-2:1:-1] #上記の指定だと最後に0フレーム目が被ってる
            sloop = "_loop"

        height, width, _ = frames[0].shape
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")

        output_file = os.path.splitext(file_path)[0] + f"_{fps}fps{sloop}.mp4"
        out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

        for frame in frames:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
            out.write(frame)

        out.release()

    def to_file_lastpic(self):
        if self.error_check(): return
        self.proc_start()
        for file_path in self.file_paths:
            self.statusBar.showMessage(f"{os.path.basename(file_path)}の処理中")
            QApplication.processEvents()
            self.convert_webp_to_lastpng(file_path)
        self.proc_end(f"処理完了！")

    def convert_webp_to_lastpng(self, file_path):
        frames = imageio.mimread(file_path)
        if not frames: return

        height, width, _ = frames[0].shape
        lastframe = len(frames) - 1
        output_file = os.path.splitext(file_path)[0] + f"_{lastframe}frame.png"
        imageio.imwrite(output_file, frames[lastframe])

    def load_settings(self):
        geox = pvsubfunc.read_value_from_config(SETTINGS_FILE, GEOMETRY_X)
        geoy = pvsubfunc.read_value_from_config(SETTINGS_FILE, GEOMETRY_Y)
        if not any(val is None for val in [geox, geoy]):
            self.setGeometry(geox, geoy, APP_WIDTH, APP_HEIGHT)
        dropchecked = pvsubfunc.read_value_from_config(SETTINGS_FILE, DROP_CHECKED)
        if dropchecked != None:
            self.drop_checkbox.setChecked(dropchecked)
        loopchecked = pvsubfunc.read_value_from_config(SETTINGS_FILE, LOOP_CHECKED)
        if loopchecked != None:
            self.loop_checkbox.setChecked(loopchecked)
        framerate = pvsubfunc.read_value_from_config(SETTINGS_FILE, FRAME_RATE)
        if framerate != None:
            self.fps_spinbox.setValue(framerate)

    def save_settings(self):
        pvsubfunc.write_value_to_config(SETTINGS_FILE, GEOMETRY_X, self.geometry().x())
        pvsubfunc.write_value_to_config(SETTINGS_FILE, GEOMETRY_Y, self.geometry().y())
        pvsubfunc.write_value_to_config(SETTINGS_FILE, DROP_CHECKED, self.drop_checkbox.isChecked())
        pvsubfunc.write_value_to_config(SETTINGS_FILE, LOOP_CHECKED, self.loop_checkbox.isChecked())
        pvsubfunc.write_value_to_config(SETTINGS_FILE, FRAME_RATE, self.fps_spinbox.value())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WebpAnim2Mp4()
    window.show()
    sys.exit(app.exec_())
