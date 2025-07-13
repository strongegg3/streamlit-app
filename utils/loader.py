
from PyPDF2 import PdfReader
import docx

def load_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text  #text最后是一个字符串，包括pdf全部文字

def load_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])
    #[]列表表达式先将所有段落字符串提取出来，"\n".join()将列表合成一个大的字符串，字符串段落之间用换行号分割

def load_text(file):
    filename = file.name
    if filename.endswith(".pdf"):
        return load_text_from_pdf(file)
    elif filename.endswith(".docx"):
        return load_text_from_docx(file)
    elif filename.endswith(".txt"):
        return file.read().decode("utf-8")
    else:
        return "Unsupported format"

    #总之loader返回的都是字符串


