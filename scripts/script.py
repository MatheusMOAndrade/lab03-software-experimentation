import csv
import requests
from datetime import datetime
import os

def calculate_age(created_at, closed_at, merged_at):
    if merged_at:
        end_time = datetime.strptime(merged_at, "%Y-%m-%dT%H:%M:%SZ")
    else:
        end_time = datetime.strptime(closed_at, "%Y-%m-%dT%H:%M:%SZ")

    start_time = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
    age = end_time - start_time
    return age.total_seconds() / 3600  # Convertendo para horas

def get_repository_info(repository):
    repo_node = repository['node']
    name = repo_node['name']
    owner = repo_node['owner']['login']

    pull_requests = repo_node['pullRequests']['edges']

    pr_metrics = []
    for pr in pull_requests:
        pr_node = pr['node']
        metrics = {
            'Files count': pr_node['files']['totalCount'],
            'Additions': pr_node['additions'],
            'Deletions': pr_node['deletions'],
            'Description length': len(pr_node['bodyText']),
            'Interactions': pr_node['participants']['totalCount'],
            'Comments': pr_node['comments']['totalCount']
        }
        analysis_time = calculate_age(pr_node['createdAt'], pr_node['closedAt'], pr_node['mergedAt'])
        metrics['Analysis time (hours)'] = analysis_time
        pr_metrics.append(metrics)

    return {
        'Repository name': name,
        'Repository owner': owner,
        'Pull Request metrics': pr_metrics
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

    # Create csv: 200 pull request list
    with open('repositories_info_graphql.csv', 'w', newline='') as fp:
        fieldnames = ['Repository name', 'Repository owner', 'Pull Request metrics']
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        
        writer.writeheader()
        for info in repositories_info:
            writer.writerow(info)
        
if __name__ == "__main__":
    main()
