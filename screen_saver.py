#!/usr/bin/env python

import curses
import socket
import time
import requests
import datetime

def kelvin_to_farenheight(temp_k):
    return (temp_k - 273.15) * 9 / 5 + 32


def hpa_to_hg(hpa):
    return hpa * 0.0295299830714


def mps_to_mph(mps):
    return mps * 2.2369362920544


def utc_to_local(utc, offset):
    return datetime.datetime.utcfromtimestamp(utc + offset)


class Weather:
    API_KEY = "687e52a4aa4828f3c8139ca794fd180c"
    FIELDS = (
        'temp_f', 'feels_like_f', 'temp_min_f', 'temp_max_f', 'pressure_hg', 'humidity_pct',
        'wind_speed_mph', 'wind_direction_deg', 'cloud_cover_pct', 'time_zone_offset',
        'sunrise_utc', 'sunset_utc', 'location_name', 'last_update')

    def __init__(self, location):
        self.location = location
        self.last_call = None
        self.last_update = None
        self._reset()

    def _reset(self):
        self.weather = {field: '' for field in Weather.FIELDS}
        self.last_call = datetime.datetime.now()

    def get_weather(self):
        self._reset()
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={self.location[0]}&lon={self.location[1]}&appid={Weather.API_KEY}"
        try:
            response = requests.get(url)
            if response.ok:
                self.last_update = self.last_call
                weather_data = response.json()
                self.weather['temp_f'] = f"{kelvin_to_farenheight(weather_data['main']['temp']):<3.0f}"
                self.weather['feels_like_f'] = f"{kelvin_to_farenheight(weather_data['main']['feels_like']):<3.0f}"
                self.weather['temp_min_f'] = f"{kelvin_to_farenheight(weather_data['main']['temp_min']):<3.0f}"
                self.weather['temp_max_f'] = f"{kelvin_to_farenheight(weather_data['main']['temp_max']):<3.0f}"
                self.weather['pressure_hg'] = f"{hpa_to_hg(weather_data['main']['pressure']):<5.2f}"
                self.weather['humidity_pct'] = f"{weather_data['main']['humidity']:<3d}"
                self.weather['wind_speed_mph'] = f"{mps_to_mph(weather_data['wind']['speed']):<3.0f}"
                self.weather['wind_direction_deg'] = f"{weather_data['wind']['deg']:<3.0f}"
                self.weather['cloud_cover_pct'] = f"{weather_data['clouds']['all']:<3d}"
                self.weather['time_zone_offset'] = f"{weather_data['timezone']}"
                self.weather['sunrise_utc'] = utc_to_local(weather_data['sys']['sunrise'],
                                                           weather_data['timezone']).strftime('%Y-%m-%d %H:%M:%S')
                self.weather['sunset_utc'] = utc_to_local(weather_data['sys']['sunset'],
                                                          weather_data['timezone']).strftime('%Y-%m-%d %H:%M:%S')
                self.weather['location_name'] = weather_data['name']
                self.weather['last_update'] = self.last_update.strftime('%Y-%m-%d %H:%M:%S')
        except:
            pass

    def __repr__(self):
        w = self.weather
        value = f"""weather for: {w['location_name']}
current temperature: {w['temp_f']:.0f} deg F feels like: {w['feels_like_f']:.0f} def F
low temperature: {w['temp_min_f']:.0f} def F high temperature: {w['weathertemp_max_f']:.0f} deg F
pressure: {w['pressure_hg']:.2f} inHg humidity: {w['humidity_pct']}%
wind: {w['wind_speed_mph']:.0f} mph at {w['wind_direction_deg']:.0f} deg
clouds: {w['cloud_cover_pct']}% sunrise: {w['sunrise_utc']} sunset: {w['sunset_utc']}"""
        return value


def write_screen(window, x, y, value, attribute):
    window.addstr(y, x, value, attribute)
    return len(value)


def curses_main(stdscr):
    stdscr.nodelay(True)
    stdscr.clear()
    curses.curs_set(False)
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    weather = Weather([33.681944, -117.973056])
    next_update = 0
    while True:
        now = datetime.datetime.now()
        height, width = stdscr.getmaxyx()

        # Print the time in the bottom left
        x = 0
        y = height - 1
        width = write_screen(stdscr, x, y, now.strftime('%Y-%m-%d %H:%M:%S'), curses.color_pair(1))
        x += width + 1

        # Print the hostname and IP address in the bottom left
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        width = write_screen(stdscr, x, y, hostname, curses.color_pair(2))
        x += width + 1
        width = write_screen(stdscr, x, y, ip_address, curses.color_pair(3))
        x += width + 1

        # Print the current weather
        time_to_next_call = max(0, next_update - (now - weather.last_call).total_seconds())
        width = write_screen(stdscr, x, y, f'{time_to_next_call:2.0f}', curses.color_pair(7))
        x += width + 1

        if not time_to_next_call > 0:
            next_update = 60
            weather.get_weather()
            x = 0
            y = 0
            color = 1
            for field in Weather.FIELDS:
                if y < height:
                    value = weather.weather[field]
                    width = write_screen(stdscr, x, y, f'{field:20}', curses.color_pair(6))
                    x += width + 1
                    width = write_screen(stdscr, x, y, f'{value:20}', curses.color_pair(color))
                    color += 1
                    if color > 7:
                        color = 1
                x = 0
                y = y + 1

        # Refresh the screen
        stdscr.refresh()

        # Wait for the user to press a key
        if stdscr.getch() != curses.ERR:
            break

        time.sleep(0.5)
    # reset the console
    stdscr.clear()
    curses.curs_set(True)


curses.wrapper(curses_main)
