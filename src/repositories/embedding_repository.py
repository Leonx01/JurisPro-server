import json

from elasticsearch import Elasticsearch, helpers
from elasticsearch.helpers import BulkIndexError
from sentence_transformers import SentenceTransformer


class EmbeddingRepository:
    @staticmethod
    def generate_embeddings(es: Elasticsearch, embedding_model: SentenceTransformer, index_name: str, text_filed: str,
                            embedding_field: str = "embedding", batch_size: int = 1000):
        query = {
            "query": {
                "bool": {
                    "must": [{"exists": {"field": text_filed}}],
                    "must_not": [{"exists": {"field": embedding_field}}]
                }
            },
            "_source": [text_filed]
        }

        scroll = es.search(index=index_name, body=query, scroll="2m", size=batch_size)
        scroll_id = scroll["_scroll_id"]
        total_docs = scroll["hits"]["total"]["value"]
        processed_docs = 0
        batch_num = 0

        print(f"Total documents needing embeddings: {total_docs}")

        while scroll["hits"]["hits"]:
            actions = []
            batch_num += 1
            hits = scroll["hits"]["hits"]

            for doc in hits:
                doc_id = doc["_id"]
                content = doc["_source"].get(text_filed, "")
                if not content:
                    continue

                try:
                    embedding = embedding_model.encode(content).tolist()
                except Exception as e:
                    print(f"Encoding error for doc {doc_id}: {e}")
                    continue

                action = {
                    "_op_type": "update",
                    "_index": index_name,
                    "_id": doc_id,
                    "doc": {embedding_field: embedding}

                }
                actions.append(action)

            # 批量更新
            if actions:
                try:
                    helpers.bulk(es, actions)
                    processed_docs += len(actions)
                    print(f"[Batch {batch_num}] Processed {processed_docs}/{total_docs} documents")
                except BulkIndexError as e:
                    print(f"[Batch {batch_num}] BulkIndexError occurred:")
                    for error in e.errors:
                        print(json.dumps(error, ensure_ascii=False, indent=2))

            # 获取下一批数据
            scroll = es.scroll(scroll_id=scroll_id, scroll="2m")
            scroll_id = scroll.get("_scroll_id")

        es.clear_scroll(scroll_id=scroll_id)
        print("Embedding generation completed.")
