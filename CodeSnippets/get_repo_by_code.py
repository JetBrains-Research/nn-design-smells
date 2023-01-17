from io import BytesIO
import pycurl
import json
import csv
import itertools
import sys
import time
import os
from github import Github

import requests

access_token = []
access_token_counter = 0

def check_language(file_name):
    file_name = file_name.lower()
    filename, file_extension = os.path.splitext(file_name)
    # if file_extension in [".py", ".ipynb"]:
    if file_extension in [".py"]:
        return True
    else:
        return False


def get_repos(start_size, end_size):
    global access_token_counter
    result = []
    page_couter = 1

    while True:
        # url = f"https://api.github.com/search/code?q=import%2Btensorflow+size:{start_size}..{end_size}+in:file+language:python+language:jupyter-notebook&page={page_couter}&per_page=100"
        url = f"https://api.github.com/search/code?q=import%2Btorch+size:{start_size}..{end_size}+in:file+language:python&page={page_couter}&per_page=100"
        # pushed:2021-01-01T00:00:00Z..2022-01-01T00:00:00Z
        # url = f"https://api.github.com/search/code?q=import%2Bkeras+size:{start_size}..{end_size}+in:file&page={page_couter}&per_page=100"
        output = BytesIO()
        request = pycurl.Curl()
        request.setopt(pycurl.HTTPHEADER, [f'Authorization: token {access_token[access_token_counter%8]}'])
        request.setopt(request.URL, url)
        request.setopt(request.WRITEDATA, output)
        request.perform()

        get_body = output.getvalue().decode()
        body = json.loads(get_body)

        access_token_counter += 1


        if not body:
            break

        if "items" not in body:
            # print("GitHub is dead...")
            break

        if len(body["items"]) == 0:
            break

        codes = body['items']
        for code in codes:
            file_name = code["name"]
            if not check_language(file_name):
                continue

            repo = code["repository"]
            if repo["private"] == True or repo["fork"] == True:
                continue
            result.append([repo["id"],repo["full_name"], repo["url"]])

        page_couter += 1
        time.sleep(2)

    result.sort()
    result = list(result for result,_ in itertools.groupby(result))

    return result

def main():

    all_repos = []

    # Extracting repositories
    size_counter = 50000
    adition = 10
    # while size_counter < 500000:
    while size_counter < 500000:
        if size_counter >= 50000 and size_counter < 100000:
            adition = 500
        elif size_counter >= 100000 and size_counter < 200000:
            adition = 1000
        elif size_counter >= 200000 and size_counter < 250000:
            adition = 2000
        elif size_counter >= 250000 and size_counter < 300000:
            adition = 3000
        elif size_counter >= 300000:
            adition = 5000

        start_size = size_counter + 1
        end_size = start_size + adition - 1
        size_counter = end_size
        print(f"repos with size from {start_size} to {end_size} are extracting....")
        repos = get_repos(start_size, end_size)
        # get_repo_pyGitHub(start_size, end_size)
        # get_repos_by_request(start_size, end_size)
        all_repos = all_repos + repos

    # Removing repeated repos
    # unique_repos = list(dict.fromkeys(all_repos))
    all_repos.sort()
    unique_repos = list(all_repos for all_repos, _ in itertools.groupby(all_repos))

    # Writing results in csv file
    output_file = open(file="data/pytorch/repos_pytorch_code_03.csv", mode="w", encoding="utf-8")
    writer = csv.writer(output_file)

    # Writing header row of the csv file
    writer.writerow(["id", "full_name", "url"])

    for item in unique_repos:
        writer.writerow(item)

    output_file.close()
    print("everything is done....!!!")

if __name__ == '__main__':
    main()