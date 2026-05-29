from abc import abstractmethod

from insight_engine.util import time


class QueryFilter:
    def __init__(self):
        pass

    @abstractmethod
    def accepts(self, value) -> bool:
        pass

    @abstractmethod
    def to_sql_clause(self, key, next_param_num: int) -> (str, int):
        pass


class NotFilter(QueryFilter):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def accepts(self, value) -> bool:
        return value != self.value

    def to_sql_clause(self, key, next_param_num: int) -> (str, int):
        return f'{key} <> ${next_param_num}', 1


class NotYetValidFilter(QueryFilter):
    def __init__(self):
        super().__init__()

    def accepts(self, value) -> bool:
        return value and time.current_datetime() < value

    def to_sql_clause(self, key, next_param_num: int) -> (str, int):
        return f'COALESCE(NOW < {key}, FALSE)', 0


class AlreadyValidFilter(QueryFilter):
    def __init__(self):
        super().__init__()

    def accepts(self, value) -> bool:
        return not value or value <= time.current_datetime()

    def to_sql_clause(self, key, next_param_num: int) -> (str, int):
        return f'COALESCE({key} <= NOW(), TRUE)', 0


class StillValidFilter(QueryFilter):
    def __init__(self):
        super().__init__()

    def accepts(self, value) -> bool:
        return not value or time.current_datetime() < value

    def to_sql_clause(self, key, next_param_num: int) -> (str, int):
        return f'COALESCE(NOW() < {key}, TRUE)', 0


class NoLongerValidFilter(QueryFilter):
    def __init__(self):
        super().__init__()

    def accepts(self, value) -> bool:
        return value and value <= time.current_datetime()

    def to_sql_clause(self, key, next_param_num: int) -> (str, int):
        return f'COALESCE({key} <= NOW(), FALSE)', 0
