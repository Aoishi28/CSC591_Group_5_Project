from row import ROW
from cols import COLS
from utils import *
from functools import cmp_to_key
import numpy as np
from sklearn.manifold import TSNE
import random


class DATA:
    def __init__(self, src = None, rows = None):
        self.rows = []
        self.cols = None
        if src or rows:
            if isinstance(src, str):
                csv(src, self.add)
            else:
                self.cols = COLS(src.cols.names)
                for row in rows:
                    self.add(row)

    def add(self, t):
        if self.cols:
            t = t if isinstance(t, ROW) else ROW(t)
            self.rows.append(t)
            self.cols.add(t)
        else:
            self.cols=COLS(t)
    
    def stats(self, cols = None, nPlaces = 2, what = 'mid'):
        stats_dict = dict(sorted({col.txt: rnd(getattr(col, what)(), nPlaces) for col in cols or self.cols.y}.items()))
        stats_dict["N"] = len(self.rows)
        return stats_dict
    
    def dist(self, row1, row2, cols = None):
        n,d = 0,0
        for col in cols or self.cols.x:
            n = n + 1
            d = d + col.dist(row1.cells[col.at], row2.cells[col.at])**the['p']
        return (d/n)**(1/the['p'])
               
    def clone(data, ts={}):
        data1 = DATA()
        data1.add(data.cols.names)
        for _, t in enumerate(ts or {}):
            data1.add(t)
        return data1

    def half(self, rows = None, cols = None, above = None):
        def gap(row1,row2): 
            return self.dist(row1,row2,cols)
        def project(row):
            return {'row' : row, 'dist' : cosine(gap(row,A), gap(row,B), c)}
        rows = rows or self.rows
        some = many(rows,the['Halves'])
        A    = above if above and the['Reuse'] else any(some)
        tmp = sorted([{'row': r, 'dist': gap(r, A)} for r in some], key=lambda x: x['dist'])
        far = tmp[int((len(tmp) - 1) * the['Far'])]
        B    = far['row']
        c    = far['dist']
        left, right = [], []
        for n,tmp in enumerate(sorted(map(project, rows), key=lambda x: x['dist'])):
            if (n + 1) <= (len(rows) / 2):
                left.append(tmp["row"])
            else:
                right.append(tmp["row"])
        evals = 1 if the['Reuse'] and above else 2
        return left, right, A, B, c, evals
    
    def half2(self, rows=None, cols=None, above=None):
        if not rows:
            rows = self.rows
        row_set = np.array([r.cells for r in rows])
        tsne = TSNE(n_components=2, perplexity=10)
        components = tsne.fit_transform(row_set)
        result = []
        for i in sorted(enumerate(rows), key=lambda x:components[x[0]][0]**2 + components[x[0]][1]**2):
            result.append(i[1])
        n = len(result)
        left = result[:n//2]
        right = result[n//2:]
        return left, right, random.choices(left, k=10), random.choices(right, k=10), 1
    

    def better(self, rows1, rows2, s1=0, s2=0, ys=None, x=0, y=0):
        if isinstance(rows1, ROW):
            rows1 = [rows1]
            rows2 = [rows2]
        if not ys:
            ys = self.cols.y
        for col in ys:
            for row1, row2 in zip(rows1, rows2):
                x = col.norm(row1.cells[col.at])
                y = col.norm(row2.cells[col.at])
                s1 = s1 - math.exp(col.w * (x - y) / len(ys))
                s2 = s2 - math.exp(col.w * (y - x) / len(ys))
        return s1 / len(ys) < s2 / len(ys)
    
    def tree(self, rows = None , min = None, cols = None, above = None):
        rows = rows or self.rows
        min  = min or len(rows)**the['min']
        cols = cols or self.cols.x
        node = { 'data' : self.clone(rows) }
        if len(rows) >= 2*min:
            left, right, node['A'], node['B'], _, _ = self.half(rows,cols,above)
            node['left']  = self.tree(left,  min, cols, node['A'])
            node['right'] = self.tree(right, min, cols, node['B'])
        return node
    
    def tree2(self, rows = None , min = None, cols = None, above = None):
        rows = rows or self.rows
        min  = min or len(rows)**the['min']
        cols = cols or self.cols.x
        node = { 'data' : self.clone(rows) }
        if len(rows) >= 2*min:
            left, right, node['A'], node['B'], _, _ = self.half2(rows,cols,above)
            node['left']  = self.tree2(left,  min, cols, node['A'])
            node['right'] = self.tree2(right, min, cols, node['B'])
        return node
    
    def sway(self):
        data = self
        def worker(rows, worse, evals0 = None, above = None):
            if len(rows) <= len(data.rows)**the['min']: 
                return rows, many(worse, the['rest']*len(rows)), evals0
            else:
                l,r,A,B,c,evals = self.half(rows, None, above)
                if self.better(B,A):
                    l,r,A,B = r,l,B,A
                for row in r:
                    worse.append(row)
                return worker(l,worse,evals+evals0,A)
        best,rest,evals = worker(data.rows,[],0)
        return DATA.clone(self, best), DATA.clone(self, rest), evals
    
    def sway2(self):
        data = self
        def worker(rows, worse, evals0 = None, above = None):
            if len(rows) <= len(data.rows)**the['min']: 
                return rows, many(worse, the['rest']*len(rows)), evals0
            else:
                l,r,A,B,evals = self.half2(rows, None, above)
                if self.better(B,A):
                    l,r,A,B = r,l,B,A
                for row in r:
                    worse.append(row)
                return worker(l,worse,evals+evals0,A)
        best,rest,evals = worker(data.rows,[],0)
        return DATA.clone(self, best), DATA.clone(self, rest), evals
    
    def betters(self,n):
        key = cmp_to_key(lambda row1, row2: -1 if self.better(row1, row2) else 1)
        tmp = sorted(self.rows, key = key)
        if n is None:
            return tmp
        else:
            return tmp[1:n], tmp[n+1:]