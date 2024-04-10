import csv
import requests
from datetime import datetime
import subprocess
import os

def calculate_age(created_at):
    created_at_date = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
    current_date = datetime.now()
    age = current_date - created_at_date
    return age.days

def get_repository_info(repository):
    repo_node = repository['node']
    name = repo_node['name']
    owner = repo_node['owner']['login']

    return {
        'Repository name': name,
        'Repository owner': owner,
    }

def download_repository(repo_url):
    os.system(f"git clone {repo_url}")

def delete_repository(directory):
    os.system(f'rmdir /s /q {directory}')

def main():
    token = 'TOKEN'
    headers = {'Authorization': f'Bearer {token}'}
    endpoint = 'https://api.github.com/graphql'
    query = '''
    query ($after: String) {
  search(query: "stars:>1", type: REPOSITORY, first: 1, after: $after) {
    pageInfo {
      endCursor
      hasNextPage
    }
    edges {
      node {
        ... on Repository {
          name
          createdAt
          updatedAt
          owner {
            login
          }
          releases {
            totalCount
          }
          stargazers {
            totalCount
          }
          pullRequests(first: 100, states: [MERGED, CLOSED], after: null) {
            totalCount
            edges {
              node {
                additions
                deletions
                files {
                  totalCount
                }
                createdAt
                closedAt
                mergedAt
                bodyText
                reviews(first: 1) {
                  totalCount
                  nodes {
                    createdAt
                    state
                  }
                }
                participants {
                  totalCount
                }
                comments {
                  totalCount
                }
              }
            }
          }
        }
      }
    }
  }
}     
'''

    repositories_info = []
    end_cursor = ""
    variables = {}
    repoCont = 0

    while len(repositories_info) < 200:
        if end_cursor == "":
            query_starter = query.replace(', after: $after', "")
            query_starter = query_starter.replace('($after: String)', "")
            response = requests.post(endpoint, json={'query': query_starter}, headers=headers)
        else:
            variables['after'] = end_cursor
            response = requests.post(endpoint, json={'query': query, 'variables': variables}, headers=headers)

        data = response.json()

        for repository in data['data']['search']['edges']:           
            repository_info = get_repository_info(repository)
            repositories_info.append(repository_info) 

            # Download repository
            repo_url = f"https://github.com/{repository_info['Repository owner']}/{repository_info['Repository name']}.git"
            download_repository(repo_url)

            # Delete repository
            delete_repository(f"{repository_info['Repository name']}")

        if data['data']['search']['pageInfo']['hasNextPage']:
            end_cursor = data['data']['search']['pageInfo']['endCursor']

        repoCont += 20

    # Create csv: 1000 repository list
    # with open('repositories_info_graphql.csv', 'w', newline='') as fp:
    #     fieldnames = repositories_info[0].keys()
    #     writer = csv.DictWriter(fp, fieldnames=fieldnames)
        
    #     writer.writeheader()
    #     for info in repositories_info:
    #         writer.writerow(info)
        
if __name__ == "__main__":
    main()
