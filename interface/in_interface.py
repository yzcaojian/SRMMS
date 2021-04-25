# -*- coding: utf-8 -*-
# @ModuleName: in_interface
# @Function: 
# @Author: Chen Zhongwei
# @Time: 2021/4/25 16:55

# 服务器硬盘和I/O负载信息接口  数据通信解析模块->资源调度分配模块
class IN_DCA_RSA:
    def function(self):
        pass

# 调度分配指令接口  资源调度分配模块->数据通信解析模块
class IN_RSA_DCA:
    def function(self):
        pass

# 资源信息接口  数据通信解析模块->资源状态显示模块
class IN_DCA_RSD:
    def function(self):
        pass

# SMART信息接口  数据通信解析模块->硬盘故障预测模块
class IN_DCA_HDFP:
    def function(self):
        pass

# 硬盘健康度预测接口  硬盘故障预测模块->资源状态显示模块
class IN_HDFP_RSD:
    def function(self):
        pass

# 硬盘故障预测处理接口  硬盘故障预测模块->资源调度分配模块
class IN_HDFP_RSA:
    def function(self):
        pass

# I/O负载预测接口  资源调度分配模块->资源状态显示模块
class IN_LP_RSD:
    def function(self):
        pass

# 分配指令日志信息接口  资源调度分配模块->资源状态显示模块
class IN_RSA_RSD:
    def function(self):
        pass

# 硬盘故障预警接口  硬盘故障预测模块->资源状态显示模块
class IN_HDW:
    def function(self):
        pass

# I/O高负载预警接口  资源调度分配模块->资源状态显示模块
class IN_IOW:
    def function(self):
        pass

