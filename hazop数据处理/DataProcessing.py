import csv

#------------------------------------------------------处理实体，以id-entity存储
def generate_unique_ids(input_file, output_file):
    # 读取CSV文件内容并去重
    data = set()
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            for value in row:
                data.add(value)

    # 为每个内容生成唯一ID
    id_data = {}
    for i, value in enumerate(sorted(data)):
        id_data[value] = i + 1

    # 将ID和内容写入CSV文件
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Content'])
        for value, id in id_data.items():
            writer.writerow([id, value])


# 测试
input_file = 'entity.csv'
output_file = 'id_entity.csv'
generate_unique_ids(input_file, output_file)


#------------------------------------------------------关系处理，以id-relation存储

def process_csv(input_file, output_file):
    data = set()
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # 读取标题行
        col_num = 2  # 第三列索引为2（从0开始）
        for row in reader:
            if len(row) > col_num:
                data.add(row[col_num])

    # 为每个内容生成唯一ID
    id_data = {}
    for i, value in enumerate(data):
        id_data[value] = i + 1

    # 将ID和内容写入CSV文件
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', header[col_num]])  # 写入标题行
        for value, id in id_data.items():
            writer.writerow([id, value])


# 测试
input_file = 'triples.csv'
output_file = 'id_relation.csv'
process_csv(input_file, output_file)

#-----------------------------------------三元组{实体id，关系id，实体id}
def convert_triples(input_file, entity_file, relation_file, output_file):
    # 读取实体对应的ID
    entity_ids = {}
    with open(entity_file, 'r', encoding='utf-8') as entity_f:
        entity_reader = csv.reader(entity_f)
        next(entity_reader)  # 跳过标题行
        for row in entity_reader:
            entity_id, entity = row[0], row[1]
            entity_ids[entity] = entity_id

    # 读取关系对应的ID
    relation_ids = {}
    with open(relation_file, 'r', encoding='utf-8') as relation_f:
        relation_reader = csv.reader(relation_f)
        next(relation_reader)  # 跳过标题行
        for row in relation_reader:
            relation_id, relation = row[0], row[1]
            relation_ids[relation] = relation_id

    # 转换三元组，并写入新的CSV文件
    with open(input_file, 'r', encoding='utf-8') as input_f, open(output_file, 'w', newline='', encoding='utf-8') as output_f:
        input_reader = csv.reader(input_f)
        output_writer = csv.writer(output_f)
        output_writer.writerow(['Head ID', 'Relation ID', 'Tail ID'])  # 写入标题行
        next(input_reader)  # 跳过标题行
        for row in input_reader:
            head_entity, relation, tail_entity = row[0], row[2], row[3]
            head_id = entity_ids.get(head_entity)  # 获取头实体对应的ID
            relation_id = relation_ids.get(relation)  # 获取关系对应的ID
            tail_id = entity_ids.get(tail_entity)  # 获取尾实体对应的ID
            if head_id and relation_id and tail_id:  # 确保找到所有实体和关系对应的ID
                output_writer.writerow([head_id, relation_id, tail_id])  # 写入新的三元组


# 测试
input_file = 'triples.csv'
entity_file = 'id_entity.csv'
relation_file = 'id_relation.csv'
output_file = 'ids_triples.csv'
convert_triples(input_file, entity_file, relation_file, output_file)