from langchain_community.document_loaders import UnstructuredMarkdownLoader

loader = UnstructuredMarkdownLoader(
    path="../test.txt",
    mode='single'
)