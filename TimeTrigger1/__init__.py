import os
import logging
import datetime
import requests
from azure.cosmosdb.table.tableservice import TableService, TableBatch
import azure.functions as func

API_KEY = os.environ['API_KEY']
GITHUB_USER = os.environ['GITHUB_USER']
TABLE_SERVICE_CONNECTION_STRING = os.environ['TABLE_SERVICE_CONNECTION_STRING']


def get_all_repositories():
    service_url = f'https://api.github.com/users/{GITHUB_USER}/repos'
    auth = (GITHUB_USER, API_KEY)
    response = requests.get(service_url, auth=auth)

    if response.status_code != 200:
        logging.error(response.content)
        return

    results = response.json()
    results = filter(lambda x: x['fork'] is False, results)
    results = map(lambda x:
                  {'repo_id': x['id'],
                   'repo_url': x['url'],
                   'repo_name': x['name']}, results)
    results = list(results)

    return results


def get_repo_attention(url: str, attention: str = 'clones'):
    assert attention in ('clones', 'views')

    service_url = url + '/traffic/' + attention
    auth = (GITHUB_USER, API_KEY)
    response = requests.get(service_url, auth=auth)

    if response.status_code != 200:
        logging.error(response.content)
        return

    results = response.json()
    results = results[attention]

    return results


def get_and_update_repo_attention(
        table_service: TableService,
        repo_id: int, repo_url: str, repo_name: str,
        attention: str = 'clones'):
    assert attention in ('clones', 'views')

    results = get_repo_attention(url=repo_url, attention=attention)

    batch = TableBatch()

    if results is not None:
        for el in results:
            batch.insert_or_replace_entity({
                'PartitionKey': str(repo_id),
                'RowKey': el['timestamp'],
                'name': repo_name,
                'count': el['count'],
                'uniques': el['uniques']
            })

    table_service.commit_batch(table_name=f'github{attention}', batch=batch)


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    table_service = TableService(
        connection_string=TABLE_SERVICE_CONNECTION_STRING
    )

    repositories = get_all_repositories()

    for repo in repositories:
        get_and_update_repo_attention(table_service, attention='clones', **repo)
        get_and_update_repo_attention(table_service, attention='views', **repo)

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
