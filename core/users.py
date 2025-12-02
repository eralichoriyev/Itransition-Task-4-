import itertools
import pandas as pd
from collections import defaultdict

from .price import normalize_string, normalize_phone

class UnionFind:
    def __init__(self, items):
        self.parent = {i:i for i in items}
    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x
    def union(self, x, y):
        rx = self.find(x); ry = self.find(y)
        if rx != ry:
            self.parent[ry] = rx
    def groups(self):
        comp = {}
        for x in self.parent:
            r = self.find(x)
            comp.setdefault(r, set()).add(x)
        return list(comp.values())

def reconcile_users(users_df):
    df = users_df.copy()
    if 'id' not in df.columns:
        df = df.reset_index().rename(columns={'index':'id'})
    df['uid'] = df['id'].astype(str)
    df['name_n'] = df['name'].apply(normalize_string) if 'name' in df.columns else ''
    df['address_n'] = df['address'].apply(normalize_string) if 'address' in df.columns else ''
    df['email_n'] = df['email'].apply(normalize_string) if 'email' in df.columns else ''
    df['phone_n'] = df['phone'].apply(normalize_phone) if 'phone' in df.columns else ''
    uids = df['uid'].tolist()
    uf = UnionFind(uids)
    records = df.set_index('uid').to_dict('index')
    for a, b in itertools.combinations(uids, 2):
        ra = records[a]; rb = records[b]
        matches = 0
        matches += 1 if (ra.get('name_n','') and rb.get('name_n','') and ra.get('name_n') == rb.get('name_n')) else 0
        matches += 1 if (ra.get('address_n','') and rb.get('address_n','') and ra.get('address_n') == rb.get('address_n')) else 0
        matches += 1 if (ra.get('email_n','') and rb.get('email_n','') and ra.get('email_n') == rb.get('email_n')) else 0
        matches += 1 if (ra.get('phone_n','') and rb.get('phone_n','') and ra.get('phone_n') == rb.get('phone_n')) else 0
        if matches >= 3:
            uf.union(a, b)
    groups = uf.groups()
    uid_to_real = {}
    for idx, comp in enumerate(groups, 1):
        for uid in comp:
            uid_to_real[uid] = f"real_user_{idx}"
    df['real_user'] = df['uid'].map(uid_to_real)
    return df[['id','name','address','phone','email','uid','real_user']]
