from typing import List

from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

from exceptions.error_codes import ErrorCode
from exceptions.exception import AppException
from schemas.section_schema import SectionVO, SectionPage, SectionRetrieval


class SectionRepository:
    @staticmethod
    def get_sections(es: Elasticsearch, lid: int, keyword: str, page: int, pagesize: int) -> SectionPage:
        if not keyword and not lid:
            query = {
                "query": {
                    "match_all": {}  # 查询所有文档
                },
                "from": (page - 1) * pagesize,  # 起始页计算，page 从 1 开始
                "size": pagesize,  # 每页返回的记录数
                "track_total_hits": True,  # 确保 Elasticsearch 返回 total count
                "sort": [
                    {
                        "order_num": {
                            "order": "asc"  # 按 order_num 降序排序
                        }
                    }
                ]
            }
        else:
            # 构造 bool 查询，组合关键词搜索和状态筛选
            query = {
                "query": {
                    "bool": {
                        "must": [],  # 必须匹配的条件
                    }
                },
                "from": (page - 1) * pagesize,
                "size": pagesize,
                "track_total_hits": True,  # 确保 Elasticsearch 返回 total count
                "sort": [
                    {
                        "order_num": {
                            "order": "asc"  # 按 order_num 降序排序
                        }
                    }
                ]
            }

            if keyword:
                query["query"]["bool"]["must"].append({
                    "match": {
                        "content": keyword  # 这里应使用 'content' 作为字段名，而不是 'query' 或 'fields'
                    }
                })

                query["highlight"] = {
                    "pre_tags": ["<span style='color:red'>"],
                    "post_tags": ["</span>"],
                    "fields": {
                        "content": {
                            "fragment_size": 1000,
                            "number_of_fragments": 1
                        }
                    }  # 高亮 content 字段
                }

            # 如果有状态，添加 term 查询
            if lid:
                query["query"]["bool"]["must"].append({
                    "term": {
                        "lid": lid
                    }
                })
        try:
            # 执行查询
            response = es.search(index="sections", body=query)
            # 解析结果，返回文档内容
        except Exception as e:
            raise AppException(ErrorCode.ELASTICSEARCH_ERROR, f"ES 查询失败: {str(e)}") from e

        sections = []
        try:
            for hit in response['hits']['hits']:
                section = SectionVO(**hit['_source'])
                section.content_highlight = hit.get('highlight', {}).get('content', [section.content])[0]
                sections.append(section)
            page = SectionPage(total=response['hits']['total']['value'], sections=sections)
            return page
        except Exception as e:
            raise e

    @staticmethod
    def retrieve_sections_knn_paginated(
            es: Elasticsearch,
            embedding_model: SentenceTransformer,
            query: str,
            page: int = 1,
            page_size: int = 5,
            top_k: int = 50,
    ) -> SectionPage:
        """
        使用 KNN 排序的语义检索分页方法，total 为全量文档总数
        """
        # 2. 执行语义排序的检索
        response = es.search(
            index="sections",
            size=top_k,  # 返回最多 top_k 条结果
            knn={
                "field": "embedding",
                "query_vector": embedding_model.encode(query).tolist(),
                "k": top_k,
                "num_candidates": max(10, top_k + 5),
            }
        )

        # 3. 获取分页命中
        hits = response["hits"]["hits"]
        start_idx = (page - 1) * page_size
        paginated_hits = hits[start_idx:start_idx + page_size]

        # 4. 转换为 SectionVO 对象
        sections = []
        for hit in paginated_hits:
            section = SectionVO(**hit["_source"])
            sections.append(section)

        # 5. 返回分页结果，total 为全量文档数
        return SectionPage(total=top_k, sections=sections)

    @staticmethod
    def retrieve_sections_bm25_paginated(
            es: Elasticsearch,
            query: str,
            page: int = 1,
            page_size: int = 5
    ) -> SectionPage:
        """
        基于关键词匹配（BM25）的分页检索方法
        """
        # 构造查询体
        body = {
            # "profile": True,
            "query": {
                # "match_phrase": {
                #     "content": {
                #         "query": query
                #     }
                # }
                # "match": {
                #     "content": query
                #
                # },
                "match": {
                    "content": {
                        "query": query,
                        "operator": "and"
                    }
                }
            },
            "from": (page - 1) * page_size,
            "size": page_size,
            "track_total_hits": True,
            "highlight": {
                "pre_tags": ["<span style='color:red'>"],
                "post_tags": ["</span>"],
                "fields": {
                    "content": {
                        "fragment_size": 1000,
                        "number_of_fragments": 1
                    }
                }
            },
            "sort": [
                {
                    "_score": {
                        "order": "desc"
                    }
                },
                {
                    "order_num": {
                        "order": "asc"
                    }
                }
            ]
        }

        # 发起检索请求
        try:
            response = es.search(index="sections", body=body)
        except Exception as e:
            raise AppException(ErrorCode.ELASTICSEARCH_ERROR, f"BM25 ES 查询失败: {str(e)}") from e

        # 构造返回数据
        sections = []
        for hit in response["hits"]["hits"]:
            section = SectionVO(**hit["_source"])
            section.content_highlight = hit.get("highlight", {}).get("content", [section.content])[0]
            sections.append(section)

        total = response["hits"]["total"]["value"]
        return SectionPage(total=total, sections=sections)

    @staticmethod
    def retrieve_sections_knn(es: Elasticsearch, embedding_model: SentenceTransformer, query: str, top_k: int = 5) -> \
            List[SectionVO]:
        response = es.search(
            index="sections",
            size=top_k,
            knn={
                "field": "embedding",
                "query_vector": embedding_model.encode(query).tolist(),
                "k": 5,
                "num_candidates": 10,
            },
        )
        sections = []
        for hit in response['hits']['hits']:
            section = SectionVO(**hit['_source'])
            sections.append(section)
        return sections

    @staticmethod
    def retrieve_sections_hybrid(
            es: Elasticsearch,
            embedding_model: SentenceTransformer,
            query: str,
            top_k: int = 5,
            knn_weight: float = 1  # 设定 kNN 权重，BM25 权重 = 1 - knn_weight
    ) -> List[SectionVO]:
        query_vector = embedding_model.encode(query).tolist()

        # kNN 向量检索
        knn_query = {
            "knn": {
                "field": "embedding",
                "query_vector": query_vector,
                "k": top_k,
                "num_candidates": top_k * 2
            }
        }

        # BM25 关键词检索
        bm25_query = {
            "match": {
                "content": query
            }
        }

        # 组合查询 (Hybrid Search)
        hybrid_query = {
            "bool": {
                "should": [
                    knn_query,  # 向量检索
                    bm25_query  # 关键词检索
                ]
            }
        }

        response = es.search(
            index="sections",
            size=top_k * 3,  # 多取一些候选项，后续融合
            body={
                "query": hybrid_query
            }
        )

        # 处理检索结果
        results = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            knn_score = hit.get("_knn_score", 0)  # 可能的 kNN 评分
            bm25_score = hit["_score"]  # BM25 评分
            final_score = knn_weight * knn_score + (1 - knn_weight) * bm25_score  # 加权平均
            results.append((final_score, SectionVO(**source)))

        # 按最终得分排序并返回 top_k 结果
        results.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in results[:top_k]]

    @staticmethod
    def retrieval_in_chat(
            es: Elasticsearch,
            embedding_model: SentenceTransformer,
            query: str,
            top_k: int = 5
    ) -> List[SectionRetrieval]:
        """
        使用语义检索（KNN）方法进行检索
        """
        # 1. 计算查询的嵌入向量
        query_vector = embedding_model.encode(query).tolist()

        # 2. 执行 KNN 检索
        response = es.search(
            index="sections",
            size=top_k,
            knn={
                "field": "embedding",
                "query_vector": query_vector,
                "k": top_k,
                "num_candidates": top_k * 2
            }
        )

        # 3. 处理检索结果
        sections = []
        for hit in response['hits']['hits']:
            section = SectionRetrieval(**hit['_source'])
            sections.append(section)
        return sections
