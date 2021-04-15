import datetime
import os
import psutil as ps                       # psutil库 需预先安装
import time
import socket
import uuid
  
  
class MachineStatus(object):
  
    #   初始化
    def __init__(self):
        self.MAC = None
        self.IP = None
        self.device = {}
        self.cpu = {}
        self.mem = {}
        self.process = {}
        self.network = {}
        self.status = []                    #  [cpu使用率， 内存使用率， 进程数目， established连接数]
        self.get_init_info()
        self.get_status_info()

    # 获取服务器信息
    def get_device_info(self):
        pass
  
    #  宿主机存库状态
    def run(self):
        self.get_status_info()
        self.save_status_to_db()
  
    def save_status_to_db(self):
        print(self.status)
  
    #  数据收集
    def get_init_info(self):
        self.device = { 'running_time' : 0,
                        'arch' : '',        
                        }
        self.cpu = {'cores' : 0,            #  cpu逻辑核数
                    'percent' : 0,          #  cpu使用率
                    'system_time' : 0,      #  内核态系统时间
                    'user_time' : 0,        #  用户态时间
                    'idle_time' : 0,        #  空闲时间
                    'nice_time' : 0,        #  nice时间 (花费在调整进程优先级上的时间)
                    'softirq' : 0,          #  软件中断时间
                    'irq' : 0,              #  中断时间
                    'iowait' : 0}           #  IO等待时间
        self.mem = {'percent' : 0,
                    'total' : 0,
                    'vailable' : 0,
                    'used' : 0,
                    'free' : 0,
                    'active' : 0}
        self.process = {'count' : 0,        #  进程数目
                        'pids' : 0}         #  进程识别号
        self.network = {'count' : 0,        #  连接总数
                        'established' : 0}  #  established连接数
        self.status = [0, 0, 0, 0]          #  cpu使用率，内存使用率， 进程数， established连接数
        # self.get_mac_address()
        # self.get_ip_address()
  
    #  获取状态列表
    def get_status_info(self):
        self.get_cpu_info()
        self.get_mem_info()
        self.get_process_info()
        self.get_network_info()
        self.status[0] = self.cpu['percent']
        self.status[1] = self.mem['percent']
        self.status[2] = self.process['count']
        self.status[3] = self.network['established']
  
    #  获取mac
    def get_mac_address(self):
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        self.MAC = ":".join([mac[e : e+2] for e in range(0, 11, 2)])
  
    #  获取ip
    def get_ip_address(self):
        tempSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        tempSock.connect(('8.8.8.8', 80))
        addr = tempSock.getsockname()[0]
        tempSock.close()
        self.IP = addr
  
    #  获得cpu信息
    def get_cpu_info(self):
        self.cpu['cores'] = ps.cpu_count()
        self.cpu['percent'] = ps.cpu_percent(interval=2)
        cpu_times = ps.cpu_times()
        self.cpu['system_time'] = cpu_times.system
        self.cpu['user_time'] = cpu_times.user
        self.cpu['idle_time'] = cpu_times.idle
        self.cpu['nice_time'] = cpu_times.nice
        self.cpu['softirq'] = cpu_times.softirq
        self.cpu['irq'] = cpu_times.irq
        self.cpu['iowait'] = cpu_times.iowait
  
    #  获得memory信息
    def get_mem_info(self):
        mem_info = ps.virtual_memory()
        self.mem['percent'] = mem_info.percent
        self.mem['total'] = mem_info.total
        self.mem['vailable'] = mem_info.available
        self.mem['used'] = mem_info.used
        self.mem['free'] = mem_info.free
        self.mem['active'] = mem_info.active
  
    #  获取进程信息
    def get_process_info(self):
       pids = ps.pids()
       self.process['pids'] = pids
       self.process['count'] = len(pids)
  
    # 获取网络数据
    def get_network_info(self):
        conns = ps.net_connections()
        self.network['count'] = len(conns)
        count = 0
        for conn in conns:
           if conn.status == 'ESTABLISHED':
               count = count + 1
        self.network['established'] = count
  
if __name__ == '__main__':
    MS = MachineStatus()
    print(MS.IP, '\n', MS.MAC, '\n', MS.cpu, '\n', MS.mem, '\n', MS.status, MS.process)