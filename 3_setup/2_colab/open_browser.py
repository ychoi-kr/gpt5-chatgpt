import datetime
import time
import webbrowser

# 1時間毎に任意のノートブックを開く
for i in range(12):
    browse = webbrowser.get("chrome")
    browse.open("<任意のノートブックのURL>")
    print(i, datetime.datetime.today())
    time.sleep(60*60)
