import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark import Session
import tempfile
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="SVG Generator with Snowflake Cortex",
    page_icon="🎨",
    layout="wide"
)

st.title("🎨 SVG Generator with Snowflake Cortex")
st.markdown("Generate SVG files using Snowflake Cortex AI and save them to a Snowflake stage")

# Get the active Snowflake session
@st.cache_resource
def get_session():
    return get_active_session()

try:
    session = get_session()
    st.success("✅ Connected to Snowflake using active session")
except Exception as e:
    st.error(f"❌ Failed to get active session: {str(e)}")
    st.stop()

# Sidebar for stage configuration
st.sidebar.header("Configuration")
stage_name = st.sidebar.text_input("Stage Name", value="SVG_STAGE", help="Stage where SVG files will be stored")

# Option to specify database and schema if different from current
current_db = st.sidebar.text_input("Database (optional)", placeholder="Leave empty to use current database")
current_schema = st.sidebar.text_input("Schema (optional)", placeholder="Leave empty to use current schema")

# Main interface
col1, col2 = st.columns([1, 1])

with col1:
    st.header("SVG Generation Settings")
    
    # SVG prompt input
    svg_prompt = st.text_area(
        "Describe the SVG you want to generate:",
        placeholder="e.g., Create a simple logo with a blue circle and white text saying 'Hello World'",
        height=100
    )
    
    # Model selection
    model = st.selectbox(
        "Cortex Model:",
        ["openai-gpt-4.1","claude-4-sonnet", "claude-3-7-sonnet","claude-3-5-sonnet"],
        index=0
    )
    
    # File naming
    filename = st.text_input(
        "SVG Filename (without extension):",
        value=f"generated_svg_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )

with col2:
    st.header("Session Information")
    
    # Display current session context
    try:
        current_role = session.sql("SELECT CURRENT_ROLE()").collect()[0][0]
        current_warehouse = session.sql("SELECT CURRENT_WAREHOUSE()").collect()[0][0]
        current_database = session.sql("SELECT CURRENT_DATABASE()").collect()[0][0]
        current_schema_name = session.sql("SELECT CURRENT_SCHEMA()").collect()[0][0]
        
        st.info(f"""
        **Current Context:**
        - Role: {current_role}
        - Warehouse: {current_warehouse}
        - Database: {current_database}
        - Schema: {current_schema_name}
        """)
    except Exception as e:
        st.warning(f"Could not retrieve session context: {str(e)}")

# Function to switch context if needed
def use_context():
    try:
        if current_db:
            session.sql(f"USE DATABASE {current_db}").collect()
        if current_schema:
            session.sql(f"USE SCHEMA {current_schema}").collect()
    except Exception as e:
        st.error(f"Failed to switch context: {str(e)}")
        return False
    return True

# Main generation and upload functionality
if st.button("Generate SVG and Upload to Stage", type="primary"):
    if not svg_prompt:
        st.error("Please provide an SVG description")
    else:
        try:
            # Switch context if needed
            if current_db or current_schema:
                if not use_context():
                    st.stop()
            
            # Prepare the Cortex prompt for SVG generation
            cortex_prompt = f"""Generate a complete, valid SVG file based on this description: {svg_prompt}

Return only the SVG code starting with <svg> and ending with </svg>. 
Make sure the SVG is properly formatted and includes all necessary attributes like viewBox, width, and height.
Do not include any explanatory text, just the SVG code."""

            # Generate SVG using Snowflake Cortex
            with st.spinner("Generating SVG with Cortex AI..."):
                cortex_query = f"""
                SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', $${cortex_prompt}$$) as svg_content
                """
                
                result = session.sql(cortex_query).collect()
                svg_content = result[0][0] if result else None
            
            if svg_content:
                # Clean up the SVG content (remove any extra text)
                svg_content = svg_content.strip()
                if not svg_content.startswith('<svg'):
                    # Try to extract SVG from the response
                    start_idx = svg_content.find('<svg')
                    end_idx = svg_content.rfind('</svg>') + 6
                    if start_idx != -1 and end_idx != 5:
                        svg_content = svg_content[start_idx:end_idx]
                
                st.success("SVG generated successfully!")
                
                # Display the generated SVG
                st.subheader("Generated SVG Preview:")
                try:
                    st.components.v1.html(svg_content, height=1000)
                except:
                    st.code(svg_content, language="xml")
                
                # Create stage if it doesn't exist
                with st.spinner("Preparing stage..."):
                    try:
                        session.sql(f"CREATE STAGE IF NOT EXISTS {stage_name}").collect()
                        st.info(f"Stage '{stage_name}' is ready")
                    except Exception as e:
                        if "already exists" not in str(e).lower():
                            st.warning(f"Stage creation warning: {str(e)}")
                
                # For Streamlit in Snowflake, we'll use a different approach for file upload
                # We'll store the SVG content in a temporary table and then copy to stage
                with st.spinner("Uploading SVG to Snowflake stage..."):
                    try:
                        # Create a temporary table to hold the SVG content
                        temp_table = f"TEMP_SVG_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        
                        # Create temporary table
                        session.sql(f"""
                        CREATE TRANSIENT TABLE {temp_table} (
                            content STRING
                        )
                        """).collect()
                        
                        # Insert SVG content
                        session.sql(f"""
                        INSERT INTO {temp_table} 
                        SELECT $${svg_content}$$
                        """).collect()
                        
                        # Copy from table to stage as a file
                        copy_query = f"""
                        COPY INTO @{stage_name}/{filename}.svg
                        FROM (
                            SELECT content FROM {temp_table}
                        )
                        FILE_FORMAT = (
                            TYPE = 'CSV' 
                            FIELD_DELIMITER = NONE 
                            RECORD_DELIMITER = NONE
                            SKIP_HEADER = 0
                        )
                        HEADER = FALSE
                        OVERWRITE = TRUE
                        """
                        
                        session.sql(copy_query).collect()
                        
                        # Clean up temporary table
                        session.sql(f"DROP TABLE {temp_table}").collect()
                        
                        st.success(f"✅ SVG file uploaded successfully to stage '{stage_name}' as '{filename}.svg'")
                        
                        # Show stage contents
                        stage_files = session.sql(f"LIST @{stage_name}").collect()
                        
                        if stage_files:
                            st.subheader("Files in Stage:")
                            for file_info in stage_files:
                                st.text(f"📄 {file_info[0]} ({file_info[1]} bytes)")
                    
                    except Exception as e:
                        st.error(f"Upload failed: {str(e)}")
                        # Try to clean up temp table if it exists
                        try:
                            session.sql(f"DROP TABLE IF EXISTS {temp_table}").collect()
                        except:
                            pass
                
                # Provide code to retrieve the file
                st.subheader("How to retrieve your SVG file:")
                st.code(f"""
-- Download the file from stage (from Snowflake CLI or other tools)
GET @{stage_name}/{filename}.svg file://path/to/local/directory/;

-- Or copy to a table for further processing
CREATE OR REPLACE TABLE svg_files (
    filename STRING,
    content STRING
);

COPY INTO svg_files
FROM (
    SELECT 
        '{filename}.svg' as filename,
        $1 as content
    FROM @{stage_name}/{filename}.svg
)
FILE_FORMAT = (TYPE = 'CSV' FIELD_DELIMITER = NONE RECORD_DELIMITER = NONE);

-- View the content directly
SELECT * FROM svg_files WHERE filename = '{filename}.svg';
                """, language="sql")
                
            else:
                st.error("Failed to generate SVG content")
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            with st.expander("Error Details"):
                st.write(str(e))

# Display current stage contents
st.markdown("---")
st.header("📁 Current Stage Contents")

if st.button("Refresh Stage Contents"):
    try:
        # Switch context if needed
        if current_db or current_schema:
            use_context()
            
        stage_files = session.sql(f"LIST @{stage_name}").collect()
        
        if stage_files:
            st.subheader(f"Files in '{stage_name}':")
            for file_info in stage_files:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.text(f"📄 {file_info[0]}")
                with col2:
                    st.text(f"{file_info[1]} bytes")
                with col3:
                    st.text(file_info[2])  # Last modified
        else:
            st.info("No files found in stage")
    except Exception as e:
        st.error(f"Could not list stage contents: {str(e)}")

# Instructions section
st.markdown("---")
st.header("📖 Instructions")
st.markdown("""
1. **Session Active**: This app uses your active Snowflake session - no additional login required
2. **Configure Stage**: Specify the stage name where SVG files will be stored
3. **Describe SVG**: Provide a detailed description of the SVG you want to generate
4. **Choose Model**: Select the Cortex AI model for generation
5. **Generate & Upload**: Click the main button to generate the SVG and upload it to your stage

**Requirements:**
- Running in Streamlit in Snowflake (SiS) environment
- Snowflake account with Cortex AI enabled
- Appropriate permissions to create stages and upload files

**Supported Models:**
- `claude-3-7-sonnet`: Anthropic Sonnet Model Version 3.7
- `claude-3-5-sonnet`: Anthropic Sonnet Model Version 3.5
- `claude-4-sonnet`: Anthropic flagship model Version 4
- `openai-gpt-4.1`: Open AI Flagship GPT Model Version 4.1
""")

# Tips section
with st.expander("💡 Tips for Better SVG Generation"):
    st.markdown("""
    - Be specific about colors, shapes, and layout
    - Mention desired dimensions if important
    - Include style preferences (modern, minimalist, etc.)
    - Specify text content and fonts if applicable
    - Consider mentioning accessibility features
    
    **Example prompts:**
    - "Create a modern logo with a gradient blue background, white geometric shapes, and the text 'TechCorp' in a clean sans-serif font"
    - "Generate a simple icon of a house with a red roof, white walls, and a brown door, sized 100x100"
    - "Make an abstract pattern with interconnected circles in various shades of green on a transparent background"
    """)

# Troubleshooting section
with st.expander("🔧 Troubleshooting"):
    st.markdown("""
    **Common Issues:**
    - **Stage not found**: Make sure you have CREATE STAGE privileges
    - **Cortex not available**: Ensure your account has Cortex AI enabled
    - **Permission errors**: Check your role has appropriate warehouse and schema access
    - **Upload failures**: Verify stage permissions and try refreshing the page
    
    **Performance Tips:**
    - Use smaller, more specific prompts for faster generation
    - Arctic model typically provides the best SVG generation quality
    - Consider the warehouse size for complex generations
    """)
