from <%my_service%>.util import time, text


class Mocking:

    def __init__(self):
        self.current_uuid_index = 0
        self.current_alphanum_index = 0
        # Any (specific) time will do, this is September 13, 2020
        self.current_timestamp = 1600000000
        time._current_datetime = self._fixed_time
        text._select_random = self._select_next
        text._random_uuid = self._incrementing_uuid

    def increment_time(self, minutes):
        self.current_timestamp += minutes * 60 * 1000

    def _incrementing_uuid(self):
        self.current_uuid_index += 1
        padded_index = str(self.current_uuid_index).zfill(12)
        return f'00000000-0000-0000-0000-{padded_index}'

    def _select_next(self, seq):
        choice = seq[self.current_alphanum_index % len(seq)]
        self.current_alphanum_index += 1
        return choice

    def _fixed_time(self):
        return time.from_epoch_seconds(self.current_timestamp)
