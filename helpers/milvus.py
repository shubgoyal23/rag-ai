import os
from pymilvus import DataType, MilvusClient

# Initialize Milvus client
milvus_uri = os.getenv("MILVUS_URI")
token = os.getenv("MILVUS_TOKEN")
milvus_client = MilvusClient(uri=milvus_uri, token=token)
print(f"Connected to DB: {milvus_uri} successfully")

# Collection configuration
collection_name = "doc_vectors"
dim_txt = 1536
metric="COSINE"
index="HNSW"


def create_Collection():
    # Clean up existing collection
	if milvus_client.has_collection(collection_name):
		milvus_client.drop_collection(collection_name)
	print(f"Dropped existing collection {collection_name}")
     
	# Create proper schema for image vectors
	schema = milvus_client.create_schema(
	    auto_id=True,  # We'll provide our own IDs
	    enable_dynamic_field=True
	)

	# Add fields matching your data structure
	schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True, auto_id=True,)
	schema.add_field(field_name="job_id", datatype=DataType.VARCHAR, max_length=256)
	schema.add_field(field_name="reference_id", datatype=DataType.VARCHAR, max_length=256)
	schema.add_field(field_name="content", datatype=DataType.VARCHAR, max_length=2000)
	schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=dim_txt)

	# Create index parameters for cosine similarity (CLIP vectors are normalized)
	index_params = milvus_client.prepare_index_params()
	index_params.add_index(
	    field_name="vector",
	    metric_type=metric, 
	    index_type=index,
	)
	# Create collection
	milvus_client.create_collection(
	    collection_name=collection_name,
	    schema=schema,
	    index_params=index_params
	)
	print(f"Collection {collection_name} created successfully")


## check if collection exists and create if not
if not milvus_client.has_collection(collection_name):
	create_Collection()


## insert data into milvus, same as insert_data
def insert_vector_data(entities) -> str:
    try:
        result = milvus_client.insert(collection_name, entities)
        flush_collection()
        return True
    except Exception as e:
        print((f"Error inserting data: {e}"))
        return False

def flush_collection():
    milvus_client.flush(collection_name)


# Search text function
def search_similar_text(query_vector, top_k=5, expr=""):
    res = milvus_client.search(
    collection_name=collection_name,
    anns_field="vector",
    data=[query_vector],
    limit=top_k,
    search_params={"metric_type": metric},
    output_fields=["job_id", "reference_id", "content"]  # Return URL field
	)
    ret = [
    f'{hit["distance"]}, {hit["entity"]["job_id"]}, {hit["entity"]["reference_id"]}, {hit["entity"]["content"]}'
    for hit in res[0]
	]
    return ret