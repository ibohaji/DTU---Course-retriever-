from ragatouille import RAGPretrainedModel
from ragatouille.utils import get_wikipedia_page
import math
import json 
import torch
from transformers import AutoTokenizer


def index_doc(document, index_name, id=None, metadata=None):
    chunked_docs, chunked_ids, chunked_metadata = chunk_if_needed(document, id, metadata)
    RAG = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")
    index_path = RAG.index(
        index_name=index_name, 
        collection=chunked_docs, 
        document_ids=chunked_ids, 
        document_metadatas=chunked_metadata
    )
    return index_path




def chunk_if_needed(document, ids, metadata): 
    
    tokenizer = AutoTokenizer.from_pretrained("colbert-ir/colbertv2.0")
    
    chunked_docs = []
    chunked_ids = []
    chunked_metadata = []
    
    for idx, doc in enumerate(document):
        tokens = tokenizer.encode(doc, return_tensors="pt")
        if tokens.shape[1] > 512:
            num_chunks = math.ceil(tokens.shape[1] / 512)
            for i in range(num_chunks):
                chunk = tokenizer.decode(tokens[0, i*512:(i+1)*512])
                chunked_docs.append(chunk)
                # Modify ID and metadata to indicate chunk number
                if ids is not None:
                    chunked_ids.append(f"{ids[idx]}_chunk_{i}")
                if metadata is not None:
                    chunk_metadata = metadata[idx].copy()
                    chunk_metadata['chunk_number'] = i
                    chunk_metadata['course_number'] = ids[idx]
                    chunk_metadata['total_chunks'] = num_chunks
                    chunked_metadata.append(chunk_metadata)
        else:
            chunked_docs.append(doc)
            if ids is not None:
                chunked_ids.append(ids[idx])
            if metadata is not None:
                chunk_metadata = metadata[idx].copy()
                chunk_metadata["course_number"] = ids[idx]
                chunked_metadata.append(chunk_metadata)
    
    return chunked_docs, chunked_ids, chunked_metadata



def preprocess_document(documents): 
    documents_out = []
    ids = []
    metadata = []
    for i, doc in enumerate(documents):
        text = doc["content"] + doc["learning_objectives"] + doc["general_course_objectives"]
        text = text.encode('ascii', 'ignore').decode('ascii')
        documents_out.append(doc["content"] + doc["learning_objectives"] + doc["general_course_objectives"])
        ids.append(doc["course_number"])
        metadata.append({"course_name": doc["course_name"]})
            
            
    return documents_out, ids, metadata



if __name__ == "__main__":
    print("Script started")

    print("Attempting to open courses_with_details.json")
    with open("courses_with_details_new_temp.json", "r") as f:
        data = json.load(f)
        
        documents_out, ids, metadata = preprocess_document(data)

    # Print document lengths
    for i in range(min(10, len(documents_out))):
        print(f"Document {i+1}: {len(documents_out[i])}")

    print("Starting indexing process...")
    index_doc(documents_out, "DTU Course-base", id=ids, metadata=metadata)
    print("Indexing completed")
    

    
    


