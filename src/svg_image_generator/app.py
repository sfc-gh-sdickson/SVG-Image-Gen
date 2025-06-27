"""
Main Streamlit application for SVG Image Generator.

This module provides the Streamlit interface for the SVG generation application,
using the modular components from the package.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

# Add the src directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import our modular components
from svg_image_generator import (
    discover_user_context,
    get_accessible_schemas,
    get_accessible_stages,
    get_available_cortex_models,
    get_session,
    implement_prompt_sandwich,
    validate_cortex_model,
    validate_user_permissions,
)

# Set up comprehensive logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Runtime patch logging system
class RuntimePatchLogger:
    """Logs any runtime patches, workarounds, or non-standard behavior"""

    @staticmethod
    def log_patch(
        component: str, description: str, impact: str = "Low", guidance: str = ""
    ):
        """Log a runtime patch with detailed information"""
        patch_msg = f"""
🔧 RUNTIME PATCH APPLIED:
Component: {component}
Description: {description}
Impact: {impact}
Guidance: {guidance or "Contact maintainers if this patch causes issues"}
Timestamp: {datetime.now().isoformat()}
        """
        logger.warning(patch_msg)
        st.warning(f"⚠️ Runtime patch applied: {description}")


# Initialize patch logger
patch_logger = RuntimePatchLogger()

# Page configuration
st.set_page_config(
    page_title="SVG Generator with Snowflake Cortex", page_icon="🎨", layout="wide"
)

st.title("🎨 SVG Generator with Snowflake Cortex")
st.markdown(
    "Generate SVG files using Snowflake Cortex AI and save them to a Snowflake stage"
)

# Get the active Snowflake session
try:
    session = get_session()
except Exception as e:
    st.error(f"❌ Failed to get session: {str(e)}")
    st.stop()

# Discover user context
try:
    user_context = discover_user_context(session)
    if not user_context:
        st.error("❌ Failed to discover user context")
        st.stop()
except Exception as e:
    st.error(f"❌ Error discovering user context: {str(e)}")
    st.stop()

# Get available models and add to context
try:
    available_models = get_available_cortex_models(session)
    user_context["available_models"] = available_models
except Exception as e:
    logger.warning(f"Could not discover Cortex models: {e}")
    patch_logger.log_patch(
        "Model Discovery",
        f"Failed to discover Cortex models: {e}",
        "Medium",
        "Using fallback models. Check Cortex availability and permissions.",
    )
    user_context["available_models"] = ["claude-3-5-sonnet"]

# Sidebar for dynamic context configuration
st.sidebar.header("🔧 Context Configuration")

# Dynamic Database Dropdown
available_databases = user_context.get("accessible_databases", [])
current_database = user_context.get("current_database", "")

if not available_databases:
    st.sidebar.error("❌ No accessible databases found")
    st.stop()

selected_database = st.sidebar.selectbox(
    "📁 Database",
    options=available_databases,
    index=available_databases.index(current_database)
    if current_database in available_databases
    else 0,
    help="Select the database where you want to work",
)

# Dynamic Schema Dropdown
available_schemas = []
if selected_database:
    try:
        available_schemas = get_accessible_schemas(session, selected_database)
    except Exception as e:
        st.sidebar.error(f"❌ Error loading schemas: {str(e)}")
        available_schemas = []

current_schema = user_context.get("current_schema", "")
if available_schemas:
    selected_schema = st.sidebar.selectbox(
        "📂 Schema",
        options=available_schemas,
        index=available_schemas.index(current_schema)
        if current_schema in available_schemas
        else 0,
        help="Select the schema within the database",
    )
else:
    st.sidebar.warning("⚠️ No accessible schemas found")
    selected_schema = ""

# Dynamic Stage Dropdown
available_stages = []
if selected_database and selected_schema:
    try:
        available_stages = get_accessible_stages(
            session, selected_database, selected_schema
        )
    except Exception as e:
        st.sidebar.error(f"❌ Error loading stages: {str(e)}")
        available_stages = []

# Add option to create new stage
stage_options = available_stages + ["Create New Stage"]
selected_stage = st.sidebar.selectbox(
    "📦 Stage",
    options=stage_options,
    index=0,
    help="Select an existing stage or create a new one",
)

# Handle new stage creation
new_stage_name = ""
if selected_stage == "Create New Stage":
    new_stage_name = st.sidebar.text_input(
        "New Stage Name", value="SVG_STAGE", help="Enter name for the new stage"
    )
    selected_stage = new_stage_name

# Main interface
col1, col2 = st.columns([1, 1])

with col1:
    st.header("🎨 SVG Generation Settings")

    # SVG prompt input
    svg_prompt = st.text_area(
        "Describe the SVG you want to generate:",
        placeholder="e.g., Create a simple logo with a blue circle and white text saying 'Hello World'",
        height=100,
    )

    # Dynamic Model Selection
    available_models = user_context.get("available_models", ["claude-3-5-sonnet"])
    if not available_models:
        st.error("❌ No Cortex models available")
        st.stop()

    model = st.selectbox(
        "🤖 Cortex Model:",
        options=available_models,
        index=0,
        help="Select the Cortex AI model for generation",
    )

    # File naming
    filename = st.text_input(
        "📝 SVG Filename (without extension):",
        value=f"generated_svg_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    )

with col2:
    st.header("📊 Session Information")

    # Display current session context
    try:
        current_role = session.sql("SELECT CURRENT_ROLE()").collect()[0][0]
        current_warehouse = session.sql("SELECT CURRENT_WAREHOUSE()").collect()[0][0]

        st.info(
            f"""
        **Current Context:**
        - Role: {current_role}
        - Warehouse: {current_warehouse}
        - Selected Database: {selected_database}
        - Selected Schema: {selected_schema}
        - Selected Stage: {selected_stage}
        - Available Models: {len(available_models)} models
        """
        )
    except Exception as e:
        st.warning(f"Could not retrieve session context: {str(e)}")


# Function to switch context if needed
def use_context() -> bool:
    try:
        if selected_database:
            session.sql(f"USE DATABASE {selected_database}").collect()
        if selected_schema:
            session.sql(f"USE SCHEMA {selected_schema}").collect()
        return True
    except Exception as e:
        st.error(f"Failed to switch context: {str(e)}")
        return False


# Main generation and upload functionality
if st.button("🚀 Generate SVG and Upload to Stage", type="primary"):
    if not svg_prompt:
        st.error("Please provide an SVG description")
    elif not selected_stage:
        st.error("Please select a stage")
    else:
        try:
            # Switch context if needed
            if not use_context():
                st.stop()

            # Validate permissions
            if not validate_user_permissions(
                session, selected_database, selected_schema, selected_stage
            ):
                st.error("❌ Insufficient permissions for the selected context")
                st.stop()

            # Validate model before proceeding
            if not validate_cortex_model(session, model):
                st.error(f"❌ Model '{model}' is not available in this environment")
                st.stop()

            # Implement Prompt Sandwich
            with st.spinner("🔄 Implementing prompt sandwich approach..."):
                try:
                    raw_prompt, refined_prompt, svg_content = implement_prompt_sandwich(
                        session, svg_prompt, model
                    )

                    # Display the prompt sandwich process
                    st.subheader("🔍 Prompt Sandwich Process")

                    with st.expander("📝 Original Prompt"):
                        st.write(raw_prompt)

                    with st.expander("✨ Refined Prompt"):
                        st.write(refined_prompt)

                except Exception as e:
                    st.error(f"❌ Error in prompt sandwich: {str(e)}")
                    st.stop()

            if svg_content:
                # Clean up the SVG content (remove any extra text)
                svg_content = svg_content.strip()
                if not svg_content.startswith("<svg"):
                    # Try to extract SVG from the response
                    start_idx = svg_content.find("<svg")
                    end_idx = svg_content.rfind("</svg>") + 6
                    if start_idx != -1 and end_idx != 5:
                        svg_content = svg_content[start_idx:end_idx]
                        patch_logger.log_patch(
                            "SVG Content Extraction",
                            "Extracted SVG content from non-standard response format",
                            "Low",
                            "This patch handles cases where Cortex returns extra text around SVG content",
                        )

                st.success("✅ SVG generated successfully!")

                # Display the generated SVG
                st.subheader("🎨 Generated SVG Preview:")
                try:
                    st.components.v1.html(svg_content, height=1000)
                except Exception as e:
                    logger.warning(f"Could not render SVG preview: {e}")
                    st.code(svg_content, language="xml")

                # Create stage if it doesn't exist
                with st.spinner("📦 Preparing stage..."):
                    try:
                        session.sql(
                            f"CREATE STAGE IF NOT EXISTS {selected_stage}"
                        ).collect()
                        st.info(f"✅ Stage '{selected_stage}' is ready")
                    except Exception as e:
                        if "already exists" not in str(e).lower():
                            st.warning(f"⚠️ Stage creation warning: {str(e)}")

                # Upload SVG to stage
                with st.spinner("📤 Uploading SVG to Snowflake stage..."):
                    try:
                        # Create a temporary table to hold the SVG content
                        temp_table = (
                            f"TEMP_SVG_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        )

                        # Create temporary table
                        session.sql(
                            f"""
                        CREATE TRANSIENT TABLE {temp_table} (
                            content STRING
                        )
                        """
                        ).collect()

                        # Insert SVG content
                        session.sql(
                            f"""
                        INSERT INTO {temp_table}
                        SELECT $${svg_content}$$
                        """
                        ).collect()

                        # Copy from table to stage as a file
                        copy_query = f"""
                        COPY INTO @{selected_stage}/{filename}.svg
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

                        st.success(
                            f"✅ SVG file uploaded successfully to stage "
                            f"'{selected_stage}' as '{filename}.svg'"
                        )

                        # Show stage contents
                        stage_files = session.sql(f"LIST @{selected_stage}").collect()

                        if len(stage_files) > 0:
                            st.subheader("📁 Files in Stage:")
                            for file in stage_files:
                                st.text(f"📄 {file['name']} ({file['size']} bytes)")

                    except Exception as e:
                        st.error(f"❌ Upload failed: {str(e)}")
                        # Try to clean up temp table if it exists
                        try:
                            session.sql(f"DROP TABLE IF EXISTS {temp_table}").collect()
                        except Exception:
                            pass  # Ignore cleanup errors

                # Provide code to retrieve the file
                st.subheader("💻 How to retrieve your SVG file:")
                st.code(
                    f"""
-- Download the file from stage (from Snowflake CLI or other tools)
GET @{selected_stage}/{filename}.svg file://path/to/local/directory/;

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
    FROM @{selected_stage}/{filename}.svg
)
FILE_FORMAT = (TYPE = 'CSV' FIELD_DELIMITER = NONE RECORD_DELIMITER = NONE);

-- View the content directly
SELECT * FROM svg_files WHERE filename = '{filename}.svg';
                """,
                    language="sql",
                )

            else:
                st.error("❌ Failed to generate SVG content")

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            with st.expander("🔍 Error Details"):
                st.write(str(e))

# Display current stage contents
st.markdown("---")
st.header("📁 Current Stage Contents")

if st.button("🔄 Refresh Stage Contents"):
    try:
        # Switch context if needed
        if not use_context():
            st.stop()

        stage_files = session.sql(f"LIST @{selected_stage}").collect()

        if len(stage_files) > 0:
            st.subheader(f"📁 Files in '{selected_stage}':")
            for file in stage_files:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.text(f"📄 {file['name']}")
                with col2:
                    st.text(f"{file['size']} bytes")
                with col3:
                    st.text(file["last_modified"])  # Last modified
        else:
            st.info("📭 No files found in stage")
    except Exception as e:
        st.error(f"❌ Could not list stage contents: {str(e)}")

# Instructions section
st.markdown("---")
st.header("📖 Instructions")
st.markdown(
    """
1. **🔧 Context Setup**: Select your database, schema, and stage from the dropdowns
2. **🎨 Describe SVG**: Provide a detailed description of the SVG you want to generate
3. **🤖 Choose Model**: Select the Cortex AI model for generation
4. **📝 Name File**: Specify the filename for your SVG
5. **🚀 Generate & Upload**: Click the main button to generate the SVG and upload it to your stage

**Requirements:**
- Running in Streamlit in Snowflake (SiS) environment
- Snowflake account with Cortex AI enabled
- Appropriate permissions to access databases, schemas, and stages

**Available Models:**
The dropdown shows only models available in your Snowflake environment.
"""
)

# Tips section
with st.expander("💡 Tips for Better SVG Generation"):
    st.markdown(
        """
    - Be specific about colors, shapes, and layout
    - Mention desired dimensions if important
    - Include style preferences (modern, minimalist, etc.)
    - Specify text content and fonts if applicable
    - Consider mentioning accessibility features

    **Example prompts:**
    - "Create a modern logo with a gradient blue background, white geometric shapes, and the text 'TechCorp' in a clean sans-serif font"
    - "Generate a simple icon of a house with a red roof, white walls, and a brown door, sized 100x100"
    - "Make an abstract pattern with interconnected circles in various shades of green on a transparent background"
    """
    )

# Troubleshooting section
with st.expander("🔧 Troubleshooting"):
    st.markdown(
        """
    **Common Issues:**
    - **Stage not found**: Make sure you have CREATE STAGE privileges
    - **Cortex not available**: Ensure your account has Cortex AI enabled
    - **Model not available**: The model dropdown shows only available models
    - **Permission errors**: Check your role has appropriate warehouse and schema access
    - **Upload failures**: Verify stage permissions and try refreshing the page

    **Performance Tips:**
    - Use smaller, more specific prompts for faster generation
    - Different models may have different performance characteristics
    - Consider the warehouse size for complex generations
    """
    )
