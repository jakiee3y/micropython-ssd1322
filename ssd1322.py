"""
MicroPython SSD1327 OLED I2C driver
https://github.com/mcauser/micropython-ssd1327

MIT License
Copyright (c) 2017 Mike Causer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__version__ = '1.1.1'

import time
from micropython import const
import framebuf

# commands
SET_COL_ADDR          = const(0x15)
SET_SCROLL_DEACTIVATE = const(0x2E)
SET_ROW_ADDR          = const(0x75)
SET_CONTRAST          = const(0x81)
SET_SEG_REMAP         = const(0xA0)
SET_DISP_START_LINE   = const(0xA1)
SET_DISP_OFFSET       = const(0xA2)
SET_DISP_MODE         = const(0xA4) # 0xA4 normal, 0xA5 all on, 0xA6 all off, 0xA7 when inverted
SET_MUX_RATIO         = const(0xA8)
SET_FN_SELECT_A       = const(0xAB)
SET_DISP              = const(0xAE) # 0xAE power off, 0xAF power on
SET_PHASE_LEN         = const(0xB1)
SET_DISP_CLK_DIV      = const(0xB3)
SET_SECOND_PRECHARGE  = const(0xB6)
SET_GRAYSCALE_TABLE   = const(0xB8)
SET_GRAYSCALE_LINEAR  = const(0xB9)
SET_PRECHARGE         = const(0xBC)
SET_VCOM_DESEL        = const(0xBE)
SET_FN_SELECT_B       = const(0xD5)
SET_COMMAND_LOCK      = const(0xFD)

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
        self.write_cmd(SET_FN_SELECT_A)
        self.write_data(0x00) # Disable internal VDD regulator, to save power
        self.write_cmd(SET_DISP)

    def poweron(self):
        self.write_cmd(SET_FN_SELECT_A)
        self.write_data(0x01) # Enable internal VDD regulator
        self.write_cmd(SET_DISP | 0x01)

    def contrast(self, contrast):
        self.write_cmd(SET_CONTRAST)
        self.write_data(contrast) # 0-255

    def rotate(self, rotate):
        self.poweroff()
        time.sleep_ms(5)
        self.write_cmd(SET_DISP_OFFSET)
        self.write_cmd(self.height if rotate else self.offset)
        self.write_cmd(SET_SEG_REMAP)
        self.write_cmd(0x42 if rotate else 0x51)
        self.poweron()
        time.sleep_ms(5)

    def invert(self, invert):
        self.write_cmd(SET_DISP_MODE | (invert & 1) << 1 | (invert & 1)) # 0xA4=Normal, 0xA7=Inverted

    '''
  // Set column address: Set_Column_Address(0x00, MAXCOLS-1);
  ssd1322_command1(0x15);
  // Each Column address holds 4 horizontal pixels worth of data
  const uint16_t Col0Off = 0x70;
  const uint16_t ColDiv  =    4;
  ssd1322_data1( (Col0Off+0x00)/ColDiv );
  ssd1322_data1( (Col0Off+WIDTH-1)/ColDiv );

  // Set row address: Set_Row_Address(0x00, MAXROWS-1);
  ssd1322_command1(0x75);
  ssd1322_data1(0x00);
  ssd1322_data1(HEIGHT-1);
  
  // Enable writing into MCU RAM: Set_Write_RAM();
  ssd1322_command1(0x5C);

  uint16_t count = WIDTH * ((HEIGHT) / 2);
  // serial_println(count);
  uint8_t *ptr   = buffer;
  SSD1322_MODE_DATA
  // while(count--) SPIwrite(*ptr++);
  spi->transfer(buffer,count); (void) ptr;
    '''
    def show(self):
        offset=(480-self.width)//2
        col_start=offset//4
        col_end=col_start+self.width//4-1
        self.write_cmd(SET_COL_ADDR)
        self.write_data(col_start)
        self.write_data(col_end)
        self.write_cmd(SET_ROW_ADDR)
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

'''
PA1     22     
PA2     19
PA3     23
--      18
PA5     5
--      17
PA7     16

#define PIN_DC       PA1  // DC: HIGH=Data, LOW=Command
#define PIN_CS       PA2  // Chip Select
#define PIN_RES      PA3 // Reset: HIGH during operation, LOW triggers reset)
SCK     PA5
MOSI    PA7

import time
import math
spi = SPI(2, polarity=0, phase=0, sck=Pin(5), mosi=Pin(16), miso=Pin(17))
# cs--25 dc--26 rst--27 mosi--14 sck--12 miso--13-no_need
# def __init__( self, spi, aDC, aReset, aCS) :
tft=TFT(spi,26,27,25)

'''

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
        if type(aCommand)==bytes or type(aCommand)==bytearray:
            self.spi.write(aCommand)
        else:
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


