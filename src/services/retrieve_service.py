# 示例文件：Elasticsearch 向量检索示例
# 注意：此文件为示例代码，实际使用时请根据项目需求修改

from langchain_elasticsearch import ElasticsearchStore
from elasticsearch import Elasticsearch

from src.configs import settings

# 使用配置中的 Elasticsearch 连接
elastic_client = Elasticsearch(
    hosts=settings.elastic.hosts,
    basic_auth=(settings.elastic.user, settings.elastic.password.get_secret_value()),
    ca_certs=settings.elastic.ca_certs,
)

# 示例：创建向量存储
# vector_store = ElasticsearchStore(
#     es_url=settings.elastic.hosts,
#     index_name="your_index_name",
#     embedding=your_embedding_model,
#     es_user=settings.elastic.user,
#     es_password=settings.elastic.password.get_secret_value(),
#     es_connection=elastic_client,
# )

# 示例：相似性搜索
# results = vector_store.similarity_search(
#     query="your query",
#     k=2,
# )
# for res in results:
#     print(f"* {res.page_content} [{res.metadata}]")
