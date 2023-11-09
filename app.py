import os
import streamlit as st
from dotenv import load_dotenv
from Vectara import Indexing, Searching  

# Load environment variables
load_dotenv()

# Create instances of Indexing and Searching classes
indexer = Indexing()
# .upload_file(
#             customer_id=int(os.getenv('CUSTOMER_ID')),
#             corpus_id=int(os.getenv('CORPUS_ID')),
#             idx_address=os.getenv('IDX_ADDRESS'),
#             uploaded_file=os.path.join(os.path.dirname(__file__),'.\vectara_employee_handbook-4524365135dc70a59977373c37601ad1.pdf'),
#             file_title="TestFile"
#         )
searcher = Searching()

# Set up the Streamlit interface
st.set_page_config(
    page_title="Vectara Retrieval Augmented System",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Financial Advising made Easier")

with st.sidebar:
    
    # st.info("Assetly.AI")
    st.image('./AssetlyImg.png')

with st.expander("Upload the Stock's 10K filings", expanded=True):
    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded_file = st.file_uploader("Select your 10k document", type=["txt", "pdf", "doc", "docx", "ppt", "pptx", "xls", "xlsx"])
        file_title = st.text_input("File Title", value="Name of your document", key='file_title')
    if st.button("Upload Document"):
        with st.spinner("AI processing the document..."):
            response, success = indexer.upload_file(
            customer_id=int(os.getenv('CUSTOMER_ID')),
            corpus_id=int(os.getenv('CORPUS_ID')),
            idx_address=os.getenv('IDX_ADDRESS'),
            uploaded_file=uploaded_file,
            file_title=file_title
        )
            if success:
                st.success("Document uploaded successfully!")
            else:
                st.error("Failed to upload document.")

with st.expander("Analyze your documents ", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        query_text = st.text_input("Get the stock info", key='query_text')
    with col2:
        num_results = st.slider("Number of Results", min_value=1, max_value=20, value=10, key='num_results')
    # with col3:
    #     summarizer_model = st.selectbox("Summary Model", ["vectara-summary-ext-v1.3.0", "vectara-summary-abstr-v1.3.0"], key='summarizer_model')
    #     response_lang = st.selectbox("Response Language", ["en", "fr", "es", "de", "it"], key='response_lang')
    if st.button("Go"):
        with st.spinner("Searching..."):
            texts = searcher.send_query(
                corpus_id=int(os.getenv('CORPUS_ID')),
                query_text=query_text,
                num_results=num_results,
                summarizer_prompt_name="vectara-summary-ext-v1.3.0",
                response_lang="en",
                max_summarized_results=5  
            )
            st.markdown('---')  
            st.markdown('### Output Answers')
            if texts:
                for text in texts:
                    st.markdown(f'- {text}')
            else:
                st.error("No results found.")