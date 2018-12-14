import random
from collections import defaultdict
from inspect import isclass
import sys
_type_ = object

##############
#    Tree    #
##############

class Fitness(object):
    
    def __init__(self, values=[]):
        self.values = values

class PrimitiveTree(list):
    
    def __init__(self, contents):
        self.fitness = Fitness()
        list.__init__(self, contents)

    def __str__(self):
        string = ""
        stack = []
        for node in self:
            stack.append((node, []))
            while len(stack[-1][1]) == stack[-1][0].arity:
                prim, args = stack.pop()
                string = prim.format(*args)
                if len(stack) == 0:
                    break
                stack[-1][1].append(string)

        return string       
        
    def height(self):
        stack = [0]
        max_depth = 0
        for ind in self:
            depth = stack.pop()
            max_depth = max(max_depth, depth)
            stack.extend([depth+1] * ind.arity)
        return max_depth

########################
#    PrimitiveClass    #
########################
class Primitive(object):
    def __init__(self, name, args, ret_type):
        self.name = name
        self.args = args
        self.ret = ret_type
        self.arity = len(args)
        args = ", ".join(map("{{{0}}}".format, list(range(self.arity))))
        self.seq = "{name}({args})".format(name=self.name, args=args)

    def format(self, *args):
        return self.seq.format(*args)

class Terminal(object):
    def __init__(self, terminal, symbolic, ret_type):
        self.value = terminal
        self.arity = 0
        self.name = str(terminal)
        self.ret = ret_type
        self.conv_fct = str if symbolic else repr

    def format(self):
        return self.conv_fct(self.value)


class Ephemeral(Terminal):
    def __init__(self):
        Terminal.__init__(self, self.func(), ret_type=_type_, symbolic=False)

    @staticmethod
    def func():
        return random.random()

######################
#    setPrimitive    #
######################
class setPrimitive(object):
    
    def __init__(self, name, in_type, ret_type, x='X'):
        self.terminal = {}#defaultdict(list)
        self.primitive = {}#defaultdict(list)
        self.prim_cnt = 0
        self.term_cnt = 0
        self.context = {"__builtins__" : None}
        self.name = name
        self.ret = ret_type
        self.x = x
        self.args = []
        for i, type_ in enumerate(in_type):
            arg_str = "{x}{index}".format(x=x, index=i)
            self.args.append(arg_str)
            term = Terminal(arg_str, True, type_)
            self._add(term)
            self.term_cnt += 1

        ephe = Ephemeral()
        self._add(ephe)
        self.term_cnt += 1

    def _add(self, content):
        def addType(dict_, ret_type):
            if not ret_type in  dict_:
                new_list = []
                for type_, list_ in list(dict_.items()):
                    for item in list_:
                        if not item in new_list:
                            new_list.append(item)
                dict_[ret_type] = new_list
                
        #確認ret_typeがあるかどうかの
        addType(self.primitive, content.ret)
        addType(self.terminal, content.ret)

        #objectの元のリストを取得
        if isinstance(content, Primitive):
            for type_ in content.args:
                #in_typeあるかの確認
                addType(self.primitive, type_)
                addType(self.terminal, type_)
            dict_ = self.primitive
        else:
            dict_ = self.terminal

        #objectの追加
        for type_ in dict_:
            dict_[type_].append(content)
            
    def addPrimitive(self, primitive, args,ret_type, name=None):
        if name == None:
            name = primitive.__name__
            
        prim = Primitive(name, args, ret_type)
        self.context[prim.name] = primitive #ここはコンパイルしたあとのgrobal値に使う
        self._add(prim)
        self.prim_cnt += 1

    def addTerminal(self, terminal, ret_type, name=None):
        if name == None:
            name = terminal.__name__

        term = Terminal(name, True, ret_type)#######
        self._add(term)
        self.term_cnt += 1


    def addEphemeral(self, name, ephemeral, ret):

        self._add(class_)
        self.term_cnt += 1
        

class PrimitiveSet(setPrimitive):
    def __init__(self, name, arity):
        args = [_type_]*arity
        setPrimitive.__init__(self, name, args, _type_)

    def addPrimitive(self, primitive, arity, name=None):
        args = [_type_]*arity
        setPrimitive.addPrimitive(self, primitive, args, _type_, name)

    def addTerminal(self, terminal, name=None):
        setPrimitive.addTerminal(self, terminal, _type_, name)

    def addEphemeral(self, name, ephemeral):
        setPrimitive.addEphemeral(self, name, ephemeral,  _type_)


#####################
#   generateTree    #
#####################
def generateTree(max_h, pset, min_h=1):
    generate_prob = 0.2
    def condition(min_height, max_height, depth):
        if ( (depth > min_height) and (random.random() < generate_prob) ) or depth == max_height :
            return True
        else:
            return False
    return generatePrimitiveTree(max_h, pset, condition, min_h=1)

def generatePrimitiveTree(max_h, pset, condition, min_h=1):
    height = random.randint(min_h, max_h)
    type_ = pset.ret
    expr = []
    stack = [(0, type_)]
    while len(stack) != 0:
        depth, type_ = stack.pop()
        if condition(min_h, max_h, depth):
            term = random.choice(pset.terminal[type_])
            if isclass(term):
                term = term()
            expr.append(term)
        else:
            prim =  random.choice(pset.primitive[type_])
            expr.append(prim)
            for arg in reversed(prim.args):
                stack.append((depth+1, arg))

    return expr

################################
#   交叉、突然変異使用関数     #
################################

def Put_in(ind, index, node):
    while True:
        if len(node) == 0:
            break
        value = node.pop(0)
        ind.insert(index, value)
        index += 1
    return ind

def Pop_out(ind, index):
    ret_node = []
    stack = []
    try:
        while True:
            node = ind.pop(index)
            stack.append((node, []))
            while len(stack[-1][1]) == stack[-1][0].arity:
                prim, in_type = stack.pop()
                if prim.arity > 0:
                    ret_node.insert(0, prim)
                else:
                    ret_node.append(prim)

                stack[-1][1].append(1)

                if len(stack) == 0:
                    raise Exception()
    except:
        return ind, ret_node

        

#################
#    compile    #
#################
def compile(expr, pset):
    
    code = str(expr)
    if len(pset.args) > 0:
        args = ",".join(arg for arg in pset.args)
        code = "lambda {args}: {code}".format(args=args, code=code)
    try:        
        return eval(code, pset.context)
    except MemoryError:
        _, _, traceback = sys.exc_info()
        raise MemoryError("DEAP : Error in tree evaluation :"
        " Python cannot evaluate a tree higher than 90. "
        "To avoid this problem, you should use bloat control on your "
        "operators. See the DEAP documentation for more information. "
        "DEAP will now abort.").with_traceback(traceback)

#################
#   crossover   #
#################

def Crossover(ind1, ind2):
    if len(ind1) < 2 or len(ind2)< 2:
        return ind1, ind2
    point1 = random.randrange(1,len(ind1))
    point2 = random.randrange(1,len(ind2))

    ind1, node1 = Pop_out(ind1, point1)
    ind2, node2 = Pop_out(ind2, point2)
    ind1 = Put_in(ind1, point1, node2)
    ind2 = Put_in(ind2, point2, node1)

    return ind1,ind2
    
#################    
#   mutation    #            
#################

def Mutation(ind, pset):
    if len(ind) < 2:
        return ind
    index = random.randrange(1, len(ind))
    point = ind[index]
    new_node = generateTree(1, pset)
    ind, old_node = Pop_out(ind, index)
    ind = Put_in(ind, index, new_node)
    return ind

#####################
#   selTournament   #
#####################

def selTournament(pop):
    list_fitness = [pop[0].fitness.values[0]]
    offspring = [pop[0]]
    for ind in pop[1:]:
        if ind.fitness.values[0] < min(list_fitness):#今回は最小化
            list_fitness.insert(0, ind.fitness.values[0])
            offspring.insert(0, ind)
        else:
            list_fitness.append(ind.fitness.values[0])
            offspring.append(ind)
    return list_fitness, offspring
        


