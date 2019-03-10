## Контроллер электрического отопления на ESP8266

[![micropython](https://user-images.githubusercontent.com/13176091/53680744-4dfcc080-3ce8-11e9-94e1-c7985181d6a5.png)](https://micropython.org/)

Контроллер для управления нагревом теплого пола. Собран на ESP8266. В качестве датчика температуры используется DS18B20, а часов времени DS3231. Для расчета выдаваемой мощности на нагревательный элемент используется PID регулятор. Для управления нагревательным элементом, симистор BTA41-600 с током до 40А. Питание контроллера выполнено на HLK-PM03 3W.

#### Функции контроллера
* Поддержание заданной температуры в помещении
* Работа по рассписанию
* Работа по 2 тарифам, день и ночь
* Автоматический переход с летнего на зимнее время
* Автоматическая подводка часов по NTP серверу, один раз в сутки, при наличии WiFi соединения.
* Web интерфейс для настройки контроллера

***
#### Используемые библиотеки
* [OneWire](https://github.com/micropython/micropython/blob/master/drivers/onewire/onewire.py)
* [DS18B20](https://github.com/gwvsol/ESP8266-1wire-DS18B20)
* [DS3231](https://github.com/gwvsol/ESP8266-i2c-DS3231)
* [PID](https://github.com/gwvsol/ESP8266-PID-controller)
* [timezone](https://github.com/gwvsol/ESP8266-TimeZone)
* [collections](https://github.com/micropython/micropython-lib/tree/master/collections/collections) и зависимости
* [uasyncio](https://github.com/micropython/micropython-lib/tree/master/uasyncio/uasyncio) и зависисмоти
* [picoweb](https://github.com/pfalcon/picoweb)

#### Описание работы контроллера
В работе контроллера используется PID регулятор. Обновление данных темературы происходит с интервалом в 15с. С этим же интервалом происходит обновление выдаваемой мощности на регулирующий элемент.

Контроллер поддерживает работу по 2 тарифам, день с 7:00:00 до 22:59:59 и ночь в остальное время. В зимнее время, с последнего воскресенья октября по последнее воскреснье марта тарифная зона день, автоматические сдвигается на 1 час назад, т.е с 6:00:00 до 21:59:59

В дневное время, контролер поддерживает изменение выдаваемой мощности на нагревательный элемент. Выдаваемую мощность можно задать в пределах от 10 до 90%. В ночное время ограничение мощности отсутствует и устанавливается на 90%. При этом всегда выдаваемая мощность зависит от температуры в помещении. Расчет выдаваемой мощности ведется PID регулятором.

Вход в ADMIN панель по логину и паролю. Дефолтный логин и пароль ```Login: root Passwd: root``` При необходимости, дефолтный логин и пароль могут быть изменены. Если изменный пароль от ADMIN панели утерян, контроллер позволяет сбросить настройки, для этого используется кнопка ```DEFAULT``` на плате контроллера. Для сброса в дефолт необходимо нажать кнопку и замкнуть контакты ```RESET``` на плате или выключить и включить контроллер. После чего необходимо настроить контроллер как при первом его включении.

При первом включениии контроллера, поднимается точка доступа ```HEAT_CONTROL``` c паролем ```roottoor```. При этом светодиод работы сети, будет мигать быстро 2 раза с интервалом 5с. Подключившись к этой точке доступа и зайдя по адресу ```192.168.4.1``` необходимо сделать необходимые настройки контроллера. После чего выключить и включить контроллер, или же замкнуть контакты ```RESET```

Если соединение по каким-либо причинам отсутствует, светодиод будет мигать всегда очень быстро. При нормальном подключении, сетодиод быстро моргает 1 раз в 5с.

Второй светодиод, светится с переменной яркостью, что соответствует разной мощности выдаваемой контроллером на нагревательный элемент. 

В контроллере отсутствует API интерфейс, это связано с ограниченностью памяти контроллера. Иногда памяти контроллера бывает не достаточно для обработки частых запросов из web интерфейса ADMIN панели.

#### Web интерфейс контроллера

![2019-03-07-11-22-041](https://user-images.githubusercontent.com/13176091/53958577-13c95f80-40ea-11e9-99eb-b88225341520.png)
![2019-03-07-11-23-031](https://user-images.githubusercontent.com/13176091/53958604-25ab0280-40ea-11e9-8cd7-16ac8b550ae0.png)
![2019-03-07-11-23-391](https://user-images.githubusercontent.com/13176091/53958630-365b7880-40ea-11e9-97dd-8bedabba2449.png)
![2019-03-07-11-23-521](https://user-images.githubusercontent.com/13176091/53958651-496e4880-40ea-11e9-92eb-2001473560c5.png)
![2019-03-07-11-23-591](https://user-images.githubusercontent.com/13176091/53958675-5b4feb80-40ea-11e9-9d7a-a62161b6a90e.png)

#### Файл настроек контроллера

```bash
{
    "pass": "Fedex##54", 
    "DAY": 50, 
    "DST": true, 
    "ssid": "w2234", 
    "DS_K": -5.0, 
    "MODE": "ST", 
    "timezone": 3, 
    "ON": [0, 0, 0, 22, 0, 0, 0, 0],
    "OFF": [0, 0, 0, 8, 0, 0, 0, 0],
    "WORK": "ON", 
    "SET": 20.0
}
```
Подавляющее большинство настроек этого файла изменяются через Web интерфейс. Исключение составляют только ```"DS_K": -4.5```. Парамер ```DS_K``` необходим для корректировки измерения температуры.

Для установки в контроллер нового файла ```config.txt``` используется USB-UART преобразователь с уровнями сигнала 3,3v, а так же утилита ```ampy```.
```bash
ampy put config.txt
```
Файл ```root.txt``` используется для хранения ```hash``` логина и пароля. По умолчанию этот файл хранит ```hash``` ```root:root```. Если же в процессе работы логин и пароль был изменен, файл будет содержать новый ```hash```.

Во время первого включения, создаются эти два файла, которые в дальнейшем используются для работы контроллера.

#### Компиляция
Для компиляции используется [SDK for ESP8266/ESP8285 chips](https://github.com/pfalcon/esp-open-sdk). 

После компиляции, необходимо очистить чип ESP8266 и залить новую прошивку, для чего используется ```esptool```
```bash
pip3 install setuptools
pip3 install esptool
```
```bash
esptool.py --port /dev/ttyUSB0 erase_flash
esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect -fm dio 0 firmware-combined.bin
```
***

#### Фото платы контроллера

![kontroll](https://user-images.githubusercontent.com/13176091/53958863-c0a3dc80-40ea-11e9-83a1-418c6be681c4.png)

***

