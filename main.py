# -*- coding: utf-8 -*-
# @Time    : 06/08/2023
# @Author  : nzooherd
# @File    : main.py 
# @Software: PyCharm
# -*- coding: utf-8 -*-

import logging
import configparser
import yaml

from typing import Tuple, List, Dict
from logging import config

from leetcode_cn import LeetcodeCN
from leetcode_us import LeetcodeUS

config_ini = configparser.ConfigParser()
config_ini.read('config.ini')


def format_cookies(cookies: str) -> Dict[str, str]:
    return {item[0]: item[1] for item in map(lambda cookie_str: cookie_str.replace(" ", "").split("="), cookies.split(";"))}


cn = LeetcodeCN(format_cookies(config_ini["cookie"]["CN_COOKIE"]))
us = LeetcodeUS(format_cookies(config_ini["cookie"]["US_COOKIE"]))


def init_log():
    LOGGING_CONFIG = f"""
    version: 1
    disable_existing_loggers: false
    formatters:
        simple:
            format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    handlers:
        console:
            class: logging.StreamHandler
            level: DEBUG
            formatter: simple
            stream: ext://sys.stdout
    root:
        level: DEBUG
        handlers: [console]
    exifread:
        level: INFO
    """
    config.dictConfig(yaml.safe_load(LOGGING_CONFIG))


def to_submit_questions() -> List[Tuple[int, str]]:
    """

    :return List: List[Tuple(question_frontend_id, question_slug)]
    """
    cn_passed = list(cn.fetch_pass_question())
    us_passed = {id for id in us.fetch_pass_question()}
    result = []
    for frontend_id, slug in cn_passed:
        if frontend_id in us_passed:
            continue
        result.append((frontend_id, slug))
    return result


def sync_submission(question_id: int, question_slug: str):
    """
    Sync one question's ac submission from leetcode-cn to leetcode-us
    :param int question_id:
    :param str question_slug:
    :return: None
    """
    submissions = cn.fetch_submissions(question_slug)
    for submission in submissions:
        if submission["status"] != "AC":
            continue
        detail = cn.fetch_submission_detail(submission["id"])
        code = detail["code"]
        if us.submit(detail["lang"], question_slug, question_id, code) == 200:
            logging.info(f"Sync question {question_slug} successfully")


if __name__ == '__main__':
    init_log()
    questions = to_submit_questions()
    for frontend_id, slug in questions:
        question_id = cn.fetch_question_detail(slug)
        sync_submission(question_id, slug)