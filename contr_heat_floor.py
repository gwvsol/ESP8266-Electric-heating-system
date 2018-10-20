from time import ticks_ms, ticks_diff, sleep_ms
from machine import I2C, Pin
import uasyncio as asyncio
import time, timezone, network, gc

i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000) # Настройка шины i2c

class ControlHeated(object):
    wifi_led = Pin(2, Pin.OUT, value = 1)
    def __init__(self):
        # Основное хранилище настроек
        config = {}
        self.internet_outage = True #Интернет отключен(значение True)
        #Читаем из файла настройки WiFi и Временную зону
        with open('config.txt') as conf_file:
            config['ssid'] = conf_file.readline().rstrip()
            config['wf_pass'] = conf_file.readline().rstrip()
            config['timezone'] = int(conf_file.readline().rstrip())
        # Числа для часов от 0 до 9 с добавлением 0 для часов
        config['num'] = ('00', '01', '02', '03', '04', '05', '06', '07', '08', '09')
           
        loop = asyncio.get_event_loop()
        loop.create_task(self._heartbeat())
        loop.create_task(self._update_time())
        
        
    # Индикация подключения WiFi
    async def _heartbeat(self):
        while True:
            if self.internet_outage:
                self.wifi_led(not self.wifi_led()) # Быстрое мигание, если соединение отсутствует
                await asyncio.sleep_ms(200) 
            else:
                self.wifi_led(0) # Редкое мигание при подключении
                await asyncio.sleep_ms(50)
                self.wifi_led(1)
                await asyncio.sleep_ms(5000)
                
    # Получение времени с сервера NTP и обноление по Time Zone
    async def _update_time(self):
        while True:
            if self.internet_outage:
                await asyncio.sleep(5) #Если нет соединения с интернетом, ожидаем 5с
            else:
                timezone.stime(config['timezone'], True)
                if time.localtime()[0] == 2000:
                    await asyncio.sleep(30)
                else:
                    await asyncio.sleep(300)

    
    #Выводим отладочные сообщения        
    def dprint(self, *args):
        if self.DEBUG:
            print(*args)

            
    #Подключаемся к WiFi
    async def _connect_to_WiFi(self):
        self.dprint('Connecting to WiFi...')
        sta_if = network.WLAN(network.STA_IF)
        sta_if.active(True)
        sta_if.connect(config['ssid'], config['wf_pass'])
        self.dprint('Connected!')
        await asyncio.sleep(5)
        self.ip = sta_if.ifconfig()[0]
        self.internet_outage = False #Интернет подключен(значение False)
        

    async def _run_main_loop(self): #Бесконечный цикл
        mins = 0
        while True:
            gc.collect() #Очищаем RAM
            mem_free = gc.mem_free()
            mem_alloc = gc.mem_alloc()
            loctime = time.localtime()
            try:
                self.dprint('Uptime:', str(mins)+' min')
                self.dprint('Local Time:', loctime)
                self.dprint('Not WiFi:', self.internet_outage)
                self.dprint('IP:', self.ip)
                self.dprint('MemFree:', str(round(mem_free/1024, 2))+' Kb')
                self.dprint('MemAlloc:', str(round(mem_alloc/1024, 2))+' Kb')
            except Extension as e:
                self.dprint('Exception occurred: ', e)
            mins += 1
            await asyncio.sleep(60)

           
    async def main(self):
         while True:
             try:
                 await self._connect_to_WiFi()
                 await self._run_main_loop()    
             except Exception as e:
                 self.dprint('Global communication failure: ', e)
                 await asyncio.sleep(20)
                              
ControlHeated.DEBUG = True	# Режим отладки, делаем программу разговорчивой
        
gc.collect()
controll = ControlHeated()
loop = asyncio.get_event_loop()
loop.run_until_complete(controll.main())

