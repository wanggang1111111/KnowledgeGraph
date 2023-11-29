import csv

import numpy as np
import pandas as pd
import codecs
import operator
import json
entity_dict = {}
relation_dict = {}
test_triple = []

with codecs.open("entity_50dim_batch400") as e_f:
    lines = e_f.readlines()
    for line in lines:
        entity,embedding = line.strip().split('\t')
        embedding = json.loads(embedding)
        entity_dict[entity] = embedding

with codecs.open("relation50dim_batch400") as r_f:
    lines = r_f.readlines()
    for line in lines:
        relation,embedding = line.strip().split('\t')
        embedding = json.loads(embedding)
        relation_dict[relation] = embedding

def distance(h, r, t):

    h = np.array(h)
    r = np.array(r)
    t = np.array(t)

    s = h + r - t
    return np.linalg.norm(s)

#多跳路径预测预测（二跳）-------------------
rank_tail_dict = {}
i=0
for head in entity_dict.keys():
    # i+=1
    # print(i)
    for relation1 in relation_dict.keys():
        for relation2 in relation_dict.keys():
             for tail in entity_dict.keys():
                  h_h = entity_dict[head]
                  r = np.array(relation_dict[relation1]) + np.array(relation_dict[relation2])
                  t_t = entity_dict[tail]
                  corrupted_tail = [head, relation1,relation2, tail]
                  rank_tail_dict[tuple(corrupted_tail)] = distance(h_h, r, t_t)
rank_tail_sorted = sorted(rank_tail_dict.items(), key=operator.itemgetter(1))

df_entity = pd.read_csv('id_entity.csv')
df_relation = pd.read_csv('id_relation.csv')
for i in range(50):
    result0 = df_entity.loc[df_entity['ID'] == int(rank_tail_sorted[i][0][0]), 'Content'].values[0]
    result1 = df_relation.loc[df_relation['ID'] == int(rank_tail_sorted[i][0][1]), 'relation'].values[0]
    result2 = df_relation.loc[df_relation['ID'] == int(rank_tail_sorted[i][0][2]), 'relation'].values[0]
    result3 = df_entity.loc[df_entity['ID'] == int(rank_tail_sorted[i][0][3]), 'Content'].values[0]
    print(str(result0)+"  "+str(result1)+"  "+str(result2)+"  "+str(result3))

#炉管结焦(中间事件)—（后果）—>严重时炉管烧穿—(风险等级)—>Ⅱ
#加热炉效率下降(后果)—保护措施—>TI1030C