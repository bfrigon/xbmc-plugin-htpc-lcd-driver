import serial
import xbmc
import string
import threading

## LCD commands ##
LCD_CMD_GOTO_ROW = 'd'
LCD_CMD_GOTO_COL = 'G'
LCD_CMD_GOTO = 'H'
LCD_CMD_CLEAR = 'J'
LCD_CMD_SET_CHAR = 'Y'
LCD_CMD_PRINT_CHAR = 'Z'
LCD_CMD_SET_MODE = 'm'
LCD_CMD_SET_LED = 'q'

LCD_KEY_UP = 0xF0
LCD_KEY_DOWN = 0xF1
LCD_KEY_RIGHT = 0xF2
LCD_KEY_LEFT = 0xF3
LCD_KEY_ENTER = 0x0D
LCD_KEY_ESC = 0x08

LCD_LED_ALLOFF = 0
LCD_LED_RECORD = 5
LCD_LED_MESSAGE = 6

LCD_LED_COLOR_GREEN = 0
LCD_LED_COLOR_RED = 1

class LcdDriver:
    

    
    
    def __init__(self):
        self.sio = serial.Serial('/dev/ttyUSB0', 38400)
        self.sio.flushInput()
        
        xbmc.sleep(1)
    
    def clear(self):
        self.sio.write('\033[2' + LCD_CMD_CLEAR)

    def setrgb(self, r, g, b):
        self.sio.write('\033[48;' + str(r) + ';' + str(g) + ';' + str(b) + LCD_CMD_SET_MODE)

    def goto(self, x=None, y=None):
        
        if x is None and y is None:
            return

        elif x is None and y is not None:
            self.sio.write('\033[' + str(y) + LCD_CMD_GOTO_ROW)    

        elif x is not None and y is None:
            elf.sio.write('\033[' + str(x) + LCD_CMD_GOTO_COL)    

        else:
            self.sio.write('\033[' + str(y) + ';' + str(x) + LCD_CMD_GOTO)
       
    def def_custom_char(self, id, data):
        if len(data) != 8:
            xbmc.log('def_custom_char data argument must be an 8 byte array', xbmc.LOGERROR)
            return
        
        self.sio.write('\033[' + str(id) + LCD_CMD_SET_CHAR)
        self.sio.write(data)
       
    def write_custom_char(self, id, x=None, y=None):
        self.goto(x, y)
        self.sio.write('\033[' + str(id) + LCD_CMD_PRINT_CHAR)


    def set_led(self, id, color):
        self.sio.write('\033[' + str(id) + ';' + str(color) + LCD_CMD_SET_LED)
       
       
    def write(self, data, x=None, y=None):
        self.goto(x, y)
        self.sio.write(data)


    def read_next_key(self):
        
        ## Check if input buffer is empty ##
        if not self.sio.inWaiting():
            return None
        
        key = self.sio.read(1)
        if key == '\033': ## Extended key ##
            if self.sio.read(1) != '[':
                return None
            
            key = self.sio.read(1)
            return ord(key) - 65 + 0xF0
            
        else: ## Single character ##
            return ord(key)
