import csv
import io
import re
from http.client import HTTPException
import os
import httpx
from elasticsearch import AsyncElasticsearch, AIOHttpConnection, \
    ConnectionTimeout
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from starlette.responses import JSONResponse

from .constants import DATA_PORTAL_AGGREGATIONS, ARTICLES_AGGREGATIONS

app = FastAPI()

origins = [
    "*"
]


ES_HOST = os.getenv('ES_CONNECTION_URL')

ES_USERNAME = os.getenv('ES_USERNAME')

ES_PASSWORD = os.getenv('ES_PASSWORD')

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

es = AsyncElasticsearch(
    [ES_HOST],
    timeout=30,
    connection_class=AIOHttpConnection,
    http_auth=(ES_USERNAME, ES_PASSWORD),
    use_ssl=True, verify_certs=True)


@app.get("/downloader_utility_data/")
async def downloader_utility_data(taxonomy_filter: str, data_status: str,
                                  experiment_type: str, project_name: str):
    body = dict()
    if taxonomy_filter != '':

        if taxonomy_filter:
            body["query"] = {
                "bool": {
                    "filter": list()
                }
            }
            nested_dict = {
                "nested": {
                    "path": "taxonomies.class",
                    "query": {
                        "bool": {
                            "filter": list()
                        }
                    }
                }
            }
            nested_dict["nested"]["query"]["bool"]["filter"].append(
                {
                    "term": {
                        "taxonomies.class.scientificName": taxonomy_filter
                    }
                }
            )
            body["query"]["bool"]["filter"].append(nested_dict)

    if data_status is not None and data_status != '':
        split_array = data_status.split("-")
        if split_array and split_array[0].strip() == 'Biosamples':
            body["query"]["bool"]["filter"].append(
                {"term": {'biosamples': split_array[1].strip()}}
            )
        elif split_array and split_array[0].strip() == 'Raw Data':
            body["query"]["bool"]["filter"].append(
                {"term": {'raw_data': split_array[1].strip()}}
            )
        elif split_array and split_array[0].strip() == 'Mapped Reads':
            body["query"]["bool"]["filter"].append(
                {"term": {'mapped_reads': split_array[1].strip()}})

        elif split_array and split_array[0].strip() == 'Assemblies':
            body["query"]["bool"]["filter"].append(
                {"term": {'assemblies_status': split_array[1].strip()}})
        elif split_array and split_array[0].strip() == 'Annotation Complete':
            body["query"]["bool"]["filter"].append(
                {"term": {'annotation_complete': split_array[1].strip()}})
        elif split_array and split_array[0].strip() == 'Annotation':
            body["query"]["bool"]["filter"].append(
                {"term": {'annotation_status': split_array[1].strip()}})
        elif split_array and split_array[0].strip() == 'Genome Notes':
            nested_dict = {
                "nested": {
                    "path": "genome_notes",
                    "query": {
                        "bool": {
                            "must": [{
                                "exists": {
                                    "field": "genome_notes.url"
                                }
                            }]
                        }
                    }
                }
            }
            body["query"]["bool"]["filter"].append(nested_dict)
    if experiment_type != '' and experiment_type is not None:
        nested_dict = {
            "nested": {
                "path": "experiment",
                "query": {
                    "bool": {
                        "must": [{
                            "term": {
                                "experiment.library_construction_protocol."
                                "keyword": experiment_type
                            }
                        }]
                    }
                }
            }
        }
        body["query"]["bool"]["filter"].append(nested_dict)
    if project_name is not None and project_name != '':
        body["query"]["bool"]["filter"].append(
            {"term": {'project_name': project_name}})

    response = await es.search(index="data_portal", from_=0, size=10000,
                               body=body)
    total_count = response['hits']['total']['value']
    result = response['hits']['hits']
    results_count = len(response['hits']['hits'])
    while total_count > results_count:
        response1 = await es.search(index="data_portal", from_=results_count,
                                    size=10000, body=body)
        result.extend(response1['hits']['hits'])
        results_count += len(response1['hits']['hits'])

    return result


@app.get("/downloader_utility_data_with_species/")
async def downloader_utility_data_with_species(species_list: str,
                                               project_name: str):
    body = dict()
    result = []
    if species_list != '' and species_list is not None:
        species_list_array = species_list.split(",")
        for organism in species_list_array:
            body["query"] = {
                "bool": {"filter": [{'term': {'_id': organism}},
                                    {'term': {'project_name': project_name}}]}}
            response = await es.search(index='data_portal',
                                       body=body)
            result.extend(response['hits']['hits'])

    return result


@app.get("/summary")
async def summary():
    response = await es.search(index="summary")
    data = dict()
    data['results'] = response['hits']['hits']
    return data


def convert_to_title_case(input_string):
    # Add a space before each capital letter
    spaced_string = re.sub(r'([A-Z])', r' \1', input_string)

    # Split the string into words, capitalize each word, and join
    # them with a space
    title_cased_string = ' '.join(
        word.capitalize() for word in spaced_string.split())

    return title_cased_string


@app.get("/detail_table_organism_filters")
async def get_detail_table_organism_filters():
    result = []
    body = {
        "size": 0, "aggregations": {
            "trackingSystem": {"nested": {"path": "trackingSystem"}, "aggs": {
                "rank": {"terms": {"field": "trackingSystem.rank",
                                   "order": {"_key": "desc"}},
                         "aggregations": {
                             "name": {
                                 "terms": {"field": "trackingSystem.name"},
                                 "aggregations": {"status": {"terms": {
                                     "field": "trackingSystem.status"}}}}}}}},
            "symbionts_biosamples_status": {
                "terms": {"field": "symbionts_biosamples_status"}},
            "symbionts_raw_data_status": {
                "terms": {"field": "symbionts_raw_data_status"}},
            "symbionts_assemblies_status": {
                "terms": {"field": "symbionts_assemblies_status"}},
            "metagenomes_biosamples_status": {
                "terms": {"field": "metagenomes_biosamples_status"}},
            "metagenomes_raw_data_status": {
                "terms": {"field": "metagenomes_raw_data_status"}},
            "metagenomes_assemblies_status": {
                "terms": {"field": "metagenomes_assemblies_status"}}
        }
    }

    data = dict()
    response = await es.search(index='tracking_status_index',
                               size=0, body=body)
    data['buckets'] = response['aggregations']['trackingSystem']['rank'][
        'buckets']


@app.get("/tracking_system_filters")
async def get_filters():
    """

    :return:
    """
    result = []
    body = {
        "size": 0, "aggregations": {
            "trackingSystem": {"nested": {"path": "trackingSystem"}, "aggs": {
                "rank": {"terms": {"field": "trackingSystem.rank",
                                   "order": {"_key": "desc"}},
                         "aggregations": {
                             "name": {
                                 "terms": {"field": "trackingSystem.name"},
                                 "aggregations": {"status": {"terms": {
                                     "field": "trackingSystem.status"}}}}}}}},
            "symbionts_biosamples_status": {
                "terms": {"field": "symbionts_biosamples_status"}},
            "symbionts_raw_data_status": {
                "terms": {"field": "symbionts_raw_data_status"}},
            "symbionts_assemblies_status": {
                "terms": {"field": "symbionts_assemblies_status"}},
            "metagenomes_biosamples_status": {
                "terms": {"field": "metagenomes_biosamples_status"}},
            "metagenomes_raw_data_status": {
                "terms": {"field": "metagenomes_raw_data_status"}},
            "metagenomes_assemblies_status": {
                "terms": {"field": "metagenomes_assemblies_status"}}
        }
    }

    data = dict()
    response = await es.search(index='tracking_status_index',
                               size=0, body=body)
    data['buckets'] = response['aggregations']['trackingSystem']['rank'][
        'buckets']
    for entry in data['buckets']:
        for name_bucket in entry['name']['buckets']:
            name = name_bucket['key']
            if name == 'annotation_complete' or name == 'biosamples' or name \
                    == 'assemblies' or name == 'raw_data':
                for status_bucket in name_bucket['status']['buckets']:
                    status = status_bucket['key']
                    status_doc_count = status_bucket['doc_count']
                    if status == 'Done':
                        # Append the results
                        result.append({
                            'name': name,
                            'doc_count': status_doc_count
                        })
    result.append({
        'name': 'symbionts_biosamples_status',
        'doc_count': response['aggregations']['symbionts_biosamples_status'][
            'buckets']
    })
    result.append({
        'name': 'symbionts_raw_data_status',
        'doc_count': response['aggregations']['symbionts_raw_data_status'][
            'buckets']
    })
    result.append({
        'name': 'symbionts_assemblies_status',
        'doc_count': response['aggregations']['symbionts_assemblies_status'][
            'buckets']
    })
    result.append({
        'name': 'metagenomes_biosamples_status',
        'doc_count': response['aggregations']['metagenomes_biosamples_status'][
            'buckets']
    })
    result.append({
        'name': 'metagenomes_raw_data_status',
        'doc_count': response['aggregations']['metagenomes_raw_data_status'][
            'buckets']
    })
    result.append({
        'name': 'metagenomes_assemblies_status',
        'doc_count': response['aggregations']['metagenomes_assemblies_status'][
            'buckets']
    })
    return result


@app.get("/{index}")
async def root(index: str, offset: int = 0, limit: int = 15,
               sort: str = None, filter: str = None,
               search: str = None, current_class: str = 'kingdom',
               phylogeny_filters: str = None, action: str = None):
    if index == 'favicon.ico':
        return None
    global value
    print(phylogeny_filters)
    # data structure for ES query
    body = dict()
    # building aggregations for every request
    body["aggs"] = dict()
    if 'articles' in index:
        aggregations_list = ARTICLES_AGGREGATIONS
    else:
        aggregations_list = DATA_PORTAL_AGGREGATIONS

    for aggregation_field in aggregations_list:
        if aggregation_field == 'asg_species_group':
            body["aggs"][aggregation_field] = {
                "terms": {"field": aggregation_field}
            }
        else:
            body["aggs"][aggregation_field] = {
                "terms": {"field": aggregation_field + '.keyword'}
            }
    body["aggs"]["taxonomies"] = {
        "nested": {"path": f"taxonomies.{current_class}"},
        "aggs": {current_class: {
            "terms": {
                "field": f"taxonomies.{current_class}.scientificName"
            }
        }
        }
    }
    body["aggs"]["experiment"] = {
        "nested": {"path": "experiment"},
        "aggs": {"library_construction_protocol": {"terms": {
            "field": "experiment.library_construction_protocol.keyword"}
        }
        }
    }
    body["aggs"]["genome"] = {
        "nested": {"path": "genome_notes"},
        "aggs": {"genome_count": {"cardinality": {"field": "genome_notes.id"}
                                  }}

    }
    if phylogeny_filters:
        body["query"] = {
            "bool": {
                "filter": list()
            }
        }
        phylogeny_filters = phylogeny_filters.split("-")
        print(phylogeny_filters)
        for phylogeny_filter in phylogeny_filters:
            name, value = phylogeny_filter.split(":")
            nested_dict = {
                "nested": {
                    "path": f"taxonomies.{name}",
                    "query": {
                        "bool": {
                            "filter": list()
                        }
                    }
                }
            }
            nested_dict["nested"]["query"]["bool"]["filter"].append(
                {
                    "term": {
                        f"taxonomies.{name}.scientificName": value
                    }
                }
            )
            body["query"]["bool"]["filter"].append(nested_dict)
    # adding filters, format: filter_name1:filter_value1, etc...
    if filter:
        filters = filter.split(",")
        if 'query' not in body:
            body["query"] = {
                "bool": {
                    "filter": list()
                }
            }
        for filter_item in filters:
            if current_class in filter_item:
                _, value = filter_item.split(":")
                nested_dict = {
                    "nested": {
                        "path": f"taxonomies.{current_class}",
                        "query": {
                            "bool": {
                                "filter": list()
                            }
                        }
                    }
                }
                nested_dict["nested"]["query"]["bool"]["filter"].append(
                    {
                        "term": {
                            f"taxonomies.{current_class}.scientificName": value
                        }
                    }
                )
                body["query"]["bool"]["filter"].append(nested_dict)

            else:
                filter_name, filter_value = filter_item.split(":")
                if filter_name == 'experimentType':
                    nested_dict = {
                        "nested": {
                            "path": "experiment",
                            "query": {
                                "bool": {
                                    "filter": {
                                        "term": {
                                            "experiment"
                                            ".library_construction_protocol"
                                            ".keyword": filter_value
                                        }
                                    }
                                }
                            }
                        }
                    }
                    body["query"]["bool"]["filter"].append(nested_dict)
                elif filter_name == 'genome_notes':
                    nested_dict = {
                        'nested': {'path': 'genome_notes', 'query': {
                            'bool': {
                                'must': [
                                    {'exists': {
                                        'field': 'genome_notes.url'}}]}}}}
                    body["query"]["bool"]["filter"].append(nested_dict)
                else:
                    print(filter_name)
                    body["query"]["bool"]["filter"].append(
                        {"term": {filter_name: filter_value}})

    # adding search string
    if search:
        if "query" not in body:
            body["query"] = {"bool": {"must": {"bool": {"should": []}}}}
        else:
            body["query"]["bool"].setdefault("must", {"bool":
                                                          {"should": []}})

        search_fields = (
            ["title", "journal_name", "study_id", "organism_name"]
            if 'articles' in index
            else ["organism", "commonName", "symbionts_records.organism.text",
                  "metagenomes_records.organism.text"]
        )

        for field in search_fields:
            body["query"]["bool"]["must"]["bool"]["should"].append({
                "wildcard": {
                    field: {
                        "value": f"*{search}*",
                        "case_insensitive": True
                    }
                }
            })

        wildcard_queries = [
            {"wildcard": {
                field: {"value": f"*{search}*", "case_insensitive": True}}}
            for field in search_fields
        ]
        body["query"]["bool"]["must"]["bool"]["should"].extend(
            wildcard_queries)

        if index == "gis_filter_data":
            # generate nested query for organisms.organism
            nested_query = {
                "nested": {
                    "path": "organisms",
                    "query": {
                        "wildcard": {
                            "organisms.organism": {
                                "value": f"*{search}*",
                                "case_insensitive": True
                            }
                        }
                    }
                }
            }
            body["query"]["bool"]["must"]["bool"]["should"].append(
                nested_query)
    if action == 'download':
        try:
            response = await es.search(index=index, sort=sort, from_=offset,
                                       body=body, size=limit)
        except ConnectionTimeout:
            return {"error": "Request to Elasticsearch timed out."}
    else:
        response = await es.search(index=index, sort=sort, from_=offset,
                                   size=limit, body=body)

    data = dict()
    data['count'] = response['hits']['total']['value']
    data['results'] = response['hits']['hits']
    data['aggregations'] = response['aggregations']
    return data


@app.get("/{index}/{record_id}")
async def details(index: str, record_id: str):
    body = dict()
    if index in ['data_portal', 'data_portal_test']:
        body["query"] = {
            "bool": {
                "filter": [
                    {
                        'term': {
                            'organism': record_id
                        }
                    }
                ]
            }
        }
        body["aggs"] = dict()
        body["aggs"]["metadata_filters"] = {
            'nested': {'path': 'records'},
            "aggs": {
                'sex_filter': {
                    'terms': {
                        'field':
                            'records.sex.keyword',
                        'size': 2000}},
                'tracking_status_filter': {
                    'terms': {
                        'field':
                            'records.'
                            'trackingSystem.keyword',
                        'size': 2000}},
                'organism_part_filter': {
                    'terms': {
                        'field': 'records'
                                 '.organismPart.keyword',
                        'size': 2000}}
            }}
        body["aggs"]["symbionts_filters"] = {
            'nested': {'path': 'symbionts_records'},
            "aggs": {
                'sex_filter': {
                    'terms': {
                        'field':
                            'symbionts_records.sex.keyword',
                        'size': 2000}},
                'tracking_status_filter': {
                    'terms': {
                        'field':
                            'symbionts_records.'
                            'trackingSystem.keyword',
                        'size': 2000}},
                'organism_part_filter': {
                    'terms': {
                        'field': 'symbionts_records'
                                 '.organismPart.keyword',
                        'size': 2000}}
            }}
        body['aggs']['metagenomes_filters'] = {
            'nested': {'path': 'metagenomes_records'},
            "aggs": {
                'sex_filter': {
                    'terms': {
                        'field':
                            'metagenomes_records.sex.keyword',
                        'size': 2000}},
                'tracking_status_filter': {
                    'terms': {
                        'field':
                            'metagenomes_records.'
                            'trackingSystem.keyword',
                        'size': 2000}},
                'organism_part_filter': {
                    'terms': {
                        'field': 'metagenomes_records'
                                 '.organismPart.keyword',
                        'size': 2000}}
            }}

        response = await es.search(index=index, body=body)
        aggregations = response['aggregations']
    else:
        response = await es.search(index=index, q=f"_id:{record_id}")
    data = dict()
    data['count'] = response['hits']['total']['value']
    data['results'] = response['hits']['hits']
    if index in ['data_portal', 'data_portal_test']:
        data['aggregations'] = aggregations
    return data


class QueryParam(BaseModel):
    pageIndex: int
    pageSize: int
    searchValue: str = ''
    sortValue: str
    filterValue: str = ''
    currentClass: str
    phylogeny_filters: str
    index_name: str
    downloadOption: str


@app.post("/data-download")
async def get_data_files(item: QueryParam):
    print(item.index_name)
    data = await fetch_data_in_batches(item)
    print(len(data))
    if len(data) > 0:
        csv_data = create_data_files_csv(data, item.downloadOption,
                                         item.index_name)

        return StreamingResponse(
            csv_data,
            media_type='text/csv',
            headers={"Content-Disposition": "attachment; filename=download.csv"}
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"error": "There was an issue downloading the file"}
        )


async def fetch_data_in_batches(item: QueryParam):
    offset = 0
    batch_size = 1000
    all_data = []

    while True:

        data = await root(
            item.index_name, offset, batch_size,
            item.sortValue, item.filterValue,
            item.searchValue, item.currentClass,
            item.phylogeny_filters, 'download'
        )


        results = data.get('results', [])
        if not results:
            break

        all_data.extend(results)
        offset += batch_size
        print(f"Fetched {len(results)} results, total: {len(all_data)}")

    return all_data

def create_data_files_csv(results, download_option, index_name):
    header = []
    if download_option.lower() == "assemblies":
        header = ["Scientific Name", "Accession", "Version", "Assembly Name",
                  "Assembly Description",
                  "Link to chromosomes, contigs and scaffolds all in one"]
    elif download_option.lower() == "annotation":
        header = ["Annotation GTF", "Annotation GFF3", "Proteins Fasta",
                  "Transcripts Fasta",
                  "Softmasked genomes Fasta"]
    elif download_option.lower() == "raw_files":
        header = ["Study Accession", "Sample Accession",
                  "Experiment Accession",
                  "Run Accession", "Tax Id",
                  "Scientific Name", "FASTQ FTP", "Submitted FTP", "SRA FTP",
                  "Library Construction Protocol"]
    elif download_option.lower() == "metadata" and index_name in [
        'data_portal', 'data_portal_test']:
        header = ['Organism', 'Common Name', 'Common Name Source',
                  'Current Status']

    elif download_option.lower() == "metadata" and index_name in [
        'tracking_status','tracking_status_index_test']:
        header = ['Organism', 'Common Name',
                  'Metadata submitted to BioSamples',
                  'Raw data submitted to ENA',
                  'Mapped reads submitted to ENA',
                  'Assemblies submitted to ENA',
                  'Annotation complete', 'Annotation submitted to ENA']

    output = io.StringIO()
    csv_writer = csv.writer(output)
    csv_writer.writerow(header)

    for entry in results:
        record = entry["_source"]
        if download_option.lower() == "assemblies":
            assemblies = record.get("assemblies", [])
            scientific_name = record.get("organism", "")
            for assembly in assemblies:
                accession = assembly.get("accession", "-")
                version = assembly.get("version", "-")
                assembly_name = assembly.get("assembly_name", "")
                assembly_description = assembly.get("description", "")
                link = f"https://www.ebi.ac.uk/ena/browser/api/fasta/{accession}?download=true&gzip=true" if accession else ""
                entry = [scientific_name, accession, version, assembly_name,
                         assembly_description, link]
                csv_writer.writerow(entry)

        elif download_option.lower() == "annotation":
            annotations = record.get("annotation", [])
            print("annotations: ", annotations)
            for annotation in annotations:
                gtf = annotation.get("annotation", {}).get("GTF", "-")
                gff3 = annotation.get("annotation", {}).get("GFF3", "-")
                proteins_fasta = annotation.get("proteins", {}).get("FASTA",
                                                                    "")
                transcripts_fasta = annotation.get("transcripts", {}).get(
                    "FASTA", "")
                softmasked_genomes_fasta = annotation.get("softmasked_genome",
                                                          {}).get("FASTA", "")
                entry = [gtf, gff3, proteins_fasta, transcripts_fasta,
                         softmasked_genomes_fasta]
                csv_writer.writerow(entry)

        elif download_option.lower() == "raw_files":
            experiments = record.get("experiment", [])
            for experiment in experiments:
                study_accession = experiment.get("study_accession", "")
                sample_accession = experiment.get("sample_accession", "")
                experiment_accession = experiment.get("experiment_accession",
                                                      "")
                run_accession = experiment.get("run_accession", "")
                tax_id = experiment.get("tax_id", "")
                scientific_name = experiment.get("scientific_name", "")
                submitted_ftp = experiment.get("submitted_ftp", "")
                sra_ftp = experiment.get("sra-ftp", "")
                library_construction_protocol = experiment.get(
                    "library_construction_protocol", "")
                fastq_ftp = experiment.get("fastq_ftp", "")

                if fastq_ftp:
                    fastq_list = fastq_ftp.split(";")
                    for fastq in fastq_list:
                        entry = [study_accession, sample_accession,
                                 experiment_accession, run_accession, tax_id,
                                 scientific_name, fastq, submitted_ftp,
                                 sra_ftp,
                                 library_construction_protocol]
                        csv_writer.writerow(entry)
                else:
                    entry = [study_accession, sample_accession,
                             experiment_accession, run_accession, tax_id,
                             scientific_name, fastq_ftp, submitted_ftp,
                             sra_ftp,
                             library_construction_protocol]
                    csv_writer.writerow(entry)

        elif download_option.lower() == "metadata" and index_name in [
            'data_portal', 'data_portal_test']:
            organism = record.get('organism', '')
            common_name = record.get('commonName', '')
            common_name_source = record.get('commonNameSource', '')
            current_status = record.get('currentStatus', '')
            entry = [organism, common_name, common_name_source, current_status]
            csv_writer.writerow(entry)

        elif download_option.lower() == "metadata" and index_name in [
            'tracking_status', 'tracking_status_index_test']:
            organism = record.get('organism', '')
            common_name = record.get('commonName', '')
            metadata_biosamples = record.get('biosamples', '')
            raw_data_ena = record.get('raw_data', '')
            mapped_reads_ena = record.get('mapped_reads', '')
            assemblies_ena = record.get('assemblies_status', '')
            annotation_complete = record.get('annotation_complete', '')
            annotation_submitted_ena = record.get('annotation_status', '')
            entry = [organism, common_name, metadata_biosamples, raw_data_ena,
                     mapped_reads_ena, assemblies_ena,
                     annotation_complete, annotation_submitted_ena]
            csv_writer.writerow(entry)

    output.seek(0)
    return io.BytesIO(output.getvalue().encode('utf-8'))


@app.get("/api/metagenomics/{study_id}/downloads")
async def get_mgnify_metagenomics(study_id):
    mgnify_metagenomics_url = "https://www.ebi.ac.uk/metagenomics/api/v1"
    url = f"{mgnify_metagenomics_url}/studies/{study_id}/downloads"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code,
                                detail=exc.response.text)
        except Exception as e:
            raise HTTPException(status_code=500,
                                detail=f"An error occurred: {str(e)}")
