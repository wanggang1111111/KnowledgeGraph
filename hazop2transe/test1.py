import csv

import numpy as np
import codecs
import operator
import json
entity_dict = {}
relation_dict = {}
test_triple = []
import pandas as pd

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



#51加剧空气预热器低温腐蚀  3后果     129造成炉管氧腐蚀  7保护措施   11 PI1012C    23 I1030C
rank_tail_dict = {}
rank_relation_dict = {}


def distance(h, r, t):

    h = np.array(h)
    r = np.array(r)
    t = np.array(t)

    s = h + r - t
    return np.linalg.norm(s)
#实体预测-------------------
for entity in entity_dict.keys():
    h_h = entity_dict["51"]
    r = np.array(relation_dict["3"]) + np.array(relation_dict["7"])
    t_t = entity_dict[entity]
    corrupted_tail = [51, 3,7, entity]
    rank_tail_dict[tuple(corrupted_tail)] = distance(h_h, r, t_t)
    rank_tail_sorted = sorted(rank_tail_dict.items(), key=operator.itemgetter(1))

df_entity = pd.read_csv('id_entity.csv')
df_relation = pd.read_csv('id_relation.csv')
print("预测尾实体：")
for i in range(20):          #11 PI1012C    23 I1030C
    result1 = df_entity.loc[df_entity['ID'] == int(rank_tail_sorted[i][0][3]), 'Content'].values[0]
    print(str(i+1)+"  "+str(result1))
print("---------------------------")
#关系预测---------------------------------------------
#51加剧空气预热器低温腐蚀  3后果     129造成炉管氧腐蚀  7保护措施   11 PI1012C    23 I1030C
for relation in relation_dict.keys():
    h_h = entity_dict["51"]
    r = relation_dict[relation]
    t_t = entity_dict["23"]
    corrupted_relation = [51, relation,23]
    rank_relation_dict[tuple(corrupted_relation)] = distance(h_h, r, t_t)
    rank_relation_sorted = sorted(rank_relation_dict.items(), key=operator.itemgetter(1))
print("预测关系：")
for i in range(len(rank_relation_sorted)):          # 23 I1030C
    result2 = df_relation.loc[df_relation['ID'] == int(rank_relation_sorted[i][0][1]), 'relation'].values[0]
    print(str(i+1)+"  "+str(result2))