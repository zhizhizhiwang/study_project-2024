from typing import Any
from typing import Callable


class Problems(object):
    """
    储存一道题目的数据
    """
    surface: str
    solution: str
    analysis: str
    other_information: Any
    handling: Callable

    def __init__(self, surface: str, solution: str, analysis: str, other_info: Any = None, handling: Callable = None):
        """
        :param surface: 题面
        :param solution: 题目答案
        :param analysis: 题目解析
        :param other_info : 其他信息，默认为None
        :param handling : 如何呈现提供的其他信息，为None则不显示
        """
        self.surface = surface
        self.solution = solution
        self.analysis = analysis
        self.other_information = other_info
        self.handling = handling
        return
