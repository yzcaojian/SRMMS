"""
-*- coding: utf-8 -*- 
@Project: SRMMS
@Description: windows...
@Time : 2021/12/22 20:48
@Author : cao jian
"""

import os, sys
import time
import wmi


def get_disk_info():
    """
    获取物理磁盘信息。
    """
    tmplist = []
    c = wmi.WMI()
    for physical_disk in c.Win32_DiskDrive():
        print(physical_disk.Model)
        tmpdict = {}
        tmpdict["Caption"] = physical_disk.Caption
        tmpdict["Size"] = int(physical_disk.Size)/1024/1024/1024
        tmplist.append(tmpdict)
    return tmplist


def get_fs_info() :
    """
    获取文件系统信息。
    包含分区的大小、已用量、可用量、使用率、挂载点信息。
    """
    tmplist = []
    c = wmi.WMI()
    for physical_disk in c.Win32_DiskDrive():
        print(physical_disk)
        for partition in physical_disk.associators("Win32_DiskDriveToDiskPartition"):
            for logical_disk in partition.associators("Win32_LogicalDiskToPartition"):
                tmpdict = {}
                tmpdict["Caption"] = logical_disk.Caption
                tmpdict["DiskTotal"] = int(logical_disk.Size)/1024/1024/1024
                tmpdict["UseSpace"] = (int(logical_disk.Size)-int(logical_disk.FreeSpace))/1024/1024/1024
                tmpdict["FreeSpace"] = int(logical_disk.FreeSpace)/1024/1024/1024
                tmpdict["Percent"] = int(100.0*(int(logical_disk.Size)-int(logical_disk.FreeSpace))/int(logical_disk.Size))
                tmplist.append(tmpdict)
    return tmplist


if __name__ == "__main__":
     disk = get_disk_info()
     print(disk)
     print('--------------------------------------' )
     fs = get_fs_info()
     print(fs)
