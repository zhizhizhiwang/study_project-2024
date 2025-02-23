import json
import logging
from functools import singledispatch
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
                raise e
            except Exception as e:
                logger.error("error in load from file", e)
                raise e
        return self


class QuestionsManager(object):

    def __init__(self):
        super().__init__()
        self.questions_dir : dict[int, bool] = {}
#                                  id : 答对情况
        with open(r".\QuestionLib.json", "r+", encoding="utf-8") as file:
            self.questions_dir = json.load(file)
            self.filehash = hash(file)

    def __getitem__(self, question_id : int) -> bool:
        if question_id in self.questions_dir.keys():
            return self.questions_dir[question_id]
        else:
            logger.info("不存在的题目已注册")
            self.questions_dir[question_id] = False
            return False

    def __setitem__(self, question_id : int, value : bool):
        self.questions_dir[question_id] = value

    def __contains__(self, question_id : int) -> bool:
        return question_id in self.questions_dir.keys()




example_question = Question().load_from_file(r"C:\Users\xpwan\Desktop\study_project-2024\question\example_question.json")
