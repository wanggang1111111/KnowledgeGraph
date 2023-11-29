import codecs
import random
import math
import numpy as np
import copy
import time
import csv

entity2id = {}
relation2id = {}


def data_loader(entity_file, relation_file, triple_file):
    entity_set = set()
    relation_set = set()
    triple_list = []

    with open(entity_file, 'r', encoding='utf-8') as entity_f:
        entity_reader = csv.reader(entity_f)
        next(entity_reader)  # 跳过标题行
        for row in entity_reader:
            entity_set.add(row[0])

    with open(relation_file, 'r', encoding='utf-8') as relation_f:
        relation_reader = csv.reader(relation_f)
        next(relation_reader)  # 跳过标题行
        for row in relation_reader:
            relation_set.add(row[0])

    with open(triple_file, 'r', encoding='utf-8') as triple_f:
        triple_reader = csv.reader(triple_f)
        next(triple_reader)  # 跳过标题行
        for row in triple_reader:
            head_id, relation_id, tail_id = row[0], row[1], row[2]
            triple_list.append((head_id, relation_id, tail_id))

    return entity_set, relation_set, triple_list


# -----------------------------------------------------------测试
entity_file = 'id_entity.csv'
relation_file = 'id_relation.csv'
triple_file = 'ids_triples.csv'
entity_set, relation_set, triple_list = data_loader(entity_file, relation_file, triple_file)

# print("Entity Set:")
# for entity in entity_set:
#     print(entity)
#
# print("Relation Set:")
# for relation in relation_set:
#     print(relation)
#
# print("Triple List:")
# for triple in triple_list:
#     print(triple)
#--------------------------------------------------------------------------

def distanceL2(h,r,t):
    #为方便求梯度，去掉sqrt
    return np.sum(np.square(h + r - t))

def distanceL1(h,r,t):
    return np.sum(np.fabs(h+r-t))

class TransE:
    def __init__(self,entity_set, relation_set, triple_list,
                 embedding_dim=100, learning_rate=0.01, margin=1,L1=True):
        self.embedding_dim = embedding_dim
        self.learning_rate = learning_rate
        self.margin = margin
        self.entity = entity_set
        self.relation = relation_set
        self.triple_list = triple_list
        self.L1=L1

        self.loss = 0

    def emb_initialize(self):
        relation_dict = {}
        entity_dict = {}

        for relation in self.relation:#首先，代码使用np.random.uniform函数生成一个范围在-6/math.sqrt(self.embedding_dim)和6/math.sqrt(self.embedding_dim)之间的随机数数组r_emb_temp。这个数组的长度为self.embedding_dim，即嵌入维度
            r_emb_temp = np.random.uniform(-6/math.sqrt(self.embedding_dim) ,
                                           6/math.sqrt(self.embedding_dim) ,
                                           self.embedding_dim)
            #代码使用np.linalg.norm函数对r_emb_temp进行L2范数归一化，得到一个单位向量。归一化后的值被赋给relation_dict字典，以relation作为键。
            relation_dict[relation] = r_emb_temp / np.linalg.norm(r_emb_temp,ord=2)

        for entity in self.entity:
            e_emb_temp = np.random.uniform(-6/math.sqrt(self.embedding_dim) ,
                                        6/math.sqrt(self.embedding_dim) ,
                                        self.embedding_dim)
            entity_dict[entity] = e_emb_temp / np.linalg.norm(e_emb_temp,ord=2)

        self.relation = relation_dict
        self.entity = entity_dict

    def train(self, epochs):
        nbatches = 20
        batch_size = len(self.triple_list) // nbatches
        print("batch size: ", batch_size)
        for epoch in range(epochs):
            start = time.time()
            self.loss = 0

            for k in range(nbatches):
                # Sbatch:list
                Sbatch = random.sample(self.triple_list, batch_size)
                Tbatch = []

                for triple in Sbatch:
                    # 每个triple选3个负样例
                    # for i in range(3):
                    corrupted_triple = self.Corrupt(triple)
                    if (triple, corrupted_triple) not in Tbatch:
                        Tbatch.append((triple, corrupted_triple))
                self.update_embeddings(Tbatch)

            end = time.time()
            print("epoch: ", epoch , "cost time: %s"%(round((end - start),3)))
            print("loss: ", self.loss)

            #保存临时结果
            if epoch % 20 == 0:
                with codecs.open("entity_temp", "w") as f_e:
                    for e in self.entity.keys():
                        f_e.write(e + "\t")
                        f_e.write(str(list(self.entity[e])))
                        f_e.write("\n")
                with codecs.open("relation_temp", "w") as f_r:
                    for r in self.relation.keys():
                        f_r.write(r + "\t")
                        f_r.write(str(list(self.relation[r])))
                        f_r.write("\n")

        print("写入文件...")
        with codecs.open("entity_50dim_batch400", "w") as f1:
            for e in self.entity.keys():
                f1.write(e + "\t")
                f1.write(str(list(self.entity[e])))
                f1.write("\n")

        with codecs.open("relation50dim_batch400", "w") as f2:
            for r in self.relation.keys():
                f2.write(r + "\t")
                f2.write(str(list(self.relation[r])))
                f2.write("\n")
        print("写入完成")


    def Corrupt(self,triple):
        corrupted_triple = list(copy.deepcopy(triple))
        seed = random.random()
        if seed > 0.5:
            # 替换head
            rand_head = triple[0]
            while rand_head == triple[0]:
                rand_head = random.sample(list(self.entity.keys()),1)[0]
            corrupted_triple[0]=rand_head

        else:
            # 替换tail
            rand_tail = triple[1]
            while rand_tail == triple[1]:
                rand_tail = random.sample(list(self.entity.keys()), 1)[0]
                #rand_tail = random.choice(list(self.entity.keys()))
            corrupted_triple[1] = rand_tail
        return corrupted_triple

    def update_embeddings(self, Tbatch):
        copy_entity = copy.deepcopy(self.entity)
        copy_relation = copy.deepcopy(self.relation)

        for triple, corrupted_triple in Tbatch:
            # 取copy里的vector累积更新
            h_correct_update = copy_entity[triple[0]]
            t_correct_update = copy_entity[triple[2]]
            relation_update = copy_relation[triple[1]]

            h_corrupt_update = copy_entity[corrupted_triple[0]]
            t_corrupt_update = copy_entity[corrupted_triple[1]]

            # 取原始的vector计算梯度
            h_correct = self.entity[triple[0]]
            t_correct = self.entity[triple[2]]
            relation = self.relation[triple[1]]

            h_corrupt = self.entity[corrupted_triple[0]]
            t_corrupt = self.entity[corrupted_triple[1]]

            if self.L1:
                dist_correct = distanceL1(h_correct, relation, t_correct) #个函数的返回值是L1范数距离，表示头实体、关系和尾实体之间的距离
                dist_corrupt = distanceL1(h_corrupt, relation, t_corrupt)
            else:
                dist_correct = distanceL2(h_correct, relation, t_correct)
                dist_corrupt = distanceL2(h_corrupt, relation, t_corrupt)

            err = self.hinge_loss(dist_correct, dist_corrupt)

            if err > 0:
                self.loss += err

                grad_pos = 2 * (h_correct + relation - t_correct)
                grad_neg = 2 * (h_corrupt + relation - t_corrupt)

                if self.L1:
                    for i in range(len(grad_pos)):
                        if (grad_pos[i] > 0):
                            grad_pos[i] = 1
                        else:
                            grad_pos[i] = -1

                    for i in range(len(grad_neg)):
                        if (grad_neg[i] > 0):
                            grad_neg[i] = 1
                        else:
                            grad_neg[i] = -1

                # head系数为正，减梯度；tail系数为负，加梯度
                h_correct_update -= self.learning_rate * grad_pos
                t_correct_update -= (-1) * self.learning_rate * grad_pos

                # corrupt项整体为负，因此符号与correct相反
                if triple[0] == corrupted_triple[0]:  # 若替换的是尾实体，则头实体更新两次
                    h_correct_update -= (-1) * self.learning_rate * grad_neg
                    t_corrupt_update -= self.learning_rate * grad_neg

                elif triple[1] == corrupted_triple[1]:  # 若替换的是头实体，则尾实体更新两次
                    h_corrupt_update -= (-1) * self.learning_rate * grad_neg
                    t_correct_update -= self.learning_rate * grad_neg

                #relation更新两次
                relation_update -= self.learning_rate*grad_pos
                relation_update -= (-1)*self.learning_rate*grad_neg


        #batch norm
        for i in copy_entity.keys():
            copy_entity[i] /= np.linalg.norm(copy_entity[i])#归一化为单位向量
        for i in copy_relation.keys():
            copy_relation[i] /= np.linalg.norm(copy_relation[i])

        # 达到批量更新的目的
        self.entity = copy_entity
        self.relation = copy_relation

    def hinge_loss(self,dist_correct,dist_corrupt):
        return max(0,dist_correct-dist_corrupt+self.margin)


if __name__=='__main__':

    entity_set, relation_set, triple_list = data_loader(entity_file, relation_file, triple_file)
    print("load file...")
    print("Complete load. entity : %d , relation : %d , triple : %d" % (len(entity_set),len(relation_set),len(triple_list)))

    transE = TransE(entity_set, relation_set, triple_list,embedding_dim=100, learning_rate=0.01, margin=1,L1=True)
    transE.emb_initialize()
    transE.train(epochs=1000)