import csv
import pandas as pd
#----------------------------------------区分头实体和尾实体
# 输入csv文件名
filename = "triples.csv"

# 读取csv文件内容，按第二列内容划分为字典
data = {}
with open("triples.csv", 'r', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        if row[1] in data:
            data[row[1]].add(row[0])  # 使用集合（set）进行去重
        else:
            data[row[1]] = {row[0]}  # 创建一个集合（set）来存储第一列的值

# 写入到新的csv文件
output_filename = "Middle.csv"

with open("Middle.csv", 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    for key, value in data.items():
        writer.writerow([key] + list(value))  # 集合（set）转化为列表（list）




## 输入csv文件名
# filename = input("请输入csv文件名：")
#-------------------------------------------------纵横交换
# 读取csv文件
rows = []
with open("Middle.csv", 'r', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        rows.append(row)

# 确定最长的行
max_length = max(len(row) for row in rows)

# 填充短行使其与最长行长度一致
for row in rows:
    row.extend([''] * (max_length - len(row)))

# 交换行和列
transposed_rows = [[rows[j][i] for j in range(len(rows))] for i in range(max_length)]

# 将交换后的结果写入新的csv文件
# output_filename = input("请输入输出csv文件名：")

with open("Head.csv", 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(transposed_rows)

#-------------------------------------合并文件
def merge_csv(file1, file2, output_file):
    # 读取第一个CSV文件
    with open(file1, 'r', encoding='utf-8') as f1:
        reader1 = csv.reader(f1)
        headers1 = next(reader1)
        data1 = [row for row in reader1]

    # 读取第二个CSV文件
    with open(file2, 'r', encoding='utf-8') as f2:
        reader2 = csv.reader(f2)
        headers2 = next(reader2)
        data2 = [row for row in reader2]

    # 获取合并后的列名
    merged_headers = headers1 + [header for header in headers2 if header not in headers1]

    # 合并内容
    merged_data = []
    for i in range(max(len(data1), len(data2))):
        row = []
        for header in merged_headers:
            if header in headers1:
                if i < len(data1):
                    row.append(data1[i][headers1.index(header)])
                else:
                    row.append('')
            else:
                if i < len(data2):
                    row.append(data2[i][headers2.index(header)])
                else:
                    row.append('')
        merged_data.append(row)

    # 写入新的CSV文件
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(merged_headers)
        writer.writerows(merged_data)


# 测试
file1 = 'Head.csv'
file2 = 'Tail.csv'
output_file = 'entity.csv'
merge_csv(file1, file2, output_file)