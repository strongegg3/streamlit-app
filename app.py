import streamlit as st
import os
from utils.rag_chain import build_vectorstore, load_vectorstore, create_qa_chain
import subprocess
import platform
from utils.loader import load_text

st.set_page_config(page_title="个人知识库 IMA", layout="wide")
#layout是页面布局，默认center，页面内容在中间，不太适合展示大段文本、表格、图谱；wide，内容铺满浏览器宽度，更适合数据分析、聊天窗口、文档问答界面
st.title("📚 我的智能知识库")

tab1, tab2 = st.tabs(["📤 上传文档", "🤖 问答"])  #tabs函数，创建一个选项卡（Tabs）组件，让页面可以分成多个标签页
DB_DIR = "knowledge_base"
os.makedirs(DB_DIR, exist_ok=True)
#makedirs函数，递归创建目录，也就是说，如果路径中的父目录不存在，会帮你一并创建
#path是要创建的目录名（字符串）// exist_ok=True：如果目录已经存在，不会报错；如果是 False，存在会抛异常

def open_file_in_browser(filepath):
    if platform.system() == "Windows":
        os.startfile(filepath)  # Windows 默认用关联程序打开
    elif platform.system() == "Darwin":  # macOS
        subprocess.run(["open", filepath])
    else:  # Linux
        subprocess.run(["xdg-open", filepath])

def build_base(uploaded_file,kb_name):
    #构建好文件夹
    kb_path = os.path.join(DB_DIR, kb_name)
    vector=os.path.join(kb_path,"vector")
    # os.path函数有很多下属函数，它能帮你拼接路径(.join)、判断路径是否存在(exists)、获取文件名(dirname)、获取文件夹路径(abspath)等
    # os.path.join(parent,child),作用是拼接路径，windows生成parents\child,并不生成文件夹，下面的makedirs才生成文件夹
    os.makedirs(kb_path, exist_ok=True)
    os.makedirs(vector, exist_ok=True)

    uploaded_file_path = os.path.join(kb_path, uploaded_file.name)
    with open(uploaded_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    text=load_text(uploaded_file)
    build_vectorstore(text, vector)


def show_base(base_name):
    # 显示该知识库文件列表
    st.markdown(f" 当前知识库 {base_name} 中的文件：")
    files = os.listdir(os.path.join(DB_DIR, base_name))
    for f in files:
        if f.endswith((".pdf", ".docx", ".txt")):
            file_full_path = os.path.join(DB_DIR, base_name, f)
            if st.button(f"📄 {f}"):
                open_file_in_browser(file_full_path)

def build_knowledge_base(uploaded_file_know,knowledge_base_name):
    if st.button("创建知识库"):
        with st.spinner("正在构建知识库..."):
            for f in uploaded_file_know:
                build_base(f, knowledge_base_name)
        st.success(f"✅ 知识库 {knowledge_base_name} 构建完成！")
        show_base(knowledge_base_name)


with tab1:
    if not os.listdir(DB_DIR):
        st.write("你还没有创建知识库哦~")
        uploaded_file = st.file_uploader("上传你的文档（PDF/DOCX/TXT）", type=["pdf", "docx", "txt"],
                                         accept_multiple_files=True)
        base_name = st.text_input("知识库名称")
        build_knowledge_base(uploaded_file,base_name)
        if st.checkbox("继续创建"):
            uploaded_file = st.file_uploader("上传你的文档（PDF/DOCX/TXT）", type=["pdf", "docx", "txt"],
                                             accept_multiple_files=True)
            base_name = st.text_input("知识库名称")
            build_knowledge_base(uploaded_file, base_name)

    else:
        for f in os.listdir(DB_DIR):
            st.subheader(f"{f}")
            show_base(f)
        if st.checkbox("继续创建"):
            uploaded_file = st.file_uploader("上传你的文档（PDF/DOCX/TXT）", type=["pdf", "docx", "txt"],
                                             accept_multiple_files=True)
            base_name = st.text_input("知识库名称")
            build_knowledge_base(uploaded_file, base_name)





with tab2:
    kb_list = [f for f in os.listdir(DB_DIR) if os.path.isdir(os.path.join(DB_DIR, f))]
    selected_kb = st.selectbox("选择知识库", kb_list)
    question = st.text_input("请输入你的问题")

    if selected_kb and question:
        db_path = os.path.join(DB_DIR, selected_kb,"vector")
        vs = load_vectorstore(db_path)
        qa = create_qa_chain(vs)
        with st.spinner("AI 回答中..."):
            answer = qa.run(question)
        st.markdown(f"**💬 回答：** {answer}")
