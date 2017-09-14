#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""executeJSメソッドの使用例"""

import qi
import argparse
import sys
import time


def main(session):
    """
    この例はexecuteJSメソッドを使用します。
    ALTabletServiceを使うために、ロボット上でスクリプトを動かしてください。
    """
    # ALTabletServiceの取得

    try:
        tabletService = session.service("ALTabletService")
        # session.connect("tcp://198.18.0.1:9559")

        # boot-config/htmlフォルダにあるhtmファイルを表示
        # タブレットから見たロボットのIPアドレスは198.18.0.1
        tabletService.showWebview("http://198.18.0.1/apps/boot-config/preloading_dialog.html")

        time.sleep(3)

        # プロンプトを表示するためのjavascript
        # ALTabletBindingタブレット上に表示されたウェブページで動くjavascriptバインディングです。
        script = """
            var name = prompt("Please enter your name", "uvahome");
            ALTabletBinding.raiseEvent(name)
        """

        # 最後にはシグナルを切断してください。
        signalID = 0

        # JSEvent上で関数ALTabletBinding.raiseEventによって、シグナルが動いた時に呼ばれる関数
        def callback(event):
            print "your name is: ", event

            # ウェブビューの非表示
            tabletService.hideWebview()
            # シグナルの切断
            tabletService.onJSEvent.disconnect(signalID)

        # JSEventシグナル上のコールバック関数にアタッチ
        signalID = tabletService.onJSEvent.connect(callback)

        # タブレット上に表示されているウェブページにjavascriptを挿入し実行
        tabletService.executeJS(script)

    except Exception, e:
        print "Error was: ", e


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    main(session)
