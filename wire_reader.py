import glob
import time

# Old read functions

# TODO: optimise this function

def find_temp_sensors():
    base_dir = '/sys/bus/w1/devices/'
    return glob.glob(base_dir + '28*')

def read_temp_raw(device_file):
    with open(device_file, 'r') as f:
        return f.readlines()

def read_1wire_sensor(sensor):
    while True:
        lines = read_temp_raw(sensor + '/w1_slave')
        if lines[0].strip()[-3:] == 'YES':
            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_string = lines[1][equals_pos + 2:]
                return round(float(temp_string) / 1000.0, 2)
        time.sleep(0.2)

def read_1wire_sensors():
    temp_sensors = find_temp_sensors()
    temps = [read_1wire_sensor(sensor) for sensor in temp_sensors]
    return temps if temps else 'No temperature sensors found' # Return message if no sensors found for debugging