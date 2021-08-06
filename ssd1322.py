"""
outline: https://github.com/mcauser/micropython-ssd1327
init sequence/write buffer: https://github.com/JamesHagerman/Jamis_SSD1322
other: SSD1322 Advance Information 480 x 128, Dot Matrix High Power OLED/PLED Segment/Common Driver with Controller 
       (9 COMMAND TABLE)  https://www.newhavendisplay.com/resources_dataFiles/datasheets/OLEDs/SSD1322.pdf
"""
__version__ = '0.1'

import time
import framebuf

class SSD1322:
    def __init__(self, width=256, height=64):
        self.width = width
        self.height = height
        self.buffer = bytearray(self.width * self.height //2)
        self.framebuf = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.GS4_HMSB)

        # self.poweron()
        time.sleep_ms(5)
        self.init_display()

    def init_display(self):
        self.write_cmd(0xFD)  # Set Command Lock (MCU protection status)
        self.write_data(0x12)  # 0x12 = Unlock Basic Commands; 0x16 = lock

        self.write_cmd(0xA4)  # Set Display Mode = OFF

        self.write_cmd(0xB3)  # Set Front Clock Divider / Oscillator Frequency
        self.write_data(0x91)  # 0x91 = 80FPS; 0xD0 = default / 1100b 

        self.write_cmd(0xCA)  # Set MUX Ratio
        self.write_data(0x3F)  # 0x3F = 63d = 64MUX (1/64 duty cycle)

        self.write_cmd(0xA2)  # Set Display Offset
        self.write_data(0x00)  # 0x00 = (default)

        self.write_cmd(0xA1)  # Set Display Start Line
        self.write_data(0x00)  # 0x00 = register 00h

        self.write_cmd(0xA0)  # Set Re-map and Dual COM Line mode
        self.write_data(0x14)  # 0x14 = Default except Enable Nibble Re-map, Scan from COM[N-1] to COM0, where N is the Multiplex ratio
        self.write_data(0x11)  # 0x11 = Enable Dual COM mode (MUX <= 63)

        self.write_cmd(0xB5)  # Set GPIO
        self.write_data(0x00)  # 0x00 = {GPIO0, GPIO1 = HiZ (Input Disabled)}

        self.write_cmd(0xAB)  # Function Selection
        self.write_data(0x01)  # 0x01 = Enable internal VDD regulator (default)

        self.write_cmd(0xB4)  # Display Enhancement A
        self.write_data(0xA0)  # 0xA0 = Enable external VSL; 0xA2 = internal VSL
        self.write_data(0xB5)  # 0xB5 = Normal (default); 0xFD = 11111101b = Enhanced low GS display quality

        self.write_cmd(0xC1)  # Set Contrast Current
        self.write_data(0x7F)  # 0x7F = (default)

        self.write_cmd(0xC7)  # Master Contrast Current Control
        self.write_data(0x0F)  # 0x0F = (default)

        self.write_cmd(0xB8)  # Select Custom Gray Scale table (GS0 = 0)
        self.write_data(0x00)  # GS1
        self.write_data(0x02)  # GS2
        self.write_data(0x08)  # GS3
        self.write_data(0x0d)  # GS4
        self.write_data(0x14)  # GS5
        self.write_data(0x1a)  # GS6
        self.write_data(0x20)  # GS7
        self.write_data(0x28)  # GS8
        self.write_data(0x30)  # GS9
        self.write_data(0x38)  # GS10
        self.write_data(0x40)  # GS11
        self.write_data(0x48)  # GS12
        self.write_data(0x50)  # GS13
        self.write_data(0x60)  # GS14
        self.write_data(0x70)  # GS15
        self.write_data(0x00)  # Enable Custom Gray Scale table

        self.write_cmd(0xB1)  # Set Phase Length
        self.write_data(0xE2)  # 0xE2 = Phase 1 period (reset phase length) = 5 DCLKs,
                               # Phase 2 period (first pre-charge phase length) = 14 DCLKs
        self.write_cmd(0xD1)  # Display Enhancement B
        self.write_data(0xA2)  # 0xA2 = Normal (default); 0x82 = reserved
        self.write_data(0x20)  # 0x20 = as-is

        self.write_cmd(0xBB)  # Set Pre-charge voltage
        self.write_data(0x1F)  # 0x17 = default; 0x1F = 0.60*Vcc (spec example)

        self.write_cmd(0xB6)  # Set Second Precharge Period
        self.write_data(0x08)  # 0x08 = 8 dclks (default)

        self.write_cmd(0xBE)  # Set VCOMH
        self.write_data(0x07)  # 0x04 = 0.80*Vcc (default); 0x07 = 0.86*Vcc (spec example)

        self.write_cmd(0xA6)  # Set Display Mode = Normal Display
        self.write_cmd(0xA9)  # Exit Partial Display
        self.write_cmd(0xAF)  # Set Sleep mode OFF (Display ON)
        
        self.fill(0)
        self.write_data(self.buffer)

    def poweroff(self):
        self.write_cmd(0xAB)
        self.write_data(0x00) # Disable internal VDD regulator, to save power
        self.write_cmd(0xAE)

    def poweron(self):
        self.write_cmd(0xAB)
        self.write_data(0x01) # Enable internal VDD regulator
        self.write_cmd(0xAF)

    def contrast(self, contrast):
        self.write_cmd(0x81)
        self.write_data(0x81) # 0-255

    def rotate(self, rotate):
        self.write_cmd(0xA0)
        self.write_data(0x06 if rotate else 0x14)
        self.write_data(0x11)

    def invert(self, invert):
        self.write_cmd(0xA4 | (invert & 1) << 1 | (invert & 1)) # 0xA4=Normal, 0xA7=Inverted

    def show(self):
        offset=(480-self.width)//2
        col_start=offset//4
        col_end=col_start+self.width//4-1
        self.write_cmd(0x15)
        self.write_data(col_start)
        self.write_data(col_end)
        self.write_cmd(0x75)
        self.write_data(0)
        self.write_data(self.height-1)
        self.write_cmd(0x5c)
        self.write_data(self.buffer)

    def fill(self, col):
        self.framebuf.fill(col)

    def pixel(self, x, y, col):
        self.framebuf.pixel(x, y, col)

    def pp(self,x,y,col):
        self.buffer[self.width//2*y+x//2]=0xff if col else 0

    def line(self, x1, y1, x2, y2, col):
        self.framebuf.line(x1, y1, x2, y2, col)

    def scroll(self, dx, dy):
        self.framebuf.scroll(dx, dy)
        # software scroll

    def text(self, string, x, y, col=15):
        self.framebuf.text(string, x, y, col)

    def write_cmd(self):
        raise NotImplementedError

    def write_data(self):
        raise NotImplementedError

class SSD1322_SPI(SSD1322):
    def __init__(self, width, height, spi, dc,cs,res):
        self.spi = spi
        self.dc=dc
        self.cs=cs
        self.res=res

        self.res(1)
        time.sleep_ms(1)
        self.res(0)
        time.sleep_ms(10)
        self.res(1)

        super().__init__(width, height)
        time.sleep_ms(5)

    def write_cmd( self, aCommand ) :
        '''Write given command to the device.'''
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([aCommand]))
        self.cs(1)

    #@micropython.native
    def write_data( self, aData ) :
        '''Write given data to the device.  This may be
           either a single int or a bytearray of values.'''
        self.dc(1)
        self.cs(0)
        if type(aData)==bytes or type(aData)==bytearray:
            self.spi.write(aData)
        else:
            self.spi.write(bytearray([aData]))
        self.cs(1)
