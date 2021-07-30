import smbus
import time, struct

motor_addr = [0x01, 0x02, 0x04, 0x03]

class motor:
    def __init__(self):
        self.bus = smbus.SMBus(1)

    def run(self, speed_list):
        assert len(speed_list) == 4
        # print(speed_list)
        for addr, speed in zip(motor_addr, speed_list):
            speed = int(speed)
            assert speed >= -105 and speed <= 105
            # self.bus.write_byte_data(addr, 0x00, 83) #S: 83
            # now_time = time.time()
            try:
                self.bus.write_byte_data(addr, 115, speed)
                time.sleep(0.00005)
            except BaseException as e:
                print(str(time.time()) + ": " + str(e))
            # print((time.time() - now_time) * 1000)
            # time.sleep(0.01)
    
    def detect(self):
        # print(speed_list)
        for addr in motor_addr:
            # self.bus.write_byte_data(addr, 0x00, 83) #S: 83
            # now_time = time.time()
            try:
                self.bus.write_byte_data(addr, 116, 0)
            except BaseException as e:
                print(str(time.time()) + ": " + str(e))
            # print((time.time() - now_time) * 1000)
            # time.sleep(0.01)