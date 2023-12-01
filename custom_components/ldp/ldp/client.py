import asyncio

import requests
from datetime import datetime, timedelta
import aiohttp
from aiohttp import ClientTimeout

NUM_CHANNELS = 7

STATE_AUTO = 0
STATE_ON = 1
STATE_OFF = 2

STATE_NAMES = {
    STATE_AUTO: 'AUTO',
    STATE_ON: 'ON',
    STATE_OFF: 'OFF'
}

STATES = [STATE_AUTO, STATE_ON, STATE_OFF]


def get_current_ldp_time(now=None) -> int:
    if not now:
        now = datetime.now()
    return int((now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds() / 60)


def time_to_ldp_time(hours: int, minutes: int) -> int:
    return get_current_ldp_time(
        datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(hours=hours, minutes=minutes)
    )


def get_current_ldp_day() -> int:
    return datetime.now().weekday()


def get_current_ldp_month() -> int:
    return datetime.now().month - 1


def get_point_string(channel_id: int, time: int, value: int, day: int = 0, month: int = 0) -> str:
    return '{}:{}:{}:{}:{}'.format(month, day, channel_id - 1, time, value)


def parse_point_string(point_string: str) -> dict:
    point = point_string.split(':')

    if point[0] == 'END':
        raise ValueError("No point here")

    return {
        'id': int(point[0]),
        'month': int(point[1]),
        'day': int(point[2]),
        'channel_id': int(point[3]) + 1,
        'time': int(point[4]),
        'value': int(point[5])
    }


class LDPAPIClient(object):
    """LedDimmerPro API client v0.1"""
    ip: str = None
    sim: bool = False

    def __init__(self, ip: str):
        self.ip = ip
        self.session = aiohttp.ClientSession()

    async def session_close(self):
        await self.session.close()

    def simulate(self, sim: bool = True):
        self.sim = sim

    async def add_point(self, point_string: str) -> int:
        result = await self._request('point/add/{}'.format(point_string))
        result = result.split('|')[1].strip()
        return int(result)

    async def get_serial_number(self) -> str:
        result = await self._request('id')
        result = result.split('|')[1].strip()
        return result


    async def get_version(self) -> str:
        result = await self._request('ver')
        result = result.split('|')[1].strip()
        return result

    async def update_point(self, point_id: int, point_string: str) -> None:
        await self._request('point/upd/{}/{}'.format(point_id, point_string))

    async def delete_point(self, point_id: int) -> None:
        await self._request('point/del/{}'.format(point_id))

    async def get_point(self, point_id: int) -> str:
        response = await self._request('point/get/{}'.format(point_id))
        return response.split('|')[1]

    async def get_point_count(self) -> int:
        response = await self._request('point/count')
        return int(response.split('|')[1].strip())

    async def is_ldp(self) -> bool:
        try:
            response = await self._request('ldp')
        except asyncio.TimeoutError:
            return False
        return response.strip() == 'LDP|OK'

    async def get_channel(self, channel_id: int) -> list:
        response = await self._request('chn/get/{}'.format(channel_id))
        return response.split('|')

    async def get_states(self) -> list:
        response = await self._request('state/get')
        return response.split('|')

    async def set_state(self, channel_id: int, state: int) -> None:
        await self._request('state/set/{}/{}'.format(channel_id - 1, state))

    async def test(self, channel_id: int, value: int) -> None:
        await self._request('tst/{}/{}'.format(channel_id, value))

    async def end_test(self) -> None:
        await self._request('tst/-1')

    async def _request(self, path) -> str:
        if self.sim:
            print('GET', self._get_url(path))
            return ''

        timeout = ClientTimeout(total=5)
        async with self.session.get(self._get_url(path), timeout=timeout) as response:
            return await response.text()

    def _get_url(self, path) -> str:
        return "http://%s/%s" % (self.ip, path)
