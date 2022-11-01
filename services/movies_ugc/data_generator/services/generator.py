import random
import socket
import struct
import datetime
from uuid import uuid4
from typing import Optional

from user_agent import generate_user_agent


class Generator:

    current_movie_uuid = None
    current_user_uuid = None

    @staticmethod
    def get_uuid() -> str:
        return str(uuid4())

    @staticmethod
    def get_ip() -> str:
        return socket.inet_ntoa(
            struct.pack('>I', random.randint(1, 0xffffffff))
        )

    @staticmethod
    def get_event() -> [str, Optional[int]]:
        events = ['visited', 'looked', 'stopped']
        event = random.choice(events)
        frame = random.randint(1, 60) if event == 'stopped' else 0
        return event, frame

    def generate_login_history(self) -> dict:
        data = {
            "user_id": self.current_user_uuid,
            "user_ip": self.get_ip(),
            "user_agent": generate_user_agent(),
            "login_time": datetime.datetime.now().strftime(
                "%d-%m-%Y %H:%M:%S"
            )
        }

        return data

    def generate_user_event(self) -> dict:
        event, frame = self.get_event()
        data = {
            "movie_id": self.current_movie_uuid,
            "user_id": self.current_user_uuid,
            "event": event,
            "frame": frame,
            "event_time": datetime.datetime.now().strftime(
                "%d-%m-%Y %H:%M:%S"
            )
        }
        return data

    def get_data(self):
        self.current_user_uuid = self.get_uuid()
        self.current_movie_uuid = self.get_uuid()

        iterations = random.randint(1, 100)

        for _ in range(iterations):
            event = random.randint(0, 1)
            if event == 0:
                yield self.generate_login_history()
            else:
                yield self.generate_user_event()
