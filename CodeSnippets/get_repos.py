from io import BytesIO
import pycurl
import json
import csv

access_token = []
access_token_counter = 0

def get_repos(start_date, end_date):
    global access_token_counter
    result = []
    page_couter = 1

    while True:

        url = f"https://api.github.com/search/repositories?q=keras+pushed:{start_date}T00:00:00Z..{end_date}T00:00:00Z&order=asc&per_page=100&page={page_couter}" #&access_token=509a21db33ebb67c140890cbd1e5a30ad92d3f79"
        output = BytesIO()
        request = pycurl.Curl()
        request.setopt(pycurl.HTTPHEADER, [f'Authorization: token {access_token[access_token_counter%3]}'])
        request.setopt(request.URL, url)
        request.setopt(request.WRITEDATA, output)
        request.perform()

        access_token_counter += 1

        get_body = output.getvalue().decode()
        body = json.loads(get_body)
        # print(body)

        if not body:
            break

        total_results = body['total_count']
        page_number = int(total_results / 100) + 1

        repos = body['items']

        # if len(repos) == 0:
        #     break

        for repo in repos:
            if repo['fork'] == True or repo['disabled'] == True or (repo['language'] not in ["Jupyter Notebook","Python"]):
                continue
            result.append([repo['id'], repo['full_name'], repo['html_url'], repo['size'], repo['stargazers_count'], repo['watchers_count'], repo['forks_count'], repo['score']])

        if page_couter == page_number:
            break

        page_couter += 1


    return result


def main():

    output_file = open(file="data/keras/repos_keras_pushed(03-12-2021)-1Y_02.csv", mode="w", encoding="utf-8")
    writer = csv.writer(output_file)

    #write header row of the csv file
    writer.writerow(["id", "full_name", "url", "size", "stargazers_count" , "watchers_count", "fork_count", "score"])

    # search based on the date - Start
    start_date = ""
    end_date = ""


    days = ["01", "05", "10", "15", "20", "25"]
    months = ["01", "02", "03","04","05","06","07","08","09","10","11","12"]
    years = [str(x) for x in range(2020,2022)]

    day_counter = 0
    month_counter = 0
    year_counter = 1

    while True:
        start_date = f"{years[year_counter]}-{months[month_counter]}-{days[day_counter]}"

        day_counter += 1
        # if day_counter == 6:
        if day_counter == 16:
            day_counter = 0
            month_counter +=1
        if month_counter == 12:
            month_counter = 0
            year_counter += 1

        end_date = f"{years[year_counter]}-{months[month_counter]}-{days[day_counter]}"

        repos = get_repos(start_date, end_date)
        for repo in repos:
            writer.writerow(repo)

        print(f"repos from {start_date} to {end_date} is written into file...")
        
        if start_date == "2021-12-01":
            print("everything is done")
            break

if __name__ == '__main__':
    main()