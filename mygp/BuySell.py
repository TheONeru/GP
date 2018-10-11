import data_house
import random
import numpy as np
import matplotlib.pyplot as plt

#bitは売り値
#askは買値
close_, high, low=data_house.Get_Value("test")#訓練データと教師データ 5秒ごと5000個
close=close_
#0.04円 bitとaskの差

#金額の変化は全部close 基本はclose
#highとかが乖離が激しいとこれ以上は下がらない（上がらない）サインのため
#hith(t)<close(i) + Benefit*spred[i]を超えたら決済にする

#買いの基本システム完成、　売値と買値の区別だけ本番環境とシミュレーション環境
#変更したほうがよさげ。あとはRSI以外の手法のシグナルの出力とGA環境をつくってシミュレーション

class Ind():
    #GTYPEは各成分が逆から読むことに注意
    #RSI_Short_Up = 5bit[0:5]
    #RSI_Short_Down = 5bit[5:10]
    #RSI_Short_Term = 3bit[10:13] 2^2 + 2^1 + 2^0 + 12(固定)
    #RSI_Long_Up = 5bit[13:18]
    #RSI_Long_Down = 5bit[18:23]
    #RSI_Long_Term = 3bit[23:26]2^2 + 2^1 + 2^0 + 30(固定)
    #RSI_Buy_Benefit = 5bit[26:31]
    #RSI_Buy_LossCut = 5bit[31:37]

    def __init__(self, GTYPE):
        self.asset = 10000000#持ち金
        self.position = False#position
        self.spred=0.04#最大のスプレッド(実際は可変)
        self.position_type=None
        self.start_value = None
        self.Volarity=None
        self.cross = 0
        self.DD=[]#DrawDown
        self.Leverage=100000
        
        self.Short_RSI=[]
        self.Long_RSI=[]
        self.RSI_Short_Up=50
        self.RSI_Short_Down=0
        self.RSI_Long_Up=50
        self.RSI_Long_Down=0
        self.RSI_Short_Term=2
        self.RSI_Long_Term=16
        self.Buy_Benefit=0.2
        self.Buy_LossCut=2
        self.up_k = random.random()
        self.down_k = random.random()
        
        for i in range(5):
            if GTYPE[0+i]:
                self.RSI_Short_Up += 2**i*1.5625
            if GTYPE[5+i]:
                self.RSI_Short_Down += 2**i*1.5625
            if GTYPE[13+i]:
                self.RSI_Long_Up += 2**i*1.5625
            if GTYPE[18+i]:
                self.RSI_Long_Down += 2**i*1.5625
            if GTYPE[26+i]:
                self.Buy_Benefit += 2**i
            if GTYPE[31+i]:
                self.Buy_LossCut += 2**i

        for i in range(3):
            if GTYPE[10+i]:
                self.RSI_Short_Term += 2**i
            elif GTYPE[23+i]:
                self.RSI_Long_Term += 2**i
        #print(self.Buy_Benefit)
        #print(self.Buy_LossCut)
        #print(self.RSI_Short_Term)
        #print(self.RSI_Long_Term)
        

    def Check_Position(self, x, index):
        if self.position:
            self.Out_PositionCheck(x, index)
        else:
            self.Get_PositionCheck(x, index)
            
    def Get_Position(self, signal, index, length):
        if signal==0:
            self.position=True
            self.position_type=signal
            self.start_value=close[index]
            self.asset -= self.Leverage*(self.start_value)
            self.Volarity=self.CulcVola(index, length)
            #print(self.Volarity)
            self.cross += 1
        elif signal==1:
            self.position=True
            self.position_type=signal
            self.start_value=close[index]-self.spred
            self.asset += self.Leverage*(self.start_value)
            self.Volarity=self.CulcVola(index, length)
            #print(self.Volarity)
            self.cross += 1            

    def CulcVola(self, index, length):
        #売値買値の処理もうちょっと考えて
        ave=sum(close[index-(length-1):index+1])/length
        std=np.std(close[index-(length-1):index+1])
        return std/ave
        

    def CulcRSI(self, index, length, signal):
        #signal=0 is buy, signal=1 is sell
        #計算確認する
        #
        Un=0
        Dn=0
        for i in range(index-(length-1), index+1):
            if i==0:
                pass
            else:
                s = (close[i]-close[i-1])
                if s>0:
                    Un += s
                elif s<0:
                    Dn -= s
        try:
            RSI = 100*Un/(Dn + Un)
            return RSI
        except:
            return 50
    
    def Get_PositionCheck(self, x, index=None):#xは単純にcloseの値にする
        if index==None:
            index=close[0].index(x)
        if len(self.Short_RSI)<=self.RSI_Short_Term or len(self.Long_RSI)<=self.RSI_Long_Term:
            RSI=self.CulcRSI(index, index+1, signal=0)
            self.Short_RSI.append( RSI )
            self.Long_RSI.append( RSI )
        else:
            #変更のよちあり
            S_RSI=self.CulcRSI(index, self.RSI_Short_Term, signal=0)
            self.Short_RSI.append( S_RSI )
            #self.Short_RSI.pop(0)

            L_RSI=self.CulcRSI(index, self.RSI_Long_Term, signal=0)
            self.Long_RSI.append( L_RSI )
            #self.Long_RSI.pop(0)
            
            if self.Short_RSI[-1]<self.RSI_Short_Up and self.Short_RSI[-1]>self.RSI_Short_Down:
                if self.Long_RSI[-1]<self.RSI_Long_Up and self.Long_RSI[-1]>self.RSI_Long_Down:
                    if self.Short_RSI[-1]>self.Long_RSI[-1]:
                        if self.Short_RSI[-2]<self.Long_RSI[-2]:
                            self.Get_Position(0, index, index+1)#買い                            
                    elif self.Short_RSI[-1]<self.Long_RSI[-1]:
                        if self.Short_RSI[-2]>self.Long_RSI[-2]:
                            self.Get_Position(1, index, index+1)

    def Out_Position(self,index):
        if self.position_type==0:
            self.asset += self.Leverage*(close[index]-self.spred)
        elif self.position_type==1:
            self.asset -= self.Leverage*(close[index])
        self.position=False
        self.position_type=None
        self.start_value=None

    def Out_PositionCheck(self, x,index=None):
        if index==None:
            index=close.index(x)
        if self.position_type==0:
            if close[index]-self.spred>(self.start_value + self.Buy_Benefit/10):
                print("a",self.asset)
                self.Out_Position(index)
                print("b",self.asset)
            elif low[index]-self.spred<(self.start_value - self.Buy_LossCut/10):
                self.Out_Position(index)
                print("c",self.asset)
        elif self.position_type==1:
            if close[index]<(self.start_value - self.Buy_Benefit/10):
                print("d",self.asset)
                self.Out_Position(index)
                print("e",self.asset)
            elif high[index]>(self.start_value + self.Buy_LossCut/10):
                self.Out_Position(index)
                print("f",self.asset)
                
def r(n):
    rr=[]
    for i in range(n):
        v=random.randint(0, 1)
        rr.append(v)
    return rr

#gtype=r(37)
#ind=Ind(gtype)
pop=[]
for i in range(100):
    ind=Ind(r(37))
    pop.append(ind)

for j in pop:
    for i in range(len(close)):
        j.Check_Position(close[i], index=i)

for i in pop:
    if i.position:
        if i.position_type==0:
            i.asset +=i.Leverage*i.start_value
        elif i.position_type==1:
            i.asset -=i.Leverage*(i.start_value)
    print(i.asset)


#plt.plot(range(len(close)), close)
#plt.show()

