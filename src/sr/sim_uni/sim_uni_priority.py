from enum import Enum
from typing import List, TypedDict


class SimUniBlessPriorityType(Enum):

    PATH: str = '命途'
    BLESS: str = '祝福'


class SimUniBlessPriority:

    def __init__(self, first_id_list: List[str], second_id_list: List[str]):
        self.first_id_list: List[str] = first_id_list
        self.second_id_list: List[str] = second_id_list


class SimUniNextLevelPriority:

    def __init__(self, id_list: List[str]):
        self.id_list: List[str] = id_list


class SimUniCurioPriority:

    def __init__(self, id_list: List[str]):
        self.id_list: List[str] = id_list