import csv
import pandas as pd
from datetime import datetime

"""
-*- coding: utf-8 -*- 
@Project: SRMMS
@Description: 统计数据集中各硬盘型号对应的故障样本数量
@Time : 2021/12/20 15:19
@Author : cao jian
"""

fail_model = {}  # 保存有故障记录的硬盘model的个数


def read_csv(file):
    reader = csv.reader(open(file))
    next(reader)  # 跳过表头
    for record in reader:
        # if len(record) <= 4:
        #     print(record)
        if record[4] == '1':
            if record[2] in fail_model:
                fail_model[record[2]] += 1  # 该硬盘型号记录数量+1
            else:
                fail_model[record[2]] = 1  # 添加新的硬盘型号


# 生成16-20年:0101-1231的日期序列
# 2016年前的数据可能已经过时或者很多型号已经老旧，先不予考虑。如果数据集不够充分，再把时间范围设置得更大20140101-至最新的数据日期
date = [datetime.strftime(x, '%Y-%m-%d') for x in list(pd.date_range('20160101', '20201231'))]
# date.reverse()  # 从故障日期向前遍历历史SMART数据
for day in date:
    filename = "D:\\backblaze hdd dataset\\" + day[0:4] + "\\" + day + ".csv"
    read_csv(filename)

for i in fail_model:
    print(i, fail_model[i])

"""
ST4000DM000 3256
ST8000DM002 449
ST8000NM0055 616
ST10000NM0086 35
ST12000NM0007 1809
ST12000NM0008 158
WDC WD30EFRX 47 -> 163
WDC WD40EFRX 2
WDC WD60EFRX 44
Hitachi HDS722020ALA330 48 -> 202
Hitachi HDS5C3030ALA630 50
Hitachi HDS5C4040ALE630 21
HGST HMS5C4040ALE640 102  -> 146
HGST HMS5C4040BLE640 268
TOSHIBA MQ01ABF050 237

WDC WD20EFRX 6
WDC WD800AAJB 2
ST320LT007 63
WDC WD10EADS 7
ST9250315AS 4
WDC WD1600BPVT 1
ST500LM012 HN 143
Hitachi HDS723030ALA640 26
ST250LT007 4
WDC WD5000LPVX 47
WDC WD3200BEKX 2
ST4000DX000 71
WDC WD10EACS 2
ST3160318AS 7
TOSHIBA DT01ACA300 2
WDC WD800JB 4
WDC WD800LB 1
WDC WD800BB 5
WDC WD1600AAJB 4
WDC WD3200AAJB 1
WDC WD800JD 1
ST3160316AS 2
ST6000DX000 58
TOSHIBA MD04ABA500V 1
WDC WD1600AAJS 8
WDC WD3200BEKT 1
WDC WD800AAJS 14
WDC WD5002ABYS 2
ST250LM004 HN 5
ST9320325AS 1
ST31500541AS 3
WDC WD5000LPCX 4
TOSHIBA MD04ABA400V 2
WDC WD5000BPKT 2
HGST HDS5C4040ALE630 4
ST3500320AS 1
HGST HUS726040ALE610 3
ST4000DM001 34
TOSHIBA MQ01ABF050M 61
ST4000DM005 6
HGST HUH728080ALE600 18
Samsung SSD 850 EVO 1TB 10
ST4000DX002 4
ST8000DM004 6
TOSHIBA MG07ACA14TA 121
ST8000DM005 3
ST500LM030 46
HGST HUH721212ALN604 82
HGST HUH721212ALE600 12
TOSHIBA HDWF180 1
Seagate BarraCuda SSD ZA500CM10002 1
ST12000NM0117 5
Seagate BarraCuda SSD ZA250CM10002 5
ST12000NM001G 30
ST16000NM001G 1
HGST HUH721212ALE604 9
Seagate SSD 1
ST14000NM001G 13
WDC WUH721414ALE6L4 1
ST18000NM000J 2
"""