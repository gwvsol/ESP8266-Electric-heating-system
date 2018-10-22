import machine
try:
   import utime as time
except:
   import time
try:
    import usocket as socket
except:
    import socket
try:
    import ustruct as struct
except:
    import struct
try:
    import uerrno as errno
except:
    import errno

# time zones is supported
TIME_ZONE = {-11: -11, -10: -10, -9: -9, -8: -8, -7: -7, -6: -6, -5: -5, \
-4: -4, -3: -3, -2: -2, -1: -1, 0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, \
7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12, 13: 13, 14: 14}
# months of summer and winter time
MONTH = {'sum': 3, 'win': 10} # 3 - march, 10 - october

# (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
NTP_DELTA = 3155673600
# NTP server
host = "pool.ntp.org"

def getntp():
    print('Get UTC time from NTP server...')
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1b
   # Handling an unavailable NTP server error
    try:
        addr = socket.getaddrinfo(host, 123)[0][-1]
    except OSError: # as exc:
        #if exc.args[0] == -2:
            print('Connect NTP Server: Error resolving pool NTP')
            return 0
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(1)
    res = s.sendto(NTP_QUERY, addr)
   # Handling NTP server long response error
    try:
        msg = s.recv(48)
    except OSError as exc:
        if exc.args[0] == errno.ETIMEDOUT:
            print('Connect NTP Server: Request Timeout')
            s.close()
            return 0
    s.close()
    val = struct.unpack("!I", msg[40:44])[0]
    return val - NTP_DELTA

#Calculate the last Sunday of the month
#https://ru.wikibooks.org/wiki/Реализации_алгоритмов/Вечный_календарь
def sunday(year, month):
    for d in range(1,32):
        a = (14 - month) // 12
        y = year - a
        m = month + 12 * a -2
        if (((d + y + y // 4 - y // 100 + y // 400 + (31 * m) // 12)) % 7) == 0: # 0 - Sunday
            if d + 7 > 31: 
                return d


#We calculate summer or winter time now
def adj_tzone(utc, zone):
    # Если текущий месяц больше 3(март) 
    if utc[1] > MONTH['sum']:
        # Проверяем равен ли месяц 10(октябрь) или меньше 10 и меньше ли дата последнего воскресенья месяца
        if utc[1] <= MONTH['win'] and utc[2] < sunday(utc[0], MONTH['win']):
            print('Set TIME ZONE Summer:', TIME_ZONE[zone])
            return TIME_ZONE[zone] # Возращаем летнее время
    # Если месяц равен 3(март) проверяем больше ли дата последнего воскресенья месяца
    if utc[1] == MONTH['sum'] and utc[2] >= sunday(utc[0], MONTH['sum']):
        print('Set TIME ZONE Summer:', TIME_ZONE[zone])
        return TIME_ZONE[zone] # Возращаем летнее время
    else:
        print('Set TIME ZONE Winter:', TIME_ZONE[zone] - 1)
        return TIME_ZONE[zone] - 1 # Во всех остальных случаях возращаем зимнее время


# Adjustment time.localtime in accordance with time zones and changes for summer and winter time
# Not the entire list of time zones is supported
def settime(ntp=True, zone=0, win=True): # По умолчанию включен переход на серзонное время
    if ntp:
        utc = time.localtime(getntp())  #При передаче параметра ntp=True включаем обноление времени с NTP
    else:
        utc = time.localtime()  # В противном случае, берем время localtime на микроконтроллере
    # We form a new cortege to upgrade from the time zone
    z = adj_tzone(utc, zone) if win else 0 # Проверяем включен ли переход на сезонное время
    zonetime = utc[0:3] + (0,) + (utc[3]+z,) + utc[4:6] + (0,)
    # We update the time taking into account the time zone and summer and winter time
    machine.RTC().datetime(zonetime)
    print('New Local Time: ', str(time.localtime()))
    
