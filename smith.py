from sympy.ntheory import multinomial
from pprint import pprint
from sklearn.linear_model import LinearRegression
import time
from math import factorial

def dig_sum_GT(n):
    return sum(int(x) for x in str(n))

def dig_sum(n):
    tot = 0
    cut = 10000
    cut_num = 10**100
    #i = 0
    while n != 0:
        #i += 1
        #print(i)
        tail = n % cut_num
        tot += dig_sum_GT(tail)
        n = n // cut_num
    return tot

def trinomial(n):
    return multinomial.multinomial_coefficients_iterator(3, n)


def palin_pow_pos_GT(power, pos, a=1, b=1, c=1):
    tot = 0
    #print("Pos:", pos)
    for inds, coef in trinomial(power):
        if pos == inds[0]*2 + inds[1]:
            #print("Inds:", inds, "Coef:", coef)
            tot += coef*(a**inds[0]) * (b**inds[1]) * (c**inds[2])
    #print("-"*10)
    return tot

def trinom_coef(power, i, j, k):
    return factorial(power)//factorial(i)//factorial(j)//factorial(k)
    tot = 1
    for n in range(i + 1, power + 1):
        tot *= n
    for n in range(1, j+1):
        tot = tot // n
    for n in range(1, k+1):
        tot = tot // n
    return tot


def palin_pow_pos(power, pos, a=1, b=1, c=1):
    tot = 0

    if pos > power:
        i = pos - power
        j = pos - 2*i
        k = 0
    else:
        i = 0
        j = pos
        k = power - pos
    #print("ijk",i,j,k)

    while j >= 0:
        tot += trinom_coef(power, i,j,k)*(a**i) * (b**j) * (c**k)
        #assert False, (tot, power, pos, i, j, k, trinom_coef(power, i,j,k))
        i += 1
        j -= 2
        k += 1
    return tot

def make_palin(mid_power, a=1, b=1, c=1):
    return a*10**(mid_power*2) + b*10**mid_power + c

def palin_dig_sum_GT(exp, mid_power, a=1, b=1, c=1):
    return dig_sum(make_palin(mid_power, a=a, b=b, c=c)**exp)

def palin_dig_sum_GT2(exp, mid_power, a=1, b=1, c=1):
    return sum(dig_sum(palin_pow_pos_GT(exp, i, a=a, b=b, c=c)) for i in range(2*exp + 1))

def palin_dig_sum(exp, mid_power, a=1, b=1, c=1):
    return sum(dig_sum(palin_pow_pos(exp, i, a=a, b=b, c=c)) for i in range(2*exp + 1))

def smith_diff(exp, mid_power, a=1, b=1, c=1):
    S = palin_dig_sum(exp, mid_power, a=a, b=b, c=c)
    print("Digit Sum:", S)
    SP = exp*(dig_sum(a)+dig_sum(b)+dig_sum(c))
    print("PrDig Sum:", SP)
    print("S - SP:", S -SP)
    print("RESIDUE:", (S-SP)%7)

#palin = make_palin(10, b = 3)

EXP = 237249

GOLDEN = 5000
#GOLDEN = 300

while True:
    S = palin_dig_sum(GOLDEN, EXP, b=999)
    txt = f"Power:  \t{GOLDEN}\nDigit Sum:\t{S}\n"
    SP = GOLDEN*(dig_sum(1)+dig_sum(999)+dig_sum(1))
    txt += f"PrDig Sum:\t{SP}\n"
    txt += f"S - SP: \t{S - SP}\n"
    txt += f"RESIDUE:\t{(S-SP)%7}\n"
    print(txt)
    print()
    with open(f"{GOLDEN}.txt", "w") as f:
        f.write(txt)
    GOLDEN += 1
"""
import matplotlib.pyplot as plt


datas = []

for i in range(1, 200, 10):
    if i%20 == 1:
        print(i)
    start = time.time()
    l = [i**2, palin_dig_sum(i, EXP, b=999)]
    l.append(time.time() - start)
    datas.append(l)


cut = lambda i: [x[i] for x in datas]


reg = LinearRegression()
reg.fit([[x**0.5] for x in cut(2)], cut(1))
pred = lambda x: reg.predict([[x**0.5]])[0]
pprint(reg.__dict__)

plt.axhline(y=10694986, color='r', linestyle='-', label="1987AD, 10,694,986 digits")
plt.axhline(y=13614514, color='r', linestyle='-', label="1990AD, 13,614,514 digits")
plt.axhline(y=32066910, color='r', linestyle='-', label="2001AD, 32,066,910 digits")
plt.plot([x/60 for x in range(0,60*60*2,3)], [pred(x) for x in range(0,60*60*2,3)], label="2022AD, My algorithm ;)")
plt.plot([x/60 for x in cut(2)], cut(1))
#plt.plot([x**.5 for x in cut(0)], cut(1))
plt.title("Largest Known Smith Number")
plt.xlabel("Computation time(Minutes)")
plt.ylabel("Digits")
plt.legend()
#plt.xscale('log')
plt.show()
f = lambda n: len(str(999**n))

reg2 = LinearRegression()
reg2.fit([[x] for x in cut(0)], cut(1))
pred2 = lambda x: int(reg2.predict([[x**2]])[0])
"""
