from datetime import datetime
from ..exceptions import DeviceError
from ..utils import Cache


class EmeterHandler(object):

    def __init__(self, device):
        if not device.HasEmeter():
            raise DeviceError('Device does not support the emeter')
        self.device = device
        self.emeterType = device.GetEmeterType()
        self.__cache = Cache()

    def ClearDeviceStats(self):
        return self.Send(
            self.QueryHelper(self.emeterType, 'erase_emeter_stat', None))

    def GetAmps(self):
        value = self.GetRealtime()
        if value is None:
            raise DeviceError('Failed to get realtime emeter stats')
        if 'current' in value:
            return float(value['current'])
        return 0

    def GetConsumption(self):
        """
        Retrieve realtime energy concumption in watts
        """
        value = self.GetRealtime()
        if value is None:
            raise DeviceError('Failed to get realtime emeter stats')
        if 'power' in value:
            return float(value['power'])
        elif 'power_mw' in value:
            return float(value['power_mw'])
        raise DeviceError('Unknown output from emeter realtime')

    def GetDailyAverage(self):
        total = 0.0
        data = self.GetDailyUsage()
        for day in data:
            if 'energy' in day:
                total += float(day['energy'])
            elif 'energy_wh' in day:
                total += float(day['energy_wh'])
            else:
                return float(-1)
        if total <= 0:
            return 0.0
        return float(total / len(data))

    def GetDailyUsage(self, month=None, year=None):
        response = self.Send(
            self.QueryHelper(self.emeterType,
                'get_daystat', {
                    'month': int(month or datetime.now().month),
                    'year': int(year or datetime.now().year)
                }))

        data = response[self.emeterType]['get_daystat']['day_list']
        return data

    def GetMonthlyAverage(self):
        total = 0.0
        data = self.GetDailyUsage()
        for month in data:
            if 'energy' in month:
                total += float(month['energy'])
            elif 'energy_wh' in month:
                total += float(month['energy_wh'])
            else:
                return float(-1)
        if total <= 0:
            return 0.0
        return float(total / len(data))

    def GetMonthlyUsage(self, year=None):
        response = self.Send(
            self.QueryHelper(self.emeterType,
                'get_monthstat', {
                    'year': int(year or datetime.now().year)
                }))

        data = response[self.emeterType]['get_monthstat']['month_list']
        return data

    def GetRealtime(self, key=None):
        data = self.__cache.Get(self.emeterType)

        if data is None:
            data = self.Send(self.QueryHelper(self.emeterType, 'get_realtime'))

        if data is not None:
            self.__cache.Insert(self.emeterType, data)

        if key is not None:
            return data[self.emeterType]['get_realtime'].get(key)
        return data[self.emeterType]['get_realtime']

    def GetUsageMonth(self):
        data = self.GetDailyUsage()
        month = datetime.now().month
        year = datetime.now().year
        for entry in data:
            if entry['month'] == month and entry['year'] == year:
                if 'energy' in entry:
                    return float(entry['energy'])
                elif 'energy_wh' in entry:
                    return float(entry['energy_wh'])
                else:
                    return float(-1)
        return float(-1)

    def GetUsageToday(self):
        data = self.GetDailyUsage()
        today = datetime.now().day
        for entry in data:
            if entry['day'] == today:
                if 'energy' in entry:
                    return float(entry['energy'])
                elif 'energy_wh' in entry:
                    return float(entry['energy_wh'])
                else:
                    return float(-1)
        return float(-1)

    def GetVoltage(self):
        value = self.GetRealtime()
        if value is None:
            raise DeviceError('Failed to get realtime emeter stats')
        if 'voltage' in value:
            return float(value['voltage'])
        return 0

    def QueryHelper(self, *args):
        return self.device.QueryHelper(*args)

    def Send(self, message):
        return self.device.Send(message)
