# -*- coding: utf-8 -*-
# @Time    : 06/08/2023
# @Author  : nzooherd
# @File    : fetch_pass_question.json.py
# @Software: PyCharm
# -*- coding: utf-8 -*-
import logging
import time
from typing import Iterator, Dict, Tuple, List

import requests


class LeetcodeCN:
    """

    """

    def __init__(self, cookies: dict):
        self.cookies = cookies
        self.headers = {
            'authority': 'leetcode.cn',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,zh-TW;q=0.6,ja;q=0.5,pt;q=0.4',
            'authorization': '',
            'baggage': 'sentry-environment=production,sentry-release=HLuEVHf5aIr77cY5nWF0g,sentry-transaction=%2Fproblems%2F%5Bslug%5D%2F%5B%5B...tab%5D%5D,sentry-public_key=767ac77cf33a41e7832c778204c98c38,sentry-trace_id=664c004f98d441f09815fd033f27cae0,sentry-sample_rate=0.03',
            'content-type': 'application/json',
            'dnt': '1',
            'referer': 'https://leetcode.cn/problems/shortest-subarray-with-sum-at-least-k/description/',
            'origin': 'https://leetcode.cn',
            'random-uuid': '8a4162a1-e2b5-0a2d-ba11-ee780b3b7d14',
            'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sentry-trace': '664c004f98d441f09815fd033f27cae0-94197b74b4c85ef5-0',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'uuuserid': 'bbd8a9a29870be03a20d789cde5cbb83',
            'x-csrftoken': 'HaCABJch2KuULfYHtvR9YPqrMqsr7YFw2Bwx7m2Gv1dC6aITY1AKwHIThHpHqhuV',
        }


    def graphql_request(self, payload: Dict):
        return requests.post('https://leetcode.cn/graphql/',
                             cookies=self.cookies,
                             headers=self.headers,
                             json=payload)

    def fetch_question_detail(self, question_slug) -> int:
        """
        Fetch question's detail information
        :param question_slug:
        :type question_slug: str
        :return: questionId
        :rtype: int
        """
        payload = {
            'query': '\n    query questionTitle($titleSlug: String!) {\n  question(titleSlug: $titleSlug) {\n    questionId\n    questionFrontendId\n    title\n    titleSlug\n    isPaidOnly\n    difficulty\n    likes\n    dislikes\n  }\n}\n    ',
            'variables': {
                'titleSlug': f'{question_slug}',
            },
            'operationName': 'questionTitle',
        }
        response = self.graphql_request(payload)
        data = response.json()
        return data["data"]["question"]["questionId"]

    def fetch_submissions(self, question_slug: str) -> List[Dict[str, str]]:
        """

        :param question_slug:
        :type question_slug: str
        :return: submissions
        :rtype: [{"id": str, "title": str, "status": str, "lang": str}]
        """
        payload = {
            'query': '\n    query submissionList($offset: Int!, $limit: Int!, $lastKey: String, $questionSlug: '
                     'String!, $lang: String, $status: SubmissionStatusEnum) {\n  submissionList(\n    offset: '
                     '$offset\n    limit: $limit\n    lastKey: $lastKey\n    questionSlug: $questionSlug\n    lang: '
                     '$lang\n    status: $status\n  ) {\n    lastKey\n    hasNext\n    submissions {\n      id\n      '
                     'title\n      status\n      statusDisplay\n      lang\n      langName: langVerboseName\n      '
                     'runtime\n      timestamp\n      url\n      isPending\n      memory\n      submissionComment {\n '
                     '       comment\n        flagType\n      }\n    }\n  }\n}\n    ',
            'variables': {
                'questionSlug': question_slug,
                'offset': 0,
                'limit': 20,
                'lastKey': None,
                'status': None,
            },
            'operationName': 'submissionList',
        }
        response = self.graphql_request(payload)
        data = response.json()
        submissions = data["data"]["submissionList"]["submissions"]
        result = []
        for submission in submissions:
            result.append({"id": submission["id"],
                           "title": submission["title"],
                           "status": submission["status"],
                           "lang": submission["lang"]})
        return result

    def fetch_submission_detail(self, submission_id: str):
        """
        fetch submission detail
        :param submission_id:
        :type submission_id: str
        :return:
        :rtype:
        """
        payload = {
            'query': '\n    query submissionDetails($submissionId: ID!) {\n  submissionDetail(submissionId: '
                     '$submissionId) {\n    code\n    timestamp\n    statusDisplay\n    isMine\n    runtimeDisplay: '
                     'runtime\n    memoryDisplay: memory\n    memory: rawMemory\n    lang\n    langVerboseName\n    '
                     'question {\n      questionId\n    }\n    user {\n      realName\n      userAvatar\n      '
                     'userSlug\n    }\n    runtimePercentile\n    memoryPercentile\n    submissionComment {\n      '
                     'flagType\n    }\n    ... on GeneralSubmissionNode {\n      outputDetail {\n        codeOutput\n '
                     '       expectedOutput\n        input\n        compileError\n        runtimeError\n        '
                     'lastTestcase\n      }\n    }\n  }\n}\n    ',
            'variables': {
                'submissionId': f'{submission_id}',
            },
            'operationName': 'submissionDetails',
        }
        response = self.graphql_request(payload)
        return response.json()["data"]["submissionDetail"]

    def fetch_pass_question(self) -> Iterator[Tuple[int, str]]:
        """

        :return: questionFrontendId
        :rtype: int
        """
        skip, num = 0, 50
        payload = {
            'operationName': 'userProfileQuestions',
            'variables': {
                'status': 'ACCEPTED',
                'sortField': 'LAST_SUBMITTED_AT',
                'sortOrder': 'DESCENDING',
                'difficulty': [],
            },
            'query': 'query userProfileQuestions($status: StatusFilterEnum!, $skip: Int!, $first: Int!, $sortField: SortFieldEnum!, $sortOrder: SortingOrderEnum!, $keyword: String, $difficulty: [DifficultyEnum!]) {\n  userProfileQuestions(status: $status, skip: $skip, first: $first, sortField: $sortField, sortOrder: $sortOrder, keyword: $keyword, difficulty: $difficulty) {\n    totalNum\n    questions {\n      translatedTitle\n      frontendId\n      titleSlug\n      title\n      difficulty\n      lastSubmittedAt\n      numSubmitted\n      lastSubmissionSrc {\n        sourceType\n        ... on SubmissionSrcLeetbookNode {\n          slug\n          title\n          pageId\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n',
        }
        while True:
            payload["variables"].update({"skip": str(skip), "first": str(num)})
            response = self.graphql_request(payload)
            data = response.json()
            questions = data["data"]["userProfileQuestions"]["questions"]
            logging.info(f"Request cn pass questions page:{skip // num + 1} successfully.")
            for question in questions:
                yield question["frontendId"], question["titleSlug"]

            if len(questions) < num:
                break
            skip += num
            time.sleep(5)  # rate limit

