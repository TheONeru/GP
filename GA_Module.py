import random

def Cross(ind1, ind2):#complete
    slice1=random.randint(0, len(ind1)-1)
    slice2=random.randint(0, len(ind2)-1)
    print(slice1, slice2)
    if slice1>slice2:
        temp=ind1[slice2:slice1+1]
        ind1[slice2:slice1+1]=ind2[slice2:slice1+1]
        ind2[slice2:slice1+1]=temp
    elif slice1<slice2:
        temp=ind1[slice1:slice2+1]
        ind1[slice1:slice2+1]=ind2[slice1:slice2+1]
        ind2[slice1:slice2+1]=temp

    return ind1, ind2


def r(n):
    rr=[]
    for i in range(n):
        v=random.randint(0, 1)
        rr.append(v)
    return rr

i=r(10)
e=r(10)
print(i)
print(e)
i, e=Cross(i, e)
print(i)
print(e)
