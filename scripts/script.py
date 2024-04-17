import requests as req
import pandas as pd
import time
import os

def post(data):
    token = 'TOKEN'
    response = req.post('https://api.github.com/graphql', headers={'Authorization': f'Bearer {token}'}, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f'Request error: {response.status_code} \n {response.text}')

def fetch_repositories():
    repositories = []
    after = None
    while len(repositories) < 2:
        variables = {"after": after}
        data = post({'query': repo_query, 'variables': variables})
        if 'errors' in data:
            print("GraphQL query failed:", data['errors'])
            break
        if 'search' in data['data'] and 'edges' in data['data']['search']:
            for edge in data['data']['search']['edges']:
                node = edge['node']
                if 'pullRequests' in node and node['pullRequests']['totalCount'] >= 100:
                    repositories.append(node)
            if data['data']['search']['pageInfo']['hasNextPage']:
                after = data['data']['search']['pageInfo']['endCursor']
            else:
                break
            time.sleep(0.002)
    return repositories

def save_csv(data, filename):
    directory = '../lab03-software-experimentation'
    if not os.path.exists(directory):
        os.makedirs(directory)
    filepath = os.path.join(directory, filename)
    data.to_csv(filepath, index=False, sep=';')

def process_repositories(repositories):
    processed_data = pd.DataFrame()
    processed_data['Repository name'] = [repo.get('name') for repo in repositories]
    processed_data['Repository owner'] = [repo.get('owner', {}).get('login') for repo in repositories]
    processed_data['Stars'] = [repo.get('stargazers', {}).get('totalCount', 0) if isinstance(repo, dict) else 0 for repo in repositories]
    processed_data['Total Pull Requests'] = [repo.get('pullRequests', {}).get('totalCount',0) if isinstance(repo, dict) else 0 for repo in repositories]
    
    save_csv(processed_data, 'processed_data.csv')
    
    return processed_data

def process_pull_request(row):
    pull_requests_data = []
    name = row['Repository name']
    owner = row['Repository owner']

    variables = {"name": name, "owner": owner}
    try:
        data_pulls = post({'query': pullRequest_query, 'variables': variables})
        if 'errors' in data_pulls:
            print("GraphQL query failed:", data_pulls['errors'])
        for edge in data_pulls['data']['repository']['pullRequests']['edges']:
            values = edge['node']
            pull_requests_data.append({
                'Owner': owner,
                'Repository name': name,
                'Title': values['title'],
                'Pull Request Number': values['number'],
                'Pull Request Created At': values['createdAt'],
                'Pull Request Closed At': values['closedAt'],
                'Total files': values['files']['totalCount'],
                'Additions': values['additions'],
                'Deletions': values['deletions'],
                'Total reviews': values['reviews']['totalCount'],
                'Review decision': values['reviewDecision'],
                'Participants': values['participants']['totalCount'],
                'Comments': values['comments']['totalCount'],
                'Body Text': values['bodyText']
            })
    except Exception as ex:
        print(f"Exception occurred for repository '{name}' owned by '{owner}': {ex}")
        
    return pull_requests_data

def fetch_pull_requests(processed_data):
    pull_requests_data = processed_data.apply(process_pull_request, axis=1).sum()
    
    dataFrame_final = pd.DataFrame(pull_requests_data)
    
    save_csv(dataFrame_final, 'processed_data_pullRequests.csv')
    
    return dataFrame_final

# Queries
repo_query = '''
    query search($after: String) {
      search(query: "stars:>0", type: REPOSITORY, first: 1, after: $after) {
        pageInfo {
          endCursor
          hasNextPage
        }
        edges {
          node {
            ... on Repository {
              name
              owner {
                login
              }
              pullRequests(states: [MERGED, CLOSED], first: 100) {
                totalCount
              }
            }
          }
        }
      }
    }
'''

pullRequest_query = '''
    query getPullRequests($name: String!, $owner: String!) {
      repository(name: $name, owner: $owner) {
        pullRequests(states: [MERGED, CLOSED], first: 100) {
          edges {
            node {
              number
              title
              createdAt
              closedAt
              additions
              deletions
              bodyText
              files {
                totalCount
              }
              participants {
                totalCount
              }
              comments {
                totalCount
              }
              reviewDecision
              reviews(first: 1) {
                totalCount
                edges {
                  node {
                    createdAt
                    updatedAt
                    state
                  }
                }
              }
            }
          }
        }
      }
    }
'''

if __name__ == "__main__":
    repositories = fetch_repositories()
    processed_data = process_repositories(repositories)
    dataFrame_final = fetch_pull_requests(processed_data)
