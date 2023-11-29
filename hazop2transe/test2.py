import numpy as np
import codecs
import operator
import json
import pandas as pd
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



#51加剧空气预热器低温腐蚀  3后果     129造成炉管氧腐蚀  7保护措施   11 PI1012C    23 I1030C
rank_tail_dict1 = {}


def distance(h, r, t):

    h = np.array(h)
    r = np.array(r)
    t = np.array(t)

    s = h + r - t
    return np.linalg.norm(s)

for entity in entity_dict.keys():
    h_h = entity_dict["51"]
    r = np.array(relation_dict["3"])
    t_t = entity_dict[entity]
    corrupted_tail = [51, 3, entity]
    rank_tail_dict1[tuple(corrupted_tail)] = distance(h_h, r, t_t)
    rank_tail_sorted1 = sorted(rank_tail_dict1.items(), key=operator.itemgetter(1))



df = pd.read_csv('id_entity.csv')


#训练集存在的三元组：51加剧空气预热器低温腐蚀->3后果->造成炉管氧腐蚀
for i in range(len(rank_tail_sorted1)):
    id=int(rank_tail_sorted1[i][0][2])
    result = df.loc[df['ID'] == id, 'Content'].values[0]
    print(str(i+1)+"：     51加剧空气预热器低温腐蚀->3后果->" +str(result))
