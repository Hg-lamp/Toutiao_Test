#定义文本切割器
from langchain_text_splitters import CharacterTextSplitter

text_spliter = CharacterTextSplitter(
    #按照双换行作为拆分规则
    separator="\n\n",
    #设置每一块的大小
    chunk_size=100,
    #设置块的重叠大小
    chunk_overlap=20,
    #设置字符长度的测量函数
    length_function=len,
    #是否正则表达式描写分隔符
    is_separator_regex=True
)