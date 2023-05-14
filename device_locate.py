import sys
import data_collection_server.db_interface as db
import time
import numpy as np
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
Standard_Signal_List = [
[-10.43, -38.00, -53.78],  
[-45.00, -22.73, -48.30],
[-41.91, -17.83, -52.85], 
[-27.70, -49.64, -42.82],
[-39.50, -44.00, -37.12],
[-37.47, -47.85, -50.81],
[-54.50, -56.61, -11.50],
[-39.33, -48.59, -34.91],
[-55.54, -55.47, -54.18]
]
Standard_Position_List = [
[0 ,   0   ],
[1.18, 0   ],
[2.38, 0   ],
[0 ,   1.09],
[1.18, 1.09],
[2.38, 1.09],
[0 ,   2.18],
[1.18, 2.18],
[2.38, 2.18]
]

Standard_Data_List = []
class Standard_Data:
    def __init__(self, signal, position):
        self.signal = signal
        self.position = position


def averge_datetime(Date_List):
    base = datetime(2023,4,1,0,0,0)
    result = timedelta(0)
    for date in Date_List:
        result = result + (date-base)
    result = result / len(Date_List)
    return result + base

def Show_Raw_Data(Data_Queue):
    for i in range(len(Data_Queue)):
        print("Router{}:".format(i))
        for data in Data_Queue[i]:
            print(data)
        print()

def Update_Data_Queue(Data_Queue, last_end, target_mac, delta_time):
    # get data from server, sort them by time
    if(delta_time == None):
        Data = db.find_target_mac_from_database(target_mac, last_end)
    else:
        Data = db.find_target_mac_from_database(target_mac, last_end, last_end + delta_time)
    sorted(Data,key= lambda x: x['record_time'],reverse=True)
    if(len(Data) > 0):
        last_end = Data[-1]['record_time']

    # the data collected since last time
    Data_List = []
    print("This second get these new data")
    
    for router_mac in router_mac_set:
        Data_List.append([data for data in Data if data["router_mac"] == router_mac])

    # Show_Raw_Data(Data_List)

    for i in range(3):
        for data in Data_List[i]:
            Data_Queue[i].append(data)
    return last_end


def Get_First_Element(data_queue):
    if(data_queue == []):
        return None
    else:
        data = data_queue[0]
        data_queue.pop(0)
        return data


def Get_Synchronous_Data(Data_Queue, Next_Data):
    for i in range(len(Next_Data)):
        next_data = Next_Data[i]
        if(next_data == None):
            Next_Data[i] = Get_First_Element(Data_Queue[i])
    
    synchronous = False
    while(synchronous == False):
        synchronous = True
        # certain router doesn't have data
        if(None in Next_Data):
            return None
        
        #check if the data is synchronous
        record_time = Next_Data[0]['record_time']
        for data in Next_Data:
            if(data['record_time']>record_time):
                record_time = data['record_time']
        threshold = timedelta(seconds=5)
        for data in Next_Data:
            if(record_time - data['record_time'] > threshold):
                synchronous = False
                break
        
        if(synchronous == False):
            # update the oldest data
            data_to_update = Next_Data[0]
            for data in Next_Data:
                if(data['record_time'] < data_to_update['record_time']):
                    data_to_update = data
            index = Next_Data.index(data_to_update)
            Next_Data[index] = Get_First_Element(Data_Queue[index])
    print('find a synchronous data')
    synchronous_data = []
    for i in range(len(Next_Data)):
        synchronous_data.append(Next_Data[i])
        Next_Data[i] = None
    return synchronous_data

def Get_Average_Data(Data_Queue, Next_Data, Fetch_Data):
    threshold = timedelta(seconds=5)
    if(Fetch_Data == []):
        Base_Data = Get_Synchronous_Data(Data_Queue, Next_Data)
        if(Base_Data == None):
            return None
        for data in Base_Data:
            Fetch_Data.append([data])
    
    base_time = Fetch_Data[0][0]['record_time']
    for data_list in Fetch_Data:
        if(data_list[0]['record_time'] < base_time):
            base_time = data_list[0]['record_time']
    
    for i in range(len(Fetch_Data)):
        while(True):
            next_data = Get_First_Element(Data_Queue[i])
            if(next_data == None):
                break
            
            if(next_data['record_time'] - base_time < threshold):
                Fetch_Data[i].append(next_data)
            else:
                Next_Data[i] = next_data
                break
    
    if (None in Next_Data):
        return None
    
    Average_Data=[]
    for i in range(len(Fetch_Data)):
        router_mac = Fetch_Data[i][0]['router_mac']
        averge_strength = 0
        for data in Fetch_Data[i]:
            averge_strength = averge_strength + data['signal_strength']
        averge_strength = averge_strength / len(Fetch_Data[i])
        Average_Data.append({'router_mac':router_mac, 'signal_strength':averge_strength, 'record_time':base_time})
    Fetch_Data.clear()
    return Average_Data
    
    
                

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __str__(self):
        return "({},{})".format(self.x, self.y)
    



def Get_Distance(data, A, n):
    PR = float(data['signal_strength'])
    distance = pow(10.0,(A - PR)/(10*n))
    print(distance)
    return distance

def Locate_Device_With_Distance(router_position, average_data):
    R = [-32, -36.9525, -45.0640]
    n = [2, 2, 2]
    distance = []
    for i in range(len(average_data)):
        data = average_data[i]
        distance.append(Get_Distance(data, R[i], n[i]))
    
    A = np.zeros((3,2))
    B = np.zeros((3,1))
    for i in range(3):
        A[i][0] = 2*(router_position[(i+1)%3].x - router_position[i].x)
        A[i][1] = 2*(router_position[(i+1)%3].y - router_position[i].y)
        B[i] =  pow(distance[i],2) - pow(distance[(i+1)%3],2) +\
                pow(router_position[(i+1)%3].x,2) -pow(router_position[i].x,2) +\
                pow(router_position[(i+1)%3].y,2) -pow(router_position[i].y,2)
    A = np.matrix(A)
    B = np.matrix(B)
    result = (A.T*A).I*A.T*B
    device_possion = Point(float(result[0][0]), float(result[1][0]))
    return device_possion

def Locate_Device_With_Signal(average_data):
    global Standard_Data_List
    signal = []
    for data in average_data:
        signal.append(float(data['signal_strength']))
    Delta_Data_List = []
    for standard_data in Standard_Data_List:
        # print("calculating distance for signal at",standard_data.position)
        # print("its signal data is ",standard_data.signal)
        # print("this point's signal data is ",signal)
        delta_data = []
        signal_distance = 0
        for i in range(len(signal)):
            delta_stength = abs(signal[i] - standard_data.signal[i])
            signal_distance += delta_stength**2
        signal_distance = signal_distance**0.5
        delta_data.append(signal_distance)
        delta_data.append(standard_data.position)
        
        Delta_Data_List.append(delta_data)
    
    Delta_Data_List.sort(key = lambda x:x[0])
    # for delta_data in Delta_Data_List:
    #     print("distance:", delta_data[0],"position:",delta_data[1])
    
    power = 4
    weight_sum = 0.0
    for delta_data in Delta_Data_List:
        if(delta_data[0] == 0):
            return Point(delta_data[1][0], delta_data[1][1])
        weight_sum += pow(2.71828, -delta_data[0]/2)
    
    device_position = [0.0, 0.0]
    device_position = np.array(device_position)
    for delta_data in Delta_Data_List:
        weight = pow(2.71828, -delta_data[0]/2)
        device_position += np.array(delta_data[1]) * (weight / weight_sum)
    device_position = Point(device_position[0], device_position[1])
    return device_position
    
            
            
         
def Handle_Collected_Data(Data_Queue, Next_Data, Fetch_Data, router_position, target_mac):

    count = 0
    while True:
        
        average_data = Get_Average_Data(Data_Queue, Next_Data, Fetch_Data)
        if(average_data == None):
            break
        count += 1
        record_time = average_data[0]['record_time']
        print("Handling Data[{}]:".format(count))
        
            
        print("record_time: {}".format(record_time))
        for i in range(len(average_data)):
            print("router_mac: {}".format(average_data[i]['router_mac']), end=" ")
            print("signal_strength: {}".format(average_data[i]['signal_strength']))
            
        # device_position = Locate_Device_With_Distance(router_position, average_data)
        device_position = Locate_Device_With_Signal(average_data)
        global Device_Position_List
        Device_Position_List.append(device_position)
        
        
        print("device position is {}".format(str(device_position)))
        # insert into database
        record = {'target_mac':target_mac, 'pos_t':record_time, 'pos_x':device_position.x, 'pos_y':device_position.y, 'pos_z':1.0}
        # db.insert_to_positions_database(record)
        print()
        
def Get_Average_Strength(Data_Queue):
    average_strength_list = []
    for i in range(len(Data_Queue)):
        router_mac = Data_Queue[i][0]['router_mac']
        averge_strength = 0
        for data in Data_Queue[i]:
            averge_strength = averge_strength + data['signal_strength']
        averge_strength = averge_strength / len(Data_Queue[i])
        average_strength_list.append(averge_strength)
        print("router {} get {} datas, average strength is {}".format(router_mac,len(Data_Queue[i]), averge_strength))
    
    for average_strength in average_strength_list:
        print("%.2f"%average_strength, end=", ")
    print()
    
delta_time = None
if sys.argv[1] == '--now' or sys.argv[1] == '-n':
    last_end = datetime.now()
elif sys.argv[1] == "--start":
    last_end = datetime.strptime(sys.argv[2], "%Y-%m-%d %H:%M:%S")
    delta_time = timedelta(0,int(sys.argv[3]))
else:
    last_end = None
    

    


router_mac_set= ['14:6b:9c:f4:04:67', '14:6b:9c:f4:04:16', '14:6b:9c:f4:04:31']
target_mac = "b8:14:4d:8a:2d:04"
# 3 lists, each store the data from a certain router
Data_Queue = [[],[],[]]
Next_Data = [None, None, None]
Fetch_Data = []
# the position of the routers
router_location = [[0.0, 0.0],[2.85, 0.0],[0.0, 5.45]]
router_position = []
Device_Position_List=[]
for router in router_location:
    router_position.append(Point(router[0], router[1]))

for i in range(len(Standard_Signal_List)):
    Standard_Data_List.append(Standard_Data(Standard_Signal_List[i], Standard_Position_List[i]))

if(delta_time == None):
    print("Updating...")
    last_end = Update_Data_Queue(Data_Queue, last_end, target_mac)
    Handle_Collected_Data(Data_Queue, Next_Data, Fetch_Data, router_position, target_mac)
    print()
    time.sleep(1)

print(delta_time)
if(delta_time != None):
    Update_Data_Queue(Data_Queue, last_end, target_mac, delta_time)
    Get_Average_Strength(Data_Queue)
    Handle_Collected_Data(Data_Queue, Next_Data, Fetch_Data, router_position, target_mac)
    x_list = [position.x for position in Device_Position_List]
    y_list = [position.y for position in Device_Position_List]
    way_x  = [0.0, 2.38, 2.38, 0.0 , 0.0 , 2.38, 2.38, 0.0,  0.0,  2.38]
    way_y  = [0.0, 0.0 , 0.55, 0.55, 1.09, 1.09, 1.64, 1.64, 2.18, 2.18]
    plt.scatter(x_list, y_list, c='r', marker='o', label='device position')
    plt.plot(way_x, way_y, color='b')
    plt.savefig('location.png')
    # print()
    

