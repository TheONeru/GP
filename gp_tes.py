import copy
#pickleといってデータをバイナリ列にすることでオブジェクトを保存する手法がある
#
#__anyting()__ってのは特殊メソッドであらかじめ決められた動作をする
class te(list):
    def __init__(self, content):
        list.__init__(self, content)
    def __deepcopy__(self, memo): #これを実装しないとcopy.deepcopy使えない
        new = self.__class__(self) #型コピー
        new.__dict__.update(copy.deepcopy(self.__dict__, memo)) #deepcopy実装の基本
        return new

t=te('3')
print(t)
print(t.__class__)
b=t.__deepcopy__
print(b)
class ts(list):
    def __init__(self, s, f):
        self.s=s
        self.f=f

s=ts(2,3)
print(s.__dict__)
