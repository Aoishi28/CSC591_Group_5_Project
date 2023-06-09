# External imports
import sys, re, math, copy
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from pathlib import Path

# Internal imports
from config import *
from sym import SYM
from Random import *

r = Random()
rand = r.rand
rint = r.rint
set_seed = r.set_seed

def kap(t, fun):
    u = {}
    what = enumerate(t)
    if type(t) == dict:
        what = t.items()
    for k, v in what:
        v, k = fun(k, v)
        if not k:
            u[len(u)] = v
        else:
            u[k] = v
    return u

def dkap(t, fun):
    u = {}
    for k,v in t.items():
        v, k = fun(k,v) 
        u[k or len(u)] = v
    return u

def cosine(a,b,c):
    if c == 0:
        return 0
    return (a ** 2 + c ** 2 - b ** 2) / (2 * c)

def any(t):
    return t[rint(len(t)) - 1]

def create_latex_table(rows):
    first_row = "\\begin{center}\n\\begin{tabular}"
    last_row = "\\end{tabular}\n\\end{center}"
    columns = "c " * len(rows[0])
    columns = "{||" + columns + "||}\n\\hline"
    rows_string = ""
    for row in rows:
        row1 = [str(cell) for cell in row]
        latex_row = " & ".join(row1)
        latex_row = "\n" + latex_row
        rows_string += latex_row
        rows_string += "\n\\hline"
    
    return first_row + columns + rows_string + last_row

def prune(rule, maxSize):
    n=0
    for txt,ranges in rule.items():
        n = n+1
        if len(ranges) == maxSize[txt]:
            n=n+1
            rule[txt] = None
    if n > 0:
        return rule
    
def stats_average(data_array):
    res = {}
    for x in data_array:
        for k,v in x.stats().items():
            res[k] = res.get(k,0) + v
    for k,v in res.items():
        res[k] /= the['n_iter']
    return res

def preprocess_data(file, DATA):
    df = pd.read_csv(file)
    df = impute_missing_values(df)
    label_encoding(df)
    file = file.replace('data', 'preprocessed_data')
    df.to_csv(file, index=False)
    return DATA(file)

def per(t, p):
    p = math.floor(((p or 0.5) * len(t)) + 0.5)
    return t[max(0, min(len(t), p) - 1)]

def settings(s):
    return dict(re.findall("\n[\s]+[-][\S]+[\s]+[-][-]([\S]+)[^\n]+= ([\S]+)",s))

def coerce(s):
    bool_s = s.lower()
    for t in [int, float]:
        try:
            return t(s)
        except ValueError:
            pass
    if bool_s in ["true", "false"]:
        return bool_s == "true"
    return s

def cli(options):
    args = sys.argv[1:]
    for k, v in options.items():
        for n, x in enumerate(args):
            if x == '-'+k[0] or x == '--'+k:
                if v == 'false':
                    v = 'true'
                elif v == 'true':
                    v = 'false'
                else:
                    v = args[n+1]
        options[k] = coerce(v)
    return options

def eg(key, str, fun):
    egs[key] = fun
    global help
    help = help + '  -g '+ key + '\t' + str + '\n'

def rnd(n, nPlaces = 3):
    mult = 10**nPlaces
    return math.floor(n * mult + 0.5) / mult

def csv(sFilename, fun):
    sFilename = Path(sFilename)
    if sFilename.exists() and sFilename.suffix == '.csv':
        t = []
        with open(sFilename.absolute(), 'r', encoding='utf-8') as file:
            for _, line in enumerate(file):
                row = list(map(coerce, line.strip().split(',')))
                t.append(row)
                fun(row)
    else:
        print("File path does not exist OR File not csv, given path: ", sFilename.absolute())
        return

def many(t,n):
    u=[]
    for _ in range(1,n+1):
        u.append(any(t))
    return u

def show(node, what, cols, nPlaces, lvl = 0):
  if node:
    print('|..' * lvl, end = '')
    if not node.get('left'):
        print(node['data'].rows[-1].cells[-1])
    else:
        print(int(rnd(100*node['c'], 0)))
    show(node.get('left'), what,cols, nPlaces, lvl+1)
    show(node.get('right'), what,cols,nPlaces, lvl+1)

def deepcopy(t):
    return copy.deepcopy(t)

def oo(t):
    d = t.__dict__
    d['a'] = t.__class__.__name__
    d['id'] = id(t)
    d = dict(sorted(d.items()))
    print(d)

def cliffsDelta(ns1,ns2):
    if len(ns1) > 256:
        ns1 = many(ns1,256)
    if len(ns2) > 256:
        ns2 = many(ns2,256)
    if len(ns1) > 10*len(ns2):
        ns1 = many(ns1,10*len(ns2))
    if len(ns2) > 10*len(ns1):
        ns2 = many(ns2,10*len(ns1))
    n,gt,lt = 0,0,0
    for x in ns1:
        for y in ns2:
            n = n + 1
            if x > y:
                gt = gt + 1
            if x < y:
                lt = lt + 1
    return abs(lt - gt)/n > the['cliffs']

def showTree(node, what, cols, nPlaces, lvl = 0):
  if node:
    print('|.. ' * lvl + '[' + str(len(node['data'].rows)) + ']' + '  ', end = '')
    if not node.get('left') or lvl==0:
        print(node['data'].stats())
    else:
        print('')
    showTree(node.get('left'), what,cols, nPlaces, lvl+1)
    showTree(node.get('right'), what,cols,nPlaces, lvl+1)

def bins(cols,rowss):
    out = []
    for col in cols:
        ranges = {}
        for y,rows in rowss.items():
            for row in rows:
                x = row.cells[col.at]
                if x != '?':
                    k = int(bin(col,x))
                    if not k in ranges:
                        ranges[k] = RANGE(col.at,col.txt,x)
                    extend(ranges[k], x, y)
        ranges = list(dict(sorted(ranges.items())).values())
        r = ranges if isinstance(col, SYM) else mergeAny(ranges)
        out.append(r)
    return out

def bin(col,x):
    if x=='?' or isinstance(col, SYM):
        return x
    tmp = (col.hi - col.lo)/(the['bins'] - 1)
    return  1 if col.hi == col.lo else math.floor(x/tmp + .5)*tmp

def merge(col1,col2):
  new = deepcopy(col1)
  if isinstance(col1, SYM):
      for n in col2.has:
        new.add(n)
  else:
    for n in col2.has:
        new.add(new,n)
    new.lo = min(col1.lo, col2.lo)
    new.hi = max(col1.hi, col2.hi) 
  return new

def RANGE(at,txt,lo,hi=None):
    return {'at':at,'txt':txt,'lo':lo,'hi':lo or hi or lo,'y':SYM()}

def extend(range,n,s):
    range['lo'] = min(n, range['lo'])
    range['hi'] = max(n, range['hi'])
    range['y'].add(s)

def itself(x):
    return x

def value(has,nB = None, nR = None, sGoal = None):
    sGoal,nB,nR = sGoal or True, nB or 1, nR or 1
    b,r = 0,0
    for x,n in has.items():
        if x==sGoal:
            b = b + n
        else:
            r = r + n
    b,r = b/(nB+1/float("inf")), r/(nR+1/float("inf"))
    return b**2/(b+r)


def merge2(col1,col2):
  new = merge(col1,col2)
  if new.div() <= (col1.div()*col1.n + col2.div()*col2.n)/new.n:
    return new

def mergeAny(ranges0):
    def noGaps(t):
        for j in range(1,len(t)):
            t[j]['lo'] = t[j-1]['hi']
        t[0]['lo']  = float("-inf")
        t[len(t)-1]['hi'] =  float("inf")
        return t

    ranges1,j = [],0
    while j <= len(ranges0)-1:
        left = ranges0[j]
        right = None if j == len(ranges0)-1 else ranges0[j+1]
        if right:
            y = merge2(left['y'], right['y'])
            if y:
                j = j+1
                left['hi'], left['y'] = right['hi'], y
        ranges1.append(left)
        j = j+1
    return noGaps(ranges0) if len(ranges0)==len(ranges1) else mergeAny(ranges1)

def firstN(sortedRanges,scoreFun):
    print("")
    def function(r):
        print(r['range']['txt'],r['range']['lo'],r['range']['hi'],rnd(r['val']),r['range']['y'].has)
    _ = list(map(function, sortedRanges))
    print()
    first = sortedRanges[0]['val']
    def useful(range):
        if range['val']>.05 and range['val']> first/10:
            return range
    sortedRanges = [x for x in sortedRanges if useful(x)]
    most,out = -1, -1
    for n in range(1,len(sortedRanges)+1):
        slice = sortedRanges[0:n]
        slice_range = [x['range'] for x in slice]
        tmp,rule = scoreFun(slice_range)
        if tmp and tmp > most:
            out,most = rule,tmp
    return out,most

def impute_missing_values(df):
    for i in df.columns[df.isnull().any(axis=0)]:
        df[i].fillna(df[i].mean(),inplace=True)
    for col in df.columns[df.eq('?').any()]:
        df[col] =df[col].replace('?', np.nan)
        df[col] = df[col].astype(float)
        df[col] = df[col].fillna(df[col].mean())
    return df

def label_encoding(df):
    syms = [col for col in df.columns if col.strip()[0].islower() and df[col].dtypes == 'O']
    le = LabelEncoder()
    for sym in syms:
        col = le.fit_transform(df[sym])
        df[sym] = col.copy()

