import pymysql.cursors
import json
from datetime import datetime

# Connect to the database


def connect_to_mysql():
    connection = pymysql.connect(host=,
                                 user=,
                                 password=,
                                 database='wifi',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection


connection = connect_to_mysql()

def insert_to_signals_database(raw_data: str):
    # Reconnect to mysql server if necessary
    global connection
    if connection.open == False:
        connection = connect_to_mysql()

    # Drop the leading "data="
    if raw_data.startswith("data="):
        raw_data = raw_data[len("data="):]
    json_data = json.loads(raw_data)
    time_str: str = json_data["time"]
    # Convert format of time
    # parse from something like "Mon Apr 17 17:43:54 2023"
    datetime_obj = datetime.strptime(time_str, "%a %b %d %H:%M:%S %Y")
    # generate something like "2038-01-19 03:14:07"
    time_mysql_str = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")

    router_mac = json_data["mmac"]

    with connection.cursor() as cursor:
        for x in json_data["data"]:
            if "router" not in x and "mac" in x and "rssi" in x:  # make sure it is not a router
                target_mac = x["mac"]
                signal_strength = float(x["rssi"])
                sql = "INSERT INTO signals (record_time, router_mac, target_mac, signal_strength) VALUES ('%s', '%s', '%s', %.1f)" % (
                    time_mysql_str, router_mac, target_mac, signal_strength)
                cursor.execute(sql)
    connection.commit()

def find_target_mac_from_database(target_mac, start_datetime=None, end_datetime=None):
    # Reconnect to mysql server if necessary
    global connection
    if connection.open == False:
        connection = connect_to_mysql()
    result = None
    with connection.cursor() as cursor:
        sql = "SELECT record_time, router_mac, target_mac, signal_strength FROM signals WHERE target_mac='%s'" % (target_mac)
        if start_datetime != None:
            sql += "AND record_time > '%s'" % (start_datetime)
        if end_datetime != None:
            sql += "AND record_time <= '%s'" % (end_datetime)
        cursor.execute(sql)
        result = cursor.fetchall()
    connection.close()
    return result

def insert_to_positions_database(record):
    # Reconnect to mysql server if necessary
    global connection
    if connection.open == False:
        connection = connect_to_mysql()
    connection.commit()
    with connection.cursor() as cursor:
        sql = "INSERT INTO positions (target_mac, pos_t, pos_x, pos_y, pos_z) VALUES ('%s', '%s', %.2f, %.2f, %.2f)" % (record["target_mac"], record["pos_t"], record["pos_x"], record["pos_y"], record["pos_z"])
        cursor.execute(sql)
    connection.commit()

def query_positions_database(target_mac, start_datetime=None, end_datetime=None):
    # Reconnect to mysql server if necessary
    global connection
    if connection.open == False:
        connection = connect_to_mysql()
    result = None
    with connection.cursor() as cursor:
        sql = "SELECT target_mac, pos_t, pos_x, pos_y, pos_z FROM positions WHERE target_mac='%s'" % (target_mac)
        if start_datetime != None:
            sql += "AND pos_t > '%s'" % (start_datetime)
        if end_datetime != None:
            sql += "AND pos_t <= '%s'" % (end_datetime)
        cursor.execute(sql)
        result = cursor.fetchall()
    connection.close()
    return result

if __name__ == "__main__":
    raw = r'{"id":"00f40431","data":[{"mac":"9c:8c:d8:01:08:24","rssi":"-62","router":"My BJMU","range":"7.7"},{"mac":"70:3a:0e:9a:0d:63","rssi":"-85","router":"My BJMU","range":"55.0"},{"mac":"9c:8c:d8:fe:3f:44","rssi":"-89","router":"My BJMU","range":"77.4"},{"mac":"9c:8c:d8:fd:ff:21","rssi":"-77","router":"PKU Visitor","range":"27.8"},{"mac":"9c:8c:d8:fd:ff:22","rssi":"-77","router":"PKU Secure","range":"27.8"},{"mac":"9c:8c:d8:fd:ff:23","rssi":"-78","router":"eduroam","range":"30.3"},{"mac":"9c:8c:d8:fd:ff:24","rssi":"-80","router":"My BJMU","range":"35.9"},{"mac":"9c:8c:d8:fd:ff:20","rssi":"-77","tmc":"c8:94:02:b8:ad:d7","router":"PKU","range":"27.8"},{"mac":"70:3a:0e:99:ff:e1","rssi":"-88","range":"71.0"},{"mac":"9c:8c:d8:01:08:22","rssi":"-64","tmc":"1e:dc:95:9d:e8:07","router":"PKU Secure","range":"9.1"},{"mac":"9c:8c:d8:01:08:23","rssi":"-65","tmc":"1e:dc:95:9d:e8:07","router":"eduroam","range":"10.0"},{"mac":"70:3a:0e:89:f1:c1","rssi":"-83","router":"eduroam","range":"46.4"},{"mac":"9c:8c:d8:01:08:20","rssi":"-65","router":"PKU","range":"10.0"},{"mac":"9c:8c:d8:01:08:21","rssi":"-65","router":"PKU Visitor","range":"10.0"},{"mac":"70:3a:0e:9a:0d:60","rssi":"-84","range":"50.5"},{"mac":"70:3a:0e:9a:0d:64","rssi":"-84","range":"50.5"},{"mac":"70:3a:0e:8a:02:60","rssi":"-83","range":"46.4"},{"mac":"70:3a:0e:8a:02:61","rssi":"-82","range":"42.6"},{"mac":"70:3a:0e:8a:02:62","rssi":"-83","range":"46.4"},{"mac":"70:3a:0e:8a:02:63","rssi":"-83","router":"My BJMU","range":"46.4"},{"mac":"80:8d:b7:7f:c2:64","rssi":"-87","range":"65.2"},{"mac":"80:8d:b7:7f:c2:65","rssi":"-91","router":"My BJMU","range":"91.8"},{"mac":"70:3a:0e:8a:02:01","rssi":"-83","range":"46.4"},{"mac":"70:3a:0e:8a:02:03","rssi":"-87","router":"My BJMU","range":"65.2"},{"mac":"70:3a:0e:99:ff:e3","rssi":"-90","router":"My BJMU","range":"84.3"},{"mac":"70:3a:0e:89:f1:c3","rssi":"-85","rssi1":"-86","tmc":"5c:c3:36:8e:77:38","router":"My BJMU","range":"55.0"},{"mac":"54:32:c7:d0:b1:da","rssi":"-52","ts":"Network","tmc":"32:80:8a:f2:5b:13","tc":"Y","range":"3.3"},{"mac":"b8:14:4d:8a:2d:04","rssi":"-70","rssi1":"-70","rssi2":"-70","rssi3":"-70","ts":"Network","tmc":"32:80:8a:f2:5b:13","tc":"Y","range":"15.3"},{"mac":"9c:8c:d8:00:59:c4","rssi":"-55","router":"My BJMU","range":"4.2"},{"mac":"70:3a:0e:9a:0b:80","rssi":"-82","router":"PKU","range":"42.6"},{"mac":"70:3a:0e:9a:0b:81","rssi":"-81","router":"eduroam","range":"39.1"},{"mac":"70:3a:0e:9a:0b:82","rssi":"-83","router":"PKU Secure","range":"46.4"},{"mac":"70:3a:0e:9a:0b:83","rssi":"-85","router":"My BJMU","range":"55.0"},{"mac":"7c:b5:9b:f4:f4:3c","rssi":"-96","tmc":"50:2b:73:18:0b:15","router":"806","range":"140.6"},{"mac":"70:3a:0e:9a:0a:20","rssi":"-68","router":"PKU","range":"12.9"},{"mac":"70:3a:0e:9a:0a:21","rssi":"-67","router":"eduroam","range":"11.8"},{"mac":"70:3a:0e:9a:0a:22","rssi":"-68","router":"PKU Secure","range":"12.9"},{"mac":"70:3a:0e:9a:0a:23","rssi":"-70","router":"My BJMU","range":"15.3"},{"mac":"70:3a:0e:9a:0a:24","rssi":"-68","router":"PKU Visitor","range":"12.9"},{"mac":"ec:26:ca:d9:4a:e2","rssi":"-87","router":"FerdinandDeSaussure","range":"65.2"},{"mac":"70:3a:0e:9a:05:01","rssi":"-84","router":"eduroam","range":"50.5"},{"mac":"9c:8c:d8:00:59:c0","rssi":"-54","router":"PKU","range":"3.9"},{"mac":"9c:8c:d8:00:59:c2","rssi":"-55","router":"PKU Secure","range":"4.2"},{"mac":"9c:8c:d8:00:04:01","rssi":"-79","router":"PKU Visitor","range":"33.0"},{"mac":"9c:8c:d8:00:04:02","rssi":"-81","router":"PKU Secure","range":"39.1"},{"mac":"9c:8c:d8:00:04:03","rssi":"-81","router":"eduroam","range":"39.1"},{"mac":"9c:8c:d8:00:04:04","rssi":"-81","router":"My BJMU","range":"39.1"},{"mac":"70:3a:0e:9a:05:03","rssi":"-88","router":"My BJMU","range":"71.0"},{"mac":"70:3a:0e:8a:12:44","rssi":"-84","router":"My BJMU","range":"50.5"},{"mac":"9c:8c:d8:00:59:c1","rssi":"-54","router":"PKU Visitor","range":"3.9"},{"mac":"9c:8c:d8:00:59:c3","rssi":"-54","router":"eduroam","range":"3.9"},{"mac":"9c:8c:d8:00:04:00","rssi":"-80","router":"PKU","range":"35.9"},{"mac":"70:3a:0e:9a:04:40","rssi":"-77","router":"PKU","range":"27.8"}],"mmac":"14:6b:9c:f4:04:31","rate":"1","time":"Mon Apr 17 17:43:58 2023","lat":"","lon":""}'
    # insert_to_database(raw)
    result = find_target_mac_from_database("b8:14:4d:8a:2d:04")
    print(type(result))
    print(len(result))
    print(result)
