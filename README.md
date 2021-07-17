This is a demo for using SSD1322 with micropython.<br/>
Tested on esp32(LOLIN32 Lite) and stm32f411ce(WeAct STM32F411CEU6). 

<table>
<tr><td><b>ssd1322</b></td><td><b>stm32f411ce</b></td></tr>
<tr><td>DC</td><td>PA1</td></tr>
<tr><td>CS</td><td>PA2</td></tr>
<tr><td>RESET</td><td>PA3</td></tr>
<tr><td>SCK</td><td>PA5</td></tr>
<tr><td>MOSI</td><td>PA7</td></tr>
</table>

<table>
<tr><td><b>ssd1322</b></td><td><b>esp32</b></td></tr>
<tr><td>DC</td><td>22</td></tr>
<tr><td>CS</td><td>19</td></tr>
<tr><td>RESET</td><td>23</td></tr>
<tr><td>SCK</td><td>5</td></tr>
<tr><td>MOSI</td><td>16</td></tr>
</table>

test code on esp32:
<pre>
import ssd1322
from machine import SPI,Pin
spi = SPI(2, baudrate=16000000,polarity=0, phase=0, sck=Pin(5), mosi=Pin(16), miso=Pin(17))
dc=Pin(22,Pin.OUT)
cs=Pin(19,Pin.OUT)
res=Pin(23,Pin.OUT)
disp=ssd1322.SSD1322_SPI(256,64,spi,dc,cs,res)
#disp.fill(0)
disp.line(5,5,60,60,0xff)
disp.show()
</pre>


test code on stm32:
<pre>
import ssd1322
from pyb import SPI,Pin
spi=SPI(1)
spi.init(SPI.MASTER,polarity=0,phase=0)
dc=Pin('A1',Pin.OUT)
cs=Pin('A2',Pin.OUT)
res=Pin('A3',Pin.OUT)
disp=ssd1322.SSD1322_SPI(256,64,spi,dc,cs,res)
disp.fill(15)
disp.show()
disp.fill(0)
disp.line(0,0,255,63,15)
disp.show()
</pre>
