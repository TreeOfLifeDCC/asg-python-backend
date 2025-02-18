import os

import requests

from elasticsearch import Elasticsearch
from elasticsearch import RequestsHttpConnection

es = Elasticsearch(["https://prj-ext-dev-asg-gcp-dr-349815.es.europe-west2.gcp.elastic-cloud.com"],
                   connection_class=RequestsHttpConnection,
                   http_auth=("elastic", "7ud5Ny7dVIgnXWHD4DBCEREf"),
                   use_ssl=False, verify_certs=False,
                   ssl_show_warn=False)


def create_articles_index():
    dest_node = 'https://elastic:7ud5Ny7dVIgnXWHD4DBCEREf@prj-ext-dev-asg-gcp-dr-349815.es.europe-west2.gcp.elastic-cloud.com'
    index_name = 'articles'

    # delete index
    # cmd = f"curl -k -X DELETE '{dest_node}/{index_name}'"
    # print(cmd)
    # os.system(cmd)
    # print()

    # create index
    # cmd = f"curl -k -X PUT '{dest_node}/{index_name}' -H 'Content-Type: application/json' " \
    #       f"-d @elasticsearch/erga_settings.json"
    # print(cmd)
    # os.system(cmd)
    # print()
    #
    # # put the mapping
    # cmd = f"curl -k -X PUT '{dest_node}/{index_name}/_mapping' -H 'Content-Type: application/json' " \
    #       f"-d @elasticsearch/{index_name}.mapping.json"
    # print(cmd)
    # os.system(cmd)
    # print()

    # resp = es.indices.create(
    #     index="articles",
    #     settings = {
    #     "max_result_window": "1000000",
    #     "analysis": {
    #         "filter": {
    #             "autocomplete_filter": {
    #                 "token_chars": [
    #                     "letter",
    #                     "digit",
    #                     "whitespace"
    #                 ],
    #                 "min_gram": "1",
    #                 "type": "edge_ngram",
    #                 "max_gram": "20"
    #             }
    #         },
    #         "normalizer": {
    #             "lower_case_normalizer": {
    #                 "filter": [
    #                     "lowercase"
    #                 ],
    #                 "type": "custom"
    #             }
    #         },
    #         "analyzer": {
    #             "autocomplete": {
    #                 "filter": [
    #                     "lowercase",
    #                     "autocomplete_filter"
    #                 ],
    #                 "type": "custom",
    #                 "tokenizer": "standard"
    #             }
    #         }
    #         }
    #      },
    #     mappings= {
    #     "properties": {
    #         "abstract": {
    #             "type": "text",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 }
    #             }
    #         },
    #         "articleType": {
    #             "type": "keyword",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 },
    #                 "normalize": {
    #                     "type": "keyword",
    #                     "normalizer": "lower_case_normalizer"
    #                 }
    #             }
    #         },
    #         "authorString": {
    #             "type": "text",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 }
    #             }
    #         },
    #         "caption": {
    #             "type": "text",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 }
    #             }
    #         },
    #         "citeURL": {
    #             "type": "text",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 }
    #             }
    #         },
    #         "citedByCount": {
    #             "type": "long"
    #         },
    #         "dbCrossReferenceList": {
    #             "properties": {
    #                 "dbName": {
    #                     "type": "text",
    #                     "fields": {
    #                         "keyword": {
    #                             "type": "keyword",
    #                             "ignore_above": 256
    #                         }
    #                     }
    #                 }
    #             }
    #         },
    #         "doi": {
    #             "type": "text",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 }
    #             }
    #         },
    #         "figureURI": {
    #             "type": "text",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 }
    #             }
    #         },
    #         "firstIndexDate": {
    #             "type": "date"
    #         },
    #         "firstPublicationDate": {
    #             "type": "date"
    #         },
    #         "fullTextIdList": {
    #             "properties": {
    #                 "fullTextId": {
    #                     "type": "text",
    #                     "fields": {
    #                         "keyword": {
    #                             "type": "keyword",
    #                             "ignore_above": 256
    #                         }
    #                     }
    #                 }
    #             }
    #         },
    #         "hasBook": {
    #             "type": "text",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 }
    #             }
    #         },
    #         "hasDbCrossReferences": {
    #             "type": "text",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 }
    #             }
    #         },
    #         "hasLabsLinks": {
    #             "type": "text",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 }
    #             }
    #         },
    #         "hasPDF": {
    #             "type": "text",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 }
    #             }
    #         },
    #         "hasReferences": {
    #             "type": "text",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 }
    #             }
    #         },
    #         "hasSuppl": {
    #             "type": "text",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 }
    #             }
    #         },
    #         "hasTMAccessionNumbers": {
    #             "type": "text",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 }
    #             }
    #         },
    #         "hasTextMinedTerms": {
    #             "type": "text",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 }
    #             }
    #         },
    #         "id": {
    #             "type": "text",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 }
    #             }
    #         },
    #         "inEPMC": {
    #             "type": "text",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 }
    #             }
    #         },
    #         "inPMC": {
    #             "type": "text",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 }
    #             }
    #         },
    #         "isOpenAccess": {
    #             "type": "text",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 }
    #             }
    #         },
    #         "issue": {
    #             "type": "text",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 }
    #             }
    #         },
    #         "journalIssn": {
    #             "type": "text",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 }
    #             }
    #         },
    #         "journalTitle": {
    #             "type": "keyword",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 },
    #                 "normalize": {
    #                     "type": "keyword",
    #                     "normalizer": "lower_case_normalizer"
    #                 }
    #             }
    #         },
    #         "journalVolume": {
    #             "type": "text",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 }
    #             }
    #         },
    #         "organism_name": {
    #             "type": "text",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 }
    #             }
    #         },
    #         "pageInfo": {
    #             "type": "text",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 }
    #             }
    #         },
    #         "pmcid": {
    #             "type": "text",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 }
    #             }
    #         },
    #         "pmid": {
    #             "type": "text",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 }
    #             }
    #         },
    #         "pubType": {
    #             "type": "text",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 }
    #             }
    #         },
    #         "pubYear": {
    #             "type": "keyword",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 },
    #                 "normalize": {
    #                     "type": "keyword",
    #                     "normalizer": "lower_case_normalizer"
    #                 }
    #             }
    #         },
    #         "pub_year": {
    #             "type": "text",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 }
    #             }
    #         },
    #         "source": {
    #             "type": "text",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 }
    #             }
    #         },
    #         "study_id": {
    #             "type": "text",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 }
    #             }
    #         },
    #         "tax_id": {
    #             "type": "text",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 }
    #             }
    #         },
    #         "title": {
    #             "type": "text",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 }
    #             }
    #         },
    #         "tmAccessionTypeList": {
    #             "properties": {
    #                 "accessionType": {
    #                     "type": "text",
    #                     "fields": {
    #                         "keyword": {
    #                             "type": "keyword",
    #                             "ignore_above": 256
    #                         }
    #                     }
    #                 }
    #             }
    #         },
    #         "url": {
    #             "type": "text",
    #             "fields": {
    #                 "keyword": {
    #                     "type": "keyword",
    #                     "ignore_above": 256
    #                 }
    #             }
    #         }
    #     }
    # })
    # print(resp)


# create_articles_index()


def get_samples(index_name, es):
    records_list = {}
    offset = 0
    data = es.search(index=index_name, size=1000, from_=offset)  # Correct parameter
    while len(data['hits']['hits']) > 0:
        for record in data['hits']['hits']:
            records_list[record['_id']] = record['_source']
        offset += 1000
        data = es.search(index=index_name, size=1000, from_=offset)
    return records_list

def create_articles():
    data_portal = get_samples("data_portal_test", es)
    # print(data_portal)
    articles = list()

    for tax_id, record in data_portal.items():
        if 'genome_notes' in record and len(record["genome_notes"]) > 0:
            for article in record["genome_notes"]:
                try:
                    # Fetch article details from EuropePMC API
                    article_response = requests.get(
                        f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={article['study_id']}&format=json").json()

                    # Extract publication year if available
                    if article_response.get('resultList', {}).get('result', []):
                        pub_year = article_response['resultList']['result'][0].get('pubYear')
                    else:
                        pub_year = None

                    # Populate article fields
                    article['pub_year'] = pub_year
                    article['pubYear'] = pub_year
                    article['id'] = article['study_id']
                    article['articleType'] = 'Genome Note'
                    article['journalTitle'] = 'Wellcome Open Res'
                    article['organism_name'] = record['organism']

                    articles.append(article)

                    # Index the article into Elasticsearch
                    es.index(
                        index="articles",
                        id=article['study_id'],  # Set document ID explicitly
                        body = article
                    )
                except requests.RequestException as e:
                    print(f"Failed to fetch article details for study_id {article['study_id']}: {e}")
                except Exception as e:
                    print(f"Error indexing article for study_id {article['study_id']}: {e}")

    print(len(articles))


if __name__ == "__main__":
    create_articles()