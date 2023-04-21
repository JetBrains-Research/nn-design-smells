import pandas as pd
import datetime
from github import Github
import os
import requests
from requests.adapters import HTTPAdapter

from urllib3 import Retry
import json

df = pd.read_csv('csv/git_repos_20-23.csv')
df = df.sort_values(['stargazers'], ascending=False)

topics = ['maching-learning', 'deep-learning', 'natural-language-processing', 
          'nlp', 'cnn', 'rnn', 'gnn', 'transformer', 'attention', 'generative-adversarial-network',
          'pytorch', 'tensorflow', 'keras', 'pytorch-lightning', 'neural-network']

contents = ['import torch', 'import keras', 'import tensorflow']

descriptions = ['torch', 'keras', 'tensorflow']

# retries to avoid github api rate limit (403 status code)
def create_github_session() -> requests.Session:
    s = requests.Session()
    retries = Retry(total=50, backoff_factor=10, status_forcelist=[403])
    s.mount('https://', HTTPAdapter(max_retries=retries))
    return s


class GetRepositories():
    def __init__(self, topics, contents, descriptions, f_repos="", f_issues=""):
        self.topics = topics
        self.contents = contents
        self.descriptions = descriptions

        self.f_repos = f_repos
        self.f_issues = f_issues

    def check_repo(self, access_token, session, name):
        try:
            url = 'https://api.github.com/'
            print(f'Query {name}...', end=' ')
            
            header = {'Authorization': f'Bearer {access_token}'}
            retries = Retry(total=50, backoff_factor=10, status_forcelist=[403])
            g = Github(access_token, retry=retries)
            
            repo = g.get_repo(name)

            repo_info = {'name': name,
                         'full_name': repo.full_name,
                         'topics': repo.get_topics(),
                         'description': repo.description}

            json.dump(repo_info, self.f_repos)
            self.f_repos.write('\n')
            
            print('Success!')
            return repo_info
            # if self.check_topics(repo_info['topics']):
            #     print(f'Success!\nFound required topics in: {repo_info["topics"]}!\n')
            #     issues_list = self.check_issues(repo, name)

            #     json.dump(repo_info, self.f_repos)
            #     self.f_repos.write('\n')

            #     return repo_info, issues_list
            
            # if self.check_description(repo_info['description']):
            #     print(f'Success!\nFound required description in: <{repo_info["description"]}>!\n')
            #     issues_list = self.check_issues(repo, name)

            #     json.dump(repo_info, self.f_repos)
            #     self.f_repos.write('\n')

            #     return repo_info, issues_list
            
            # print('Failed!')
            # return None
        except Exception as e:
            print('Failed!')
            print(f'In check_repo : {e}')
            return None
                
    def check_topics(self, repo_topics):
        for topic in self.topics:
            if topic in repo_topics:
                return True
        return False
        
    def check_description(self, repo_description):
        if repo_description is None:
            return False
        
        for desc in self.descriptions:
            if desc in repo_description:
                return True
        return False
    
    def check_issues(self, repo, name):
        try:
            issues = repo.get_issues()
            issues_list = []
            for issue in issues:
                if (issue.comments == 0 and issue.pull_request is None):
                    continue

                issue_url = issue.url
                url = 'https://github.com/' + issue_url[issue_url.find('repos/') + 6:]
                number = issue.number
                title = issue.title
                body = issue.body
                labels = issue.labels

                issue_info = {'repo': name,
                            'url': url,
                            'number': number,
                            'title': title,
                            'body': body,
                            'labels': [label.name for label in labels]}

                json.dump(issue_info, self.f_issues)
                self.f_issues.write('\n')

                issues_list.append(issue_info)
                
            print(f'Success! Found {len(issues_list)} issues!')
            return issues_list

        except Exception as e:
            print('Failed!')
            print(f'In check_issues : {e}')
            return None


access_token = "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"
session = create_github_session()
names = df.name.to_list()

with open('json/ml_repos_sorted_all.jsonl', 'a') as f_repos:
    get_ml_repos = GetRepositories(topics, contents, descriptions, f_repos)
    
    for i, name in enumerate(names):
        print(i, end=' ')
        result = get_ml_repos.check_repo(access_token, session, name)