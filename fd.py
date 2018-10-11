import matplotlib.pyplot as plt
import datetime
import oandapy

def pause_plot():
    fig, ax = plt.subplots(1, 1) #行数、列数1,1のオブジェクト生成
    x_time = [datetime.datetime.now()]
    #oandapyの設定
    oanda = oandapy.API(environment="practice", access_token="e777fc0c0a7aedb89e00f91e15a7b415-ac361a890d2fa25b195ba4dbe825f38b")
    response = oanda.get_prices(instruments='USD_JPY')
    print(type(response))
    prices = response.get('prices')
    asking_price = prices[0].get('ask')
    #ｙにレート入力
    y = [asking_price]
    # 初期化的に一度plotしなければならない
    # そのときplotしたオブジェクトを受け取る受け取る必要がある．
    # listが返ってくるので，注意
    lines,= ax.plot(x_time, y)
    # グラフのフォーマットの設定
    cnt = 0
    plt.grid(True)
    # ここから無限にplotする
    while True:
        cnt +=1
        # plotデータの更新
        response = oanda.get_prices(instruments='USD_JPY')
        prices = response.get('prices')
        asking_price = prices[0].get('ask')
        x_time.append(datetime.datetime.now())
        y.append(asking_price)
        print(asking_price)

        # 描画データを更新するときにplot関数を使うと
        # lineオブジェクトが都度増えてしまうので，注意．
        #
        # 一番楽なのは上記で受け取ったlinesに対して
        # set_data()メソッドで描画データを更新する方法．
        lines.set_data(x_time, y)

        # set_data()を使うと軸とかは自動設定されないっぽいので，
        # そのためx軸の範囲は適宜修正してやる必要がある．
        ax.set_xlim(datetime.datetime.now() - datetime.timedelta(seconds=1000),datetime.datetime.now() + datetime.timedelta(seconds=10))
        if cnt > 2:
            plt.ylim(min(y)-0.01, max(y)+0.01)
        
        # 一番のポイント
        # - plt.show() ブロッキングされてリアルタイムに描写できない
        # - plt.ion() + plt.draw() グラフウインドウが固まってプログラムが止まるから使えない
        # ----> plt.pause(interval) これを使う!!! 引数はsleep時間
        plt.pause(1)
        if cnt > 100000:
            plt.close()
            break
        

if __name__ == "__main__":
    pause_plot()
