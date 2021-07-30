from luma.core.interface.serial import spi
from luma.lcd.device import st7735
from PIL import Image, ImageDraw, ImageFont

font = ImageFont.truetype("/home/pi/code/UI/font.ttf", 18)

class lcd:
    def __init__(self):
        self.serial = spi(port=0, device=0, gpio_DC=17, gpio_RST=27)
        self.device = st7735(self.serial, width=160, height=128, rotate=1, h_offset=0, v_offset=0, bgr=False)
        self.buffer = Image.new(self.device.mode, self.device.size)
        self.draw = ImageDraw.Draw(self.buffer)
    
    def display(self, str_list, red_line=None):
        self.draw.rectangle(self.device.bounding_box, outline=None, fill=(3, 152, 152))
        for inx, str in enumerate(str_list):
            if inx == red_line:
                self.draw.text((4, inx * 19), str, "red", font=font)
            else:
                self.draw.text((4, inx * 19), str, "white", font=font)
        self.device.display(self.buffer)