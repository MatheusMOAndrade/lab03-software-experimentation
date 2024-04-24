import requests as req
import pandas as pd
import time
import os

tokens = ['TOKEN1', 'TOKEN2', 'TOKEN3', 'TOKEN4']
current_token_index = 0

def get_current_token():
    global current_token_index
    return tokens[current_token_index]

def switch_token():
    global current_token_index
    current_token_index = (current_token_index + 1) % len(tokens)

def post(data):
    token = get_current_token()
    response = req.post('https://api.github.com/graphql', headers={'Authorization': f'Bearer {token}'}, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f'Request error: {response.status_code} \n {response.text}')

def fetch_repositories():
    repositories = []
    per_page = 1
    after = None
    query_string = "stars:>0"
    calls_counter = 0
    
    while len(repositories) < 200:
      variables = {
          "queryString": query_string,
          "first": per_page,
          "after": after
      }
      
      data = post({'query': repo_query, 'variables': variables})
      
      calls_counter += 1
      if calls_counter > 20:
          switch_token()
          calls_counter = 0
      
      if 'errors' in data:
          print("GraphQL query failed:", data['errors'])
          print("Waiting for 60 seconds before retrying...")
          time.sleep(60)
          continue

      print(f"Received {len(data['data']['search']['edges'])} repositories in this batch.")

      for edge in data['data']['search']['edges']:
          node = edge['node']
          pull_requests_count = node['pullRequests']['totalCount']
          if pull_requests_count >= 100:
              repositories.append(node)
      
      if data['data']['search']['pageInfo']['hasNextPage']:
        after = data['data']['search']['pageInfo']['endCursor']
        print("Fetching next page...")
      else:
        print("No more pages.")
        break
      
      time.sleep(1)

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
    processed_data['Total Pull Requests'] = [repo['pullRequests']['totalCount'] for repo in repositories]
    
    save_csv(processed_data, 'processed_data.csv')
    print('The repository list has been created')

    return processed_data

def process_pull_request(row):
    pull_requests_data = []
    name = row['Repository name']
    owner = row['Repository owner']
    variables = {"name": name, "owner": owner}
    attempts = 0

    while attempts < 5:
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
                    'Created At': values['createdAt'],
                    'Merged At': values['mergedAt'],
                    'Closed At': values['closedAt'],
                    'Total files': values['files']['totalCount'],
                    'Additions': values['additions'],
                    'Deletions': values['deletions'],
                    'Total reviews': values['reviews']['totalCount'],
                    'Review decision': values['reviewDecision'],
                    'Participants': values['participants']['totalCount'],
                    'Comments': values['comments']['totalCount'],
                    'Body Text': values['bodyText']
                })

                switch_token()
                time.sleep(1)

            break
        
        except Exception as ex:
            attempts += 1
            print(f"Exception occurred for repository '{name}' owned by '{owner}': {ex}")
            print(f"Waiting 60 seconds before retrying...")
            time.sleep(60)

    return pull_requests_data

def fetch_pull_requests(processed_data):
    pull_requests_data = []

    for _, row in processed_data.iterrows():
        pull_requests_data.extend(process_pull_request(row))
        time.sleep(1)
        
    dataFrame_final = pd.DataFrame(pull_requests_data)
    
    save_csv(dataFrame_final, 'processed_data_pullRequests.csv')
    
    return dataFrame_final

# Queries
repo_query = '''
    query search($queryString: String!, $first: Int, $after: String) {
      search(query: $queryString, type: REPOSITORY, first: $first, after: $after) {
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
              stargazers {
                totalCount
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
              mergedAt
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