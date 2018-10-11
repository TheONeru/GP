import gpmodule as gp
import numpy as np
import matplotlib.pyplot as plt
import math
import random
import copy
import data_house

pset = gp.PrimitiveSet("main", 2)
value=data_house.Get_Value("test")[0]#訓練データと教師データ
print(len(value))
time= data_house.Get_Time("test")
def add(a, b):
    return a+b

def sub(a, b):
    return a-b

def mul(a, b):
    return a*b

def div(a, b):
    b += 1e-4
    return a/b

def Before3(i):#xはValueの値
    if i>=3:
        return value[i-3]
    else:
        return value[i]

def Before1(i):#xはValueの値
    if i>=1:
        return value[i-1]
    else:
        return value[i]

pset.addPrimitive(add, 2)
pset.addPrimitive(sub, 2)
pset.addPrimitive(mul, 2)
pset.addPrimitive(div, 2)

#何時間前かのデータを平均線として変数で引き渡す。
#比較関数の作成
#これは売買ルール作成のためのprogramだから売買ルールのapiも必要。
#売買の方はfxtradeでやり方（特に注文の方法）を見てみる。
#売買ルールの数式をどう渡すかも考える（ファイルにjson形式のネストとして渡して）
#売買ルールの方で読み込んで貰う形を考えている。

def diff_expr(individual, pset):
    func = gp.compile(individual, pset)
    diff=0
    for i in range(int(len(value)/2)):
        diff +=(value[i] - func(Before1(i), Before3(i)) )**2    
    return diff

def main():
    Gene = 10
    Mut_prob = 0.35
    Cx_prob_1 = 0.6
    Cx_prob_2 = 0.3
    ind_num = 10
    #世代作成
    pop = []
    for x in range(ind_num):
        ind = gp.PrimitiveTree(gp.generateTree(3,pset))
        pop.append(ind)

    #評価値決定
    for ind in pop:
        fitness = diff_expr(ind, pset)
        ind.fitness.values = [fitness]
        
    #評価リストと子孫を作成
    list_fitness, offspring = gp.selTournament(pop)

    print('第0世代',list_fitness[0])
    for i in range(Gene):
        print('第',i+1,'世代')
        
        #交叉
        elite = copy.deepcopy(offspring[0])
        for ind1, ind2 in zip(offspring[2::2], offspring[1::2]):
            sw = random.random()
            if  sw < Cx_prob_2:
                ind1, ind2 = gp.Crossover(ind1, ind2)
            else:
                ind1, ind2 = gp.Crossover(elite, random.choice([ind1, ind2]))#最優秀と交叉

        #突然変異
        for mut in offspring[1:]:
            if random.random() < Mut_prob:
                mut = gp.Mutation(mut, pset)

        #評価値決定
        for ind in offspring:
            del ind.fitness.values[0]
            fitness = diff_expr(ind, pset)
            ind.fitness.values = [fitness]

        pop[:] = offspring[:]
        
        #評価リストと子孫を作成
        list_fitness, offspring = gp.selTournament(pop)
        if list_fitness[0] == 0:
            break
        
        print("Min", min(list_fitness))

    print("finish")
    print("Best individual is", offspring[0])
    print("fitness",list_fitness[0])
    return offspring, list_fitness

if __name__ == "__main__":
    offspring, list_fitness = main()
    func = gp.compile(offspring[0], pset)
    plt.plot(time, value, label="Real Data")
    forecast = []
    
    for i in range(len(value)):
        forecast.append(func(Before1(i),Before3(i)))
                        
    plt.plot(time, forecast, label="Forecast Data")
    for i in range(2500, 2700):
        print(forecast[i], value[i])
    plt.legend()
    plt.show()
                        
    
