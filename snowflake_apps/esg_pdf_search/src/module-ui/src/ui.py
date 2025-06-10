import pandas as pd
import streamlit as st
from snowflake.snowpark.functions import call_udf, col
from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session
from snowflake.core import Root
import json

session = None
### Default Values
NUM_CHUNKS = 3 # Num-chunks provided as context. Play with this to check how it affects your accuracy

# service parameters
# TODO: Add the setup of the staged PDF's in provider scripts 
CORTEX_SEARCH_DATABASE = "CC_QUICKSTART_CORTEX_SEARCH_DOCS"
CORTEX_SEARCH_SCHEMA = "DATA"
CORTEX_SEARCH_SERVICE = "CC_SEARCH_SERVICE_CS"

# columns to query in the service
COLUMNS = [
   "chunk",
   "chunk_index",
   "relative_path",
   "category",
   "company"
]

def run():
   # Import python packages
   # Streamlit app testing framework requires imports to reside here
   # Streamlit app testing documentation: https://docs.streamlit.io/library/api-reference/app-testing

   pd.set_option("max_colwidth",None)



   session = get_active_session()
   root = Root(session)                         

   svc = root.databases[CORTEX_SEARCH_DATABASE].schemas[CORTEX_SEARCH_SCHEMA].cortex_search_services[CORTEX_SEARCH_SERVICE]
      
   ### Functions
     
def config_options():

    st.sidebar.selectbox('Select your model:',('mistral-large2', 'llama3.1-70b',
                        'llama3.1-8b', 'snowflake-arctic'), key="model_name")

    categories = session.sql("select category from docs_chunks_table group by category").collect()

    cat_list = ['ALL']
    for cat in categories:
        cat_list.append(cat.CATEGORY)
        cat_list = ['ALL']
    
    st.sidebar.selectbox('Select what report categories you are looking for', cat_list, key = "category_value")

    companies = session.sql("select company from docs_chunks_table group by company").collect()
    comp_list = ['ALL']
    for comp in companies:
        comp_list.append(comp.COMPANY)
        comp_list = ['ALL']

    st.sidebar.selectbox('Select what companies you are looking for', cat_list, key = "company_value")

    st.sidebar.expander("Session State").write(st.session_state)

def get_similar_chunks_search_service(query):
    if st.session_state.category_value == "ALL":
        response = svc.search(query, COLUMNS, limit=NUM_CHUNKS)
    else: 

        filter_obj = {"@and": [
            {"@eq": {"category": st.session_state.category_value} },
            {"@eq": {"company": st.session_state.company_value} }
        ]}
        response = svc.search(query, COLUMNS, filter=filter_obj, limit=NUM_CHUNKS)
        
        print("Overide Filtering not done yet")
        response = svc.search(query, COLUMNS, limit=NUM_CHUNKS)

    st.sidebar.json(response.json())
    return response.json()  

def create_prompt (myquestion):

    if st.session_state.rag == 1:
        prompt_context = get_similar_chunks_search_service(myquestion)
  
        prompt = f"""
           You are an investment manager that extracts information from comapny reports in the CONTEXT provided
           between <context> and </context> tags.
           When answering the question contained between <question> and </question> tags
           be concise and do not hallucinate. 
           If you don´t have the information just say so.
           Only anwer the question if you can extract it from the CONTEXT provideed.
           
           Do not mention the CONTEXT used in your answer.
    
           <context>          
           {prompt_context}
           </context>
           <question>  
           {myquestion}
           </question>
           Answer: 
           """

        json_data = json.loads(prompt_context)

        relative_paths = set(item['relative_path'] for item in json_data['results'])
        
    else:     
        prompt = f"""[0]
         'Question:  
           {myquestion} 
           Answer: '
           """
        relative_paths = "None"
            
    return prompt, relative_paths

def complete(myquestion):

    prompt, relative_paths =create_prompt (myquestion)
    cmd = """
            select snowflake.cortex.complete(?, ?) as response
          """
    
    df_response = session.sql(cmd, params=[st.session_state.model_name, prompt]).collect()
    return df_response, relative_paths

def worker():
    
    st.title(f":speech_balloon: Chat Document Assistant with Snowflake Cortex")
    st.write("This is the list of documents you already have and that will be used to answer your questions:")
    docs_available = session.sql("ls @docs").collect()
    list_docs = []
    for doc in docs_available:
        list_docs.append(doc["name"])
    st.dataframe(list_docs)

    config_options()

    st.session_state.rag = st.sidebar.checkbox('Use your own documents as context?', value=True)

    question = st.text_input("Enter question", placeholder="?", label_visibility="collapsed")

    if question:
        response, relative_paths = complete(question)
        res_text = response[0].RESPONSE
        st.markdown(res_text)

        if relative_paths != "None":
            with st.sidebar.expander("Related Documents"):
                for path in relative_paths:
                    cmd2 = f"select GET_PRESIGNED_URL(@docs, '{path}', 360) as URL_LINK from directory(@docs)"
                    df_url_link = session.sql(cmd2).to_pandas()
                    url_link = df_url_link._get_value(0,'URL_LINK')
        
                    display_url = f"Doc: [{path}]({url_link})"
                    st.sidebar.markdown(display_url)


if __name__ == '__main__':
   run()