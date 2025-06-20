CREATE DATABASE IF NOT EXISTS CC_QUICKSTART_CORTEX_SEARCH_DOCS;
CREATE SCHEMA IF NOT EXISTS DATA;

CREATE SCHEMA IF NOT EXISTS APPS;


use database cc_quickstart_cortex_search_docs;
use schema data;

create or alter stage docs ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE') DIRECTORY = ( ENABLE = true );

-- Add Docs


ls @docs;
ls @CC_QUICKSTART_CORTEX_SEARCH_DOCS.DATA.DOCS;
describe stage CC_QUICKSTART_CORTEX_SEARCH_DOCS.DATA.DOCS;

create or alter TABLE DOCS_CHUNKS_TABLE ( 
    RELATIVE_PATH VARCHAR(16777216), -- Relative path to the PDF file
    SIZE NUMBER(38,0), -- Size of the PDF
    FILE_URL VARCHAR(16777216), -- URL for the PDF
    SCOPED_FILE_URL VARCHAR(16777216), -- Scoped url (you can choose which one to keep depending on your use case)
    CHUNK VARCHAR(16777216), -- Piece of text
    CHUNK_INDEX INTEGER, -- Index for the text
    CATEGORY VARCHAR(16777216), -- Will hold the document category to enable filtering
    COMPANY VARCHAR(16777216)
);

CREATE or replace TEMPORARY table RAW_TEXT AS
SELECT 
    RELATIVE_PATH,
    SIZE,
    FILE_URL,
    build_scoped_file_url(@docs, relative_path) as scoped_file_url,
    TO_VARCHAR (
        SNOWFLAKE.CORTEX.PARSE_DOCUMENT (
            '@docs',
            RELATIVE_PATH,
            {'mode': 'LAYOUT'} ):content
        ) AS EXTRACTED_LAYOUT 
FROM 
    DIRECTORY('@docs');
WHERE RELATIVE_PATH not in (select distinct RELATIVE_PATH from DOCS_CHUNKS_TABLE)


insert into docs_chunks_table (relative_path, size, file_url,
                            scoped_file_url, chunk, chunk_index)
    select relative_path, 
            size,
            file_url, 
            scoped_file_url,
            c.value::TEXT as chunk,
            c.INDEX::INTEGER as chunk_index         
    from raw_text,
        LATERAL FLATTEN( input => SNOWFLAKE.CORTEX.SPLIT_TEXT_RECURSIVE_CHARACTER (
              EXTRACTED_LAYOUT,
              'markdown',
              1512,
              256,
              ['\n\n', '\n', ' ', '']
           )) c;

-- select * from docs_chunks_table;

CREATE OR REPLACE TEMPORARY TABLE docs_categories AS WITH unique_documents AS (
  SELECT
    DISTINCT relative_path, chunk
  FROM
    docs_chunks_table
  WHERE 
    chunk_index = 0
  ),
 docs_category_cte AS (
  SELECT
    relative_path,
    TRIM(snowflake.cortex.CLASSIFY_TEXT (
      'Title:' || relative_path || 'Content:' || chunk, ['Annual Report', 'Action Plan', 'Metric', 'Data', 'Sustainability Report', 'Appendix']
     )['label'], '"') AS category,
    TRIM(snowflake.cortex.CLASSIFY_TEXT (
      'Title:' || relative_path || 'Content:' || chunk, [
                            'BHP',
                            'Commonwealth Bank of Australia',
                            'Coles Group',
                            'Wesfarmers',
                            'Woodside Energy',
                            'Woolworths Group',
                            'ANZ'
                ]
     )['label'], '"') AS company,
  FROM
    unique_documents
)
SELECT
  *
FROM
  docs_category_cte;


update docs_chunks_table 
  SET 
    category = docs_categories.category,
    company = docs_categories.company
  from docs_categories
  where  docs_chunks_table.relative_path = docs_categories.relative_path;

select * from docs_chunks_table;


create or replace CORTEX SEARCH SERVICE CC_SEARCH_SERVICE_CS
ON chunk
ATTRIBUTES category
warehouse = COMPUTE_WH
TARGET_LAG = '1 minute'
as (
    select chunk,
        chunk_index,
        relative_path,
        file_url,
        category,
        company
    from docs_chunks_table
);

use schema apps;
create or alter stage streamlit_esg_search_app ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE') DIRECTORY = ( ENABLE = true );


CREATE OR REPLACE STREAMLIT CC_CORTEX_SEARCH_APP
    FROM @CC_QUICKSTART_CORTEX_SEARCH_DOCS.APPS.STREAMLIT_ESG_SEARCH_APP
    QUERY_WAREHOUSE = COMPUTE_WH
    TITLE = 'Pure Streamlit ESG Search App'
    MAIN_FILE = 'pure_streamlit_esg_search_app.py';

-- CC_QUICKSTART_CORTEX_SEARCH_DOCS database and DATA
