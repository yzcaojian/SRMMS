import csv
import pandas as pd
from datetime import datetime

"""
-*- coding: utf-8 -*- 
@Project: disk_failure_prediction
@Description: 以HGST HMS5C4040ALE640型号硬盘读故障记录和故障前正常记录
@Time : 2021/2/2 10:10
@Author : cao jian
"""
fail_list = []  # 保存已经故障的硬盘的序列号
first_time = True  # 第一次读取为第一行列名，用于生成表头title
# title = []  # 生成新表属性列名，步骤一
# template = []  # 模板：记录failure字段和有效SMART属性列号字段
title = ['serial_number', 'failure', 'smart_1_raw', 'smart_2_raw', 'smart_3_raw', 'smart_4_raw', 'smart_5_raw',
         'smart_7_raw', 'smart_8_raw', 'smart_9_raw', 'smart_10_raw', 'smart_12_raw', 'smart_192_raw', 'smart_193_raw',
         'smart_194_raw','smart_196_raw', 'smart_197_raw', 'smart_198_raw', 'smart_199_raw']

# 运行生成临时数据耗用内存过大
# 生成15年-20年的日期序列
date = [datetime.strftime(x, '%Y-%m-%d') for x in list(pd.date_range('20150101', '20201231'))]
date.reverse()  # 从故障日期向前遍历历史SMART数据
for day in date:
    filename = "D:\\backblaze hdd dataset\\" + day[0:4] + "\\" + day + ".csv"
    print(day)
    fr = open(filename)
    reader = csv.reader(fr)
    # if first_time:  # 生成新表属性列名，步骤二
    #     title = next(reader)[1:]
    for record in reader:
        # 选择第一行列名部分的字段作为结果表列名
        # 生成新表属性列名，步骤三
        # if first_time and record[2] == "HGST HMS5C4040ALE640":
        #     # 利用已知信息，第一条读入记录肯定不是故障的，所以遍历此记录并得到模板, 每个序列号只会执行一次
        #     # 已弃用用template模板加速SMART有效数据读，因为每个季度之间的smart数据字段数量是不一样的，趋势为逐年增加
        #     for i in range(4, len(record)):  # 遍历failure字段和所有SMART属性值，保留不为空的字段
        #         if record[i] != "":
        #             template.append(i)
        #             i = i + 1
        #     first_time = False

        if record[2] == "HGST HMS5C4040ALE640":  # 选择只采集昱科HGST HMS5C4040ALE640型号的硬盘数据
            temp = []  # 临时保留有效的SMART数据
            # 读故障记录
            if record[4] == "1":
                fail_list.append({"sequence": record[1], "record": []})  # 先选择保留整条记录，后面再指定列
                # for i in template:  # 遍历所有SMART属性值，保留不为空的字段
                i = 4
                j = len(record)
                while i < j:  # 遍历failure字段和所有SMART属性值raw_data，保留不为空的字段
                    if record[i] != "":
                        temp.append(record[i])
                    i = i + 2  # 跳过normalized data，取raw data
                # for i in range(4, len(record)):  # for in语句不能改变迭代操作符i
                #     if record[i] != "":
                #         temp.append(record[i])
                #         i = i + 1  # 跳过normalized data，取raw data
                # temp.append(1)  # 标签为1，表示failure，弃用，failure在record里
                # 添加刚新增的某硬盘历史SMART数据的"record"字段，"record"数据格式为列表的列表
                fail_list[len(fail_list) - 1]["record"].append(temp)

            # 读非故障记录
            else:
                for i in range(len(fail_list)):
                    if record[1] == fail_list[i]["sequence"]:
                        j = 4
                        k = len(record)
                        while j < k:  # 遍历failure字段和所有SMART属性值raw_data，保留不为空的字段
                            if record[j] != "":
                                temp.append(record[j])
                            j = j + 2  # 跳过normalized data，取raw data
                        # temp.append(0)  # 标签为0，表示not failure，弃用，failure在record里
                        # 添加刚新增的某硬盘历史SMART数据的"record"字段，"record"数据格式为列表的列表
                        fail_list[i]["record"].append(temp)
                        break
    fr.close()

# 修改表列名，生成新表属性列名，步骤四
# for (i, j) in zip(range(1, len(title)), range(len(template))):
#     title[i] = title[template[j] - 1]
# print(title[:len(template) + 1])

# 参数newline是用来控制文本模式之下一行的结束字符
writer = csv.writer(open('HGST HMS5C4040ALE640_v1.csv', 'a+', newline=''))
# writer.writerow(title[:len(template) + 1])  # 写入title，步骤五
writer.writerow(title)

for item in fail_list:
    # 写入csv文件
    for k in range(len(item["record"])):  # record记录数据类型：元素为列表的列表，遍历第一层列表
        eff_line = [item["sequence"]]  # 有效行的写入
        for l in range(len(item["record"][k])):  # 遍历第二层列表
            eff_line.append(item["record"][k][l])
        writer.writerow(eff_line)
