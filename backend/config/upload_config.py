"""文件上传相关配置常量。"""

# 支持的文件扩展名
ALLOWED_EXTENSIONS = {
    ".txt", ".md", ".csv",
    ".pdf", ".docx", ".xlsx",
}

# 文件大小上限：5MB
MAX_FILE_SIZE = 5 * 1024 * 1024

# 解析后文本长度上限（约 10 万字），防止前端渲染爆炸
MAX_CHARS = 100000
