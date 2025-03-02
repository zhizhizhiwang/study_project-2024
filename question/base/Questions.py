import json
import logging
import os
from functools import singledispatchmethod
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(message)s')
logger.setLevel(logging.DEBUG)


class Question(object):
    """
    储存一道题目的数据
    """
    surface: str | None
    solution: str | None
    analysis: str | None
    options: list[str]
    tags: list[str]
    difficulty: str
    question_id: int

    def __init__(self, surface: str = "", answer: str | None = None, analysis: str | None = None):
        super().__init__()
        """
        :param surface: 题面
        :param answer: 题目答案
        :param analysis: 题目解析
        """
        self.surface = surface
        self.answer = answer
        self.analysis = analysis

        self.options : list[str] = []
        self.tags : list[str] = []
        self.difficulty : str = "空"

        self.question_id : int = -1

    def unpack(self):
        return self.surface, self.options, self.answer, self.analysis, self.tags

    def load_from_file(self, file_name: str):
        with open(file_name, "r", encoding='utf8') as file:
            d = json.load(file)
            return self.load_from_json(d)

    def load_from_json(self, d : dir):
        try:
            self.surface, self.answer, self.analysis, self.question_id = ('\n\n'.join(d['question']), d['answer'], d['analysis'], int(d["problem_id"]))
        except KeyError as e:
            logger.error(f"加载题目文件失败 {e}", )
            raise e

        if "options" in d.keys():
            self.options = d["options"]
        if "tags" in d.keys():
            self.tags = d["tags"]
        if "difficulty" in d.keys():
            self.difficulty = d["difficulty"]

        return self


class QuestionsManager(object):

    def __init__(self):
        super().__init__()
        self.questions_dir : dict[int, tuple[bool, Question]] = {}
#                                  id : 答对情况
        """
        with open(r".\QuestionLib.json", "r+", encoding="utf-8") as file:
            self.questions_dir = json.load(file)
            self.filehash = hash(file)
        """

    def __getitem__(self, question_id : Question | int):
        if isinstance(question_id, int):
            if question_id in self.questions_dir.keys():
                return self.questions_dir[question_id][1]
            else:
                return Question()
        elif isinstance(question_id, Question):
            if question_id.question_id in self.questions_dir.keys():
                return self.questions_dir[question_id.question_id][0]
            else:
                return False

    def __setitem__(self, question_id : int, value : bool):
        self.questions_dir[question_id] = (value, self.questions_dir[question_id][1])

    def __contains__(self, question_id : int) -> bool:
        return question_id in self.questions_dir.keys()

    def load_lib(self, path : str):
        with open(path, "r", encoding="utf-8") as input:
            input_json = json.load(input)
            if type(input_json) is not list:
                logger.error(f"读取类型错误, type = {type(input_json)}, 应为list")
                try:
                    input_json = list(input_json)
                except Exception as e:
                    logger.error(f"转换失败 error:{e}")
                    raise TypeError

            for each_question in input_json:
                q = Question().load_from_json(each_question)
                self.questions_dir[int(q.question_id)] = (False, q)
        return self




example_question = Question().load_from_file(r"C:\Users\xpwan\Desktop\study_project-2024\question\example_question.json")
