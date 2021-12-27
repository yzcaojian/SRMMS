import wmi
import json
import socket
import win32com.client as client
import time
import _thread


def get_disk_data():
    c = wmi.WMI()
    detailed_info = []
    data_list = []

    total_capacity = 0
    total_used = 0

    #  DriveType=3 : "Local Disk",
    for disk in c.Win32_LogicalDisk(DriveType=3):
        disk_name = disk.DeviceID
        capacity = round(float(disk.Size) / (1024 * 1024 * 1024), 2)
        available = round(float(disk.FreeSpace) / (1024 * 1024 * 1024), 2)
        used = round(capacity - available, 2)
        percent = str(round(100 * used / capacity, 2)) + '%'

        total_capacity += capacity
        total_used += used

        data_list.append(disk_name)
        detailed_info.append([disk_name, capacity, used, percent])

    total_percent = str(round(100 * total_used / total_capacity, 2)) + '%'

    com = client.Dispatch("WbemScripting.SWbemRefresher")
    obj = client.GetObject("winmgmts:\\root\cimv2")
    diskitems = com.AddEnum(obj, "Win32_PerfFormattedData_PerfDisk_LogicalDisk").objectSet

    com.Refresh()
    # I/O负载单位统一为kB，保留一位小数
    read_bytes, write_bytes = 0, 0
    for item in diskitems:
        if item.Name in data_list:
            read_bytes += round(float(item.DiskReadBytesPerSec) / 1024, 1)
            write_bytes += round(float(item.DiskWriteBytesPerSec) / 1024, 1)
    total_io = round(read_bytes + write_bytes, 1)

    overall_info = [total_capacity, total_used, total_percent, total_io]

    dic = {"overall_info": overall_info, "detailed_info": detailed_info}

    return dic


def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('1.1.1.1', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


def background_broadcast_ip():
    port = 1234
    dest = ('<broadcast>', port)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    flag = True
    while flag:
        data = "SRMMS" + "_" + get_host_ip() + "_0"
        byte = bytes(data, encoding="utf-8")
        s.sendto(byte, dest)
        time.sleep(5)
    s.close()


# 后台线程发送服务器的IP地址
_thread.start_new_thread(background_broadcast_ip, ())

ip = get_host_ip()
port = 12345
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((ip, port))
loop_flag = True
while loop_flag:
    s.listen(1)
    sock, addr = s.accept()
    print("连接已经建立")

    info = sock.recv(1024).decode().split('/')
    if info[0] == "请求数据1" or info[0] == "请求数据2" or info[0] == "请求数据3":
        dic = get_disk_data()
        string = json.dumps(dic)
        byte = bytes(string, encoding="utf-8")
        sock.send(byte)
    # elif info[0] == "接收指令":
    #     instructions = info[1]
    #     file = open('./instructions.txt', 'a+')
    #     file.writelines(instructions + "\n")
    #     file.close()

    sock.close()
    print("连接已经断开")
s.close()
