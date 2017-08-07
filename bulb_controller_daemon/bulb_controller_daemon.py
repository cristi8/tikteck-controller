#!/usr/bin/env python

import tikteck2
import os
import sys
import random
import time
import logging
import watchdog.observers
from watchdog.events import FileSystemEventHandler

try:
    # watchdog module has a hardcoded delay of 0.5 sec for all events. It's too much for this application, so we patch that out.
    # The delay reason, as explained in observers/inotify_buffer.py, is to pair IN_MOVED_FROM and IN_MOVED_TO events.
    watchdog.observers.inotify_buffer.InotifyBuffer.delay = 0
except:
    pass

logger = logging.getLogger(__name__)

CONFIG_FILE = '/etc/lightbulbs.config'
COLOR_FILE = '/dev/shm/lightbulbs_color'


class FileMonitor(object):
    class MyEventHandler(FileSystemEventHandler):
        def __init__(self, file_path, callback):
            super(FileMonitor.MyEventHandler, self).__init__()
            self.my_callback = callback
            self.my_file_path = file_path

        def on_modified(self, evt):
            if os.path.realpath(evt.src_path) != self.my_file_path:
                return
            try:
                self.my_callback()
            except:
                pass

    def __init__(self, file_path, new_content_callback):
        self.file_path = os.path.realpath(file_path)
        self.event_handler = FileMonitor.MyEventHandler(self.file_path, new_content_callback)
        self.observer = watchdog.observers.Observer()
        self.observer.schedule(self.event_handler, os.path.dirname(self.file_path), recursive=False)

    def start(self):
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()


class BulbController(object):
    def __init__(self, bulb_defs, color_file_path):
        self.color_file_path = color_file_path
        self.monitor = FileMonitor(color_file_path, self.refresh_from_file)
        self.bulbs = [tikteck2.tikteck(x['mac'], x['name'], x['pwd']) for x in bulb_defs]
        for bulb in self.bulbs:
            logger.info('Connecting to %s...', bulb.mac)
            bulb.connect()
            logger.info('Connected')

        try:
            self.refresh_from_file()
        except:
            pass

    def start_monitoring(self):
        self.monitor.start()

    def refresh_from_file(self):
        with open(self.color_file_path, 'r') as f:
            values = [int(x) for x in f.read().strip().split(' ')]
        r, g, b, bright = values
        self.set_color(r, g, b, bright)

    def set_color(self, r, g, b, bright):
        for bulb in self.bulbs:
            logger.info("Setting %s to %s, %s, %s, %s...", bulb.mac, r, g, b, bright)
            bulb.set_state(r, g, b, bright)
            logger.info("Done")


def main():
    logging.basicConfig(level=logging.INFO)
    bulbs = []
    with open(CONFIG_FILE) as f:
        bulb_count = int(f.readline().strip())
        for i in range(bulb_count):
            mac = f.readline().strip()
            name = f.readline().strip()
            pwd = f.readline().strip()
        bulbs.append({'mac': mac, 'name': name, 'pwd': pwd})

    controller = BulbController(bulbs, COLOR_FILE)
    controller.start_monitoring()


if __name__ == '__main__':
    main()
