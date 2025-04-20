from langchain_community.document_loaders import CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_text_splitters import CharacterTextSplitter
#from langchain_text_splitters import NLTKTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore
from langchain_chroma import Chroma
import os
import torch
import gc
torch.cuda.empty_cache()
gc.collect()



#torch_config
device = torch.device("cuda")
torch.cuda.set_per_process_memory_fraction(0.7)

#load_csv
loader = CSVLoader(file_path='geroprotec_corpus.csv',
                   csv_args={'delimiter' : '\t',}, source_column="PMID")

data = loader.load()



#split_csv
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 900, #the character length of the chunk
    chunk_overlap = 20, #the character length of the overlap between chunks
    separators=[".", " ", ","],
    length_function = len, #the length function - character length
)

splits = text_splitter.transform_documents(data)



#text_splitter = CharacterTextSplitter( 
#    chunk_size=1000, 
#    chunk_overlap=200,
#    length_function=len,
#    separator="\n\n"
#)


#text_splitter = NLTKTextSplitter(chunk_size=1000)





embed_model_id = 'nomic-ai/nomic-embed-text-v1.5'
model_kwargs = {'device': 'cuda', 'trust_remote_code' : True}
encode_kwargs = {'batch_size': 1, 'normalize_embeddings': True}

core_embeddings_model = HuggingFaceEmbeddings(model_name=embed_model_id, model_kwargs=model_kwargs, encode_kwargs = encode_kwargs, show_progress=True)

persist_directory = './vectorstore_gero_nomic/'



def split_list(splits, chunk_size):
    for i in range(0, len(splits), chunk_size):
        yield splits[i:i + chunk_size]
        
split_docs_chunked = split_list(splits, 41000)

for split_docs_chunk in split_docs_chunked:
    vectordb = Chroma.from_documents(
        documents=split_docs_chunk,
        embedding=core_embeddings_model,
        persist_directory=persist_directory,
        collection_metadata={"hnsw:space":"cosine"}
    )
    torch.cuda.empty_cache()
    gc.collect()



