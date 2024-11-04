# @Time: 2024/11/3 23:08
# @Author: AsakawaNagi
# @File: main.py
# @Software: PyCharm

import time
from threading import Thread
import random

# 初始化设备节点信息，分别为节点标识符、ip地址，路由表、邻居节点信息、节点状态
class DeviceNode:
    def __init__(self, node_id, ip_address, neighbors=None):
        self.node_id = node_id
        self.ip_address = ip_address
        self.routing_table = {}
        self.neighbors = neighbors if neighbors else []
        self.active = True

    # 向邻居节点广播路由信息，更新路由表
    def broadcast_route_info(self):
        while self.active:
            print("节点 {} (IP: {}) 正向其他节点广播路径信息".format(self.node_id, self.ip_address))
            for neighbor in self.neighbors:
                neighbor.update_routing_table(self.node_id, self.routing_table)
            time.sleep(5)

    # 广播传感器信息
    def broadcast_sensor_data(self, sensor_id, temperature, humidity):
        print("节点 {} (IP: {}) 正在广播传感器 {}的数据: 当前温度={:.2f}°C, 当前湿度={:.2f}%".format(self.node_id, self.ip_address, sensor_id, temperature, humidity))
        for neighbor in self.neighbors:
            neighbor.receive_sensor_data(sensor_id, temperature, humidity)

    # 接受传感器信息
    def receive_sensor_data(self, sensor_id, temperature, humidity):
        print("节点 {} (IP: {}) 从传感器 {}接收到了信息: 当前温度={:.2f}°C, 当前湿度={:.2f}%".format(self.node_id, self.ip_address, sensor_id, temperature, humidity))

    # 更新路由表
    # 假设节点A收到了来自节点B的路由信息。A会逐一查看B的路由表。如果B表中的某个节点X的距离加上A到B的距离比A自己路由表中记录的到X的距离更短，A就会把新的距离记录下来，形成新的路由表
    def update_routing_table(self, source_id, source_table):
        print("节点 {} (IP: {}) 从设备 {} 接收到了路径信息".format(self.node_id, self.ip_address, source_id))
        # 检查source_table中每个节点的距离，如果新的距离更短，那么就更新
        for node, distance in source_table.items():
            # 如果是自己节点的 ID，就跳过更新
            if node == self.node_id:
                continue
            if node not in self.routing_table or self.routing_table[node] > distance + 1:
                self.routing_table[node] = distance + 1
        # 设置与直接相邻节点的距离为 1
        self.routing_table[source_id] = 1

    def stop(self):
        self.active = False

# 这是一个一个温度传感器啊啊
class TemperatureHumiditySensor:
    def __init__(self, sensor_id, device_node):
        self.sensor_id = sensor_id
        self.device_node = device_node
        self.active = True

    # 模拟生成随机温湿度数据并广播
    def read_sensor_data(self):
        while self.active:
            temperature = random.uniform(15.0, 30.0)  # 随机生成温度在15-30°C范围
            humidity = random.uniform(30.0, 70.0)     # 随机生成湿度在30-70%范围
            self.device_node.broadcast_sensor_data(self.sensor_id, temperature, humidity)
            time.sleep(5)  # 每隔5秒广播一次数据

    def stop(self):
        self.active = False


# 模拟设备节点
central_controller = DeviceNode("中央控制器", "192.168.1.1")  # 中央控制器节点
temperature_sensor = DeviceNode("温湿度传感器", "192.168.1.2", [central_controller])  # 温湿度传感器节点
air_conditioner = DeviceNode("空调", "192.168.1.3", [central_controller, temperature_sensor])  # 空调节点
humidifier = DeviceNode("加湿器", "192.168.1.4", [central_controller, temperature_sensor, air_conditioner])  # 加湿器节点

# 设置每个节点的邻居节点
central_controller.neighbors = [temperature_sensor, air_conditioner, humidifier]
temperature_sensor.neighbors = [central_controller]
air_conditioner.neighbors = [central_controller, humidifier]
humidifier.neighbors = [central_controller, air_conditioner]

# 创建温湿度传感器并启动数据读取
sensor_A = TemperatureHumiditySensor("Sensor_A", temperature_sensor)

# 启动线程
threads = []
sensor_thread = Thread(target=sensor_A.read_sensor_data)
sensor_thread.start()
threads.append(sensor_thread)

# 启动每个节点的路由信息广播
for node in [central_controller, temperature_sensor, air_conditioner, humidifier]:
    t_broadcast = Thread(target=node.broadcast_route_info)
    t_broadcast.start()
    threads.append(t_broadcast)

# 让模拟运行一段时间
time.sleep(20)

# 停止所有活动
sensor_A.stop()
for node in [central_controller, temperature_sensor, air_conditioner, humidifier]:
    node.stop()
for thread in threads:
    thread.join()

print("\n最终路由表:")
for node in [central_controller, temperature_sensor, air_conditioner, humidifier]:
    print("节点 {} (IP: {}) 的最终路径表: {}".format(node.node_id, node.ip_address, node.routing_table))


'''
sensor 传感器
device 设备
node 节点
你妈的我要洋人似
'''
