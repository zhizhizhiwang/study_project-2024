import json
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(message)s')
logger.setLevel(logging.DEBUG)


class Problem(object):
    """
    储存一道题目的数据
    """
    surface: str | None
    solution: str | None
    analysis: str | None

    def __init__(self, surface: str = "", answer: str | None = None, analysis: str | None = None):
        """
        :param surface: 题面
        :param answer: 题目答案
        :param analysis: 题目解析
        """
        self.surface = surface
        self.answer = answer
        self.analysis = analysis
        return

    def unpack(self):
        return self.surface, self.answer, self.analysis

    def load_from_file(self, file_name: str):
        with open(file_name, "r", encoding='utf8') as file:
            d = json.load(file)
            try:
                self.surface, self.answer, self.analysis = ('\n\n'.join(d['surface']), d['answer'], d['analysis'])
            except KeyError as e:
                logger.error("加载题目文件失败", e)
                return None
        return self


example_question = Problem().load_from_file(r"C:\Users\xpwan\Desktop\study_project-2024\question\example_question.json")
