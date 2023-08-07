# -*- coding: utf-8 -*-
# @Time    : 06/08/2023
# @Author  : nzooherd
# @File    : leetcode_us.py 
# @Software: PyCharm
# -*- coding: utf-8 -*-
import logging
import time
from typing import Dict, Iterator

import requests


class LeetcodeUS:

    def __init__(self, cookies: dict):
        self.cookies = cookies

        self.headers = {
            'authority': 'leetcode.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,zh-TW;q=0.6,ja;q=0.5,pt;q=0.4',
            'content-type': 'application/json',
            'dnt': '1',
            'origin': 'https://leetcode.com',
            'referer': 'https://leetcode.com/problems/letter-combinations-of-a-phone-number/description/',
            'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'x-csrftoken': 'nfRrH14MaQ84eiJPh93zTIDQsiJPgOUBfLWPGXYFhZTxbVqosfQP15YG0pkp9ij8',
        }

    def graphql_request(self, payload: Dict):
        return requests.post('https://leetcode.com/graphql/',
                             cookies=self.cookies,
                             headers=self.headers,
                             json=payload)

    def submit(self, lang: str, question_slug: str, question_id: int, typed_code: str):
        """
        Submit code
        :param lang:
        :type lang:
        :param question_slug:
        :type question_slug: str
        :param question_id:
        :type question_id:
        :param typed_code:
        :type typed_code:
        :return:
        :rtype:
        """
        payload = {
            'lang': lang,
            'question_id': str(question_id),
            'typed_code': typed_code,
        }

        response = requests.post(
            f'https://leetcode.com/problems/{question_slug}/submit/',
            cookies=self.cookies,
            headers=self.headers,
            json=payload,
        )
        logging.debug(f"Submit code to {question_slug}, Get: {response.status_code}")
        time.sleep(10)
        return response.status_code

    def fetch_pass_question(self) -> Iterator[int]:
        """

        :return: questionFrontendId
        :rtype: int
        """
        pageNo, numPerPage = 1, 50
        payload = {
            'query': '\n query progressList($pageNo: Int, $numPerPage: Int, $filters: ProgressListFilterInput) {\n '
                     'isProgressCalculated\n solvedQuestionsInfo(pageNo: $pageNo, numPerPage: $numPerPage, '
                     'filters: $filters) {\n currentPage\n pageNum\n totalNum\n data {\n totalSolves\n question {\n '
                     'questionFrontendId\n questionTitle\n questionDetailUrl\n difficulty\n topicTags {\n name\n '
                     'slug\n }\n }\n lastAcSession {\n time\n wrongAttempts\n }\n }\n }\n}\n ',
            'variables': {'pageNo': pageNo, 'numPerPage': numPerPage, 'filters': {}, }, 'operationName': 'progressList',
        }

        while True:
            payload["variables"].update({"pageNo": pageNo, "numPerPage": numPerPage})
            response = self.graphql_request(payload)
            data = response.json()
            questions = data["data"]["solvedQuestionsInfo"]["data"]
            logging.info(f"Request us pass questions page:{pageNo} successfully.")
            for question in questions:
                yield question["question"]["questionFrontendId"]

            if len(questions) < numPerPage:
                break
            pageNo += 1
            time.sleep(5) # rate limit





