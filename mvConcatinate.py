import argparse
import os
import sys
from typing import NamedTuple, List
import imageio.v2 as imageio
import cv2

class Args(NamedTuple):
    inputs: List[str]
    output: str
    loop: bool
    fps: int

def make_default_output(file: str) -> str:
    base = os.path.basename(file)
    name, ext = os.path.splitext(base)
    dir_path = os.path.dirname(file)
    output = os.path.join(dir_path, f"{name}_out.mp4")
    return output

def chech_moviefile(file):
    base = os.path.basename(file)
    name, ext = os.path.splitext(base)
    if ext in (".mp4", ".webp"):
        return True
    return False

def parse_args(argv=None) -> Args:
    p = argparse.ArgumentParser(description="可変個の入力ファイルを扱うスケルトン")
    p.add_argument("inputs", nargs="+", help="入力ファイル（2個以上）")
    p.add_argument("-o", "--output", help="出力ファイル（オプション）")
    p.add_argument("-l", "--loop", action="store_true", help="オプション：指定すれば ON")
    p.add_argument("-fps", type=int, default=15, help="fps（デフォルト15）")

    ns = p.parse_args(argv)

    # 入力ファイル数が2未満の場合はエラーにする
    if len(ns.inputs) < 2:
        p.error("入力ファイルは 2 個以上指定してください")

    output = ns.output if ns.output else make_default_output(ns.inputs[0])
    return Args(inputs=ns.inputs, output=output, loop=ns.loop, fps=ns.fps)

def process_files(inputs: List[str], output: str, loop: bool, fps: int) -> int:
    print("----------------------")
    print(f"以下のパラメータで動画の結合処理を開始します")
    print(f"inputs : {inputs}")
    print(f"output : {output}")
    print(f"loop   : {'ON' if loop else 'OFF'}")
    print(f"fps    : {fps}")
    print("----------------------")

    #動画サイズは先頭ファイルで決定し、他は全て同じとする
    firstfile = inputs[0]
    frames = imageio.mimread(firstfile, memtest=False)
    height, width, _ = frames[0].shape

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output, fourcc, fps, (width, height))

    filenum = len(inputs)
    count = 0
    isFirstFile = not loop
    for file_path in inputs:
        if not os.path.exists(file_path): continue  #一応なかった時はスキップ

        print(f"{os.path.basename(file_path)}の結合中({count+1}/{filenum})")

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

        isFirstFile = False

    out.release()
    print(f"結合完了！({count}ファイル)")

    return 0


def main(argv=None):
    try:
        args = parse_args(argv)

        # 入力ファイル存在チェック
        for path in args.inputs:
            if not os.path.exists(path):
                print(f"Error: 入力ファイルが見つかりません: {path}", file=sys.stderr)
                return 2
            elif not chech_moviefile(path):
                print(f"Error: 入力ファイルが動画ファイルではありません: {path}", file=sys.stderr)
                return 3

        rc = process_files(args.inputs, args.output, args.loop, args.fps)
        return rc

    except Exception as e:
        print(f"予期しないエラー: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
