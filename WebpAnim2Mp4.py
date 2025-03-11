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

#良く使いそうなフレームレートをボタンで選択可能としておく
FRAME_LIST = (10,15,30,60)

class WebpAnim2Mp4(QMainWindow):
    def __init__(self):
        super().__init__()

        # ウィンドウ設定
        self.setWindowTitle("WebP Anim to MP4 Converter")
        self.setGeometry(100, 100, 480, 320)
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
        self.loop_checkbox = QCheckBox("loop", self)
        self.settingLayout1.addWidget(self.loop_checkbox)
        self.settingLayout1.addStretch()
        self.settingLayout1.addWidget(QLabel("frame:", self))
        self.convertBtns = []
        for i in range(len(FRAME_LIST)):
            self.convertBtns.append(QPushButton(str(FRAME_LIST[i])))
            self.convertBtns[i].setFixedWidth(32)
            self.settingLayout1.addWidget(self.convertBtns[i])
        self.fps_spinbox = QSpinBox(self)
        self.fps_spinbox.setRange(1, 240)
        self.fps_spinbox.setValue(15)
        self.fps_spinbox.setFixedWidth(64)
        self.settingLayout1.addWidget(self.fps_spinbox)
        self.layout.addLayout(self.settingLayout1)

        self.buttonLayout = QHBoxLayout()
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

        self.button_convert.clicked.connect(self.convert_files)
        self.button_clear.clicked.connect(self.clear_files)
        for i in range(len(FRAME_LIST)):
            self.convertBtns[i].clicked.connect(lambda _, i=i: self.fps_spinbox.setValue(FRAME_LIST[i]))

        self.statusBar = QStatusBar()
        self.statusBar.setStyleSheet("color: white; font-size: 14px; background-color: #31363b;")
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage(f"WebPのアニメーションファイルをドラッグドロップしてください")

        self.file_paths = []  # ファイルパスのリスト

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        self.file_list.clear()
        self.file_paths = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith(".webp") and file_path not in self.file_paths:
                self.file_paths.append(file_path)
                self.file_list.addItem(os.path.basename(file_path))

    def convert_files(self):
        if not self.file_paths:
            self.statusBar.showMessage(f"エラー: ファイルが選択されていません")
            return

        self.setEnabled(False)
        QApplication.processEvents()
        fps = self.fps_spinbox.value()
        for file_path in self.file_paths:
            self.statusBar.showMessage(f"{file_path}の変換中")
            QApplication.processEvents()
            self.convert_webp_to_mp4(file_path, fps)

        self.setEnabled(True)
        self.statusBar.showMessage(f"変換完了！")

    def clear_files(self):
        self.file_list.clear()
        self.file_paths = []
        self.statusBar.showMessage(f"リストをクリアしました")

    def convert_webp_to_mp4(self, file_path, fps):
        frames = imageio.mimread(file_path)
        if not frames:
            return

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WebpAnim2Mp4()
    window.show()
    sys.exit(app.exec_())
