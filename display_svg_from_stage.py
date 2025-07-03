import base64
import re

import streamlit as st
from snowflake.snowpark.context import get_active_session

# Get the current Snowpark session - works in both SiS and local dev
try:
    session = get_active_session()
except Exception:
    # Fallback to local development
    from src.svg_image_generator.session_manager import get_session as get_session_full

    session = get_session_full()

st.set_page_config(
    page_title="Dynamic SVG Display from Snowflake Stage", layout="centered"
)
st.title("Dynamic SVG Display from Snowflake Stage")
st.write(
    "Select your Snowflake database, schema, and stage to browse SVG files and view them."
)

# Initialize session state for selected full-size SVG
if "selected_full_svg_path" not in st.session_state:
    st.session_state["selected_full_svg_path"] = None

# --- Functions to fetch Snowflake metadata ---


@st.cache_data(
    ttl=3600
)  # Cache the results for an hour to avoid re-querying frequently
def get_databases():
    """Fetches all accessible databases."""
    try:
        databases_df = session.sql("SHOW DATABASES").collect()
        return [row["name"] for row in databases_df]
    except Exception as e:
        st.error(f"Error fetching databases: {e}")
        return []


@st.cache_data(ttl=3600)
def get_schemas(database_name):
    """Fetches schemas for a given database."""
    if not database_name:
        return []
    try:
        schemas_df = session.sql(f"SHOW SCHEMAS IN DATABASE {database_name}").collect()
        return [row["name"] for row in schemas_df]
    except Exception as e:
        st.error(f"Error fetching schemas for database '{database_name}': {e}")
        return []


@st.cache_data(ttl=3600)
def get_stages(database_name, schema_name):
    """Fetches stages for a given database and schema."""
    if not database_name or not schema_name:
        return []
    try:
        stages_df = session.sql(
            f"SHOW STAGES IN SCHEMA {database_name}.{schema_name}"
        ).collect()
        return [row["name"] for row in stages_df]
    except Exception as e:
        st.error(
            f"Error fetching stages for schema '{database_name}.{schema_name}': {e}"
        )
        return []


@st.cache_data(ttl=60)  # Cache file list for a shorter duration
def get_svg_file_paths_in_stage(database_name, schema_name, stage_name):
    """Fetches paths of SVG files from a given stage."""
    if not database_name or not schema_name or not stage_name:
        return []
    try:
        # Use the fully qualified stage name
        stage_path = f"@{database_name}.{schema_name}.{stage_name}"
        list_command = f"LIST {stage_path}"
        files_df = session.sql(list_command).collect()

        svg_full_paths = []
        for row in files_df:
            # The row['name'] contains the relative path within the stage
            relative_path = row["name"]

            # Include SVG files and extract just the filename for root-level access
            if relative_path.lower().endswith(".svg"):
                # Extract filename from path (e.g., "specs/Data_Share_Logo.svg" -> "Data_Share_Logo.svg")
                filename = relative_path.split("/")[-1]
                full_stage_path = f"{stage_path}/{filename}"
                svg_full_paths.append(full_stage_path)

        if not svg_full_paths:
            st.warning("⚠️ No SVG files found at root level")
            st.info(
                "💡 Upload SVG files to the root of the stage (not in subdirectories)"
            )
        return svg_full_paths
    except Exception as e:
        st.warning(
            f"Could not list files in stage '{database_name}.{schema_name}.{stage_name}': {e}"
        )
        st.info("Ensure the stage exists and you have `READ` permissions on it.")
        return []


def read_svg_content_from_stage(svg_file_path):
    """Reads SVG content from a given Snowflake stage path using the proven Python file API."""
    if not svg_file_path:
        return None
    try:
        # Ensure we have a fully qualified stage path
        if not svg_file_path.startswith("@"):
            st.error(f"Invalid stage path: {svg_file_path}. Must start with @")
            return None

        # Use the proven Python file API that works for root files
        with session.file.get_stream(svg_file_path) as f:
            svg_content = f.read().decode("utf-8")
            return svg_content

    except Exception as e:
        st.error(f"Error reading SVG file '{svg_file_path}': {e}")
        st.info(
            "Possible reasons: File does not exist, incorrect path, or insufficient permissions."
        )
        return None


# --- Streamlit UI for selection ---

# Store previous selections to detect changes
prev_selected_database = st.session_state.get("prev_selected_database", None)
prev_selected_schema = st.session_state.get("prev_selected_schema", None)
prev_selected_stage = st.session_state.get("prev_selected_stage", None)


# Select Database
all_databases = get_databases()
try:
    current_db = session.get_current_database()
    current_db_index = (
        all_databases.index(current_db) if current_db in all_databases else 0
    )
except Exception:
    current_db_index = 0

selected_database = st.selectbox(
    "Select Database",
    all_databases,
    index=current_db_index,
    key="db_select",  # Add a key for consistent state management
)

# Select Schema (dependent on selected_database)
selected_schemas = []
if selected_database:
    selected_schemas = get_schemas(selected_database)
try:
    current_schema = session.get_current_schema()
    current_schema_index = (
        selected_schemas.index(current_schema)
        if current_schema in selected_schemas
        else 0
    )
except Exception:
    current_schema_index = 0

selected_schema = st.selectbox(
    "Select Schema",
    selected_schemas,
    index=current_schema_index,
    key="schema_select",  # Add a key
)

# Select Stage (dependent on selected_database and selected_schema)
selected_stages = []
if selected_database and selected_schema:
    selected_stages = get_stages(selected_database, selected_schema)

selected_stage = st.selectbox(
    "Select Stage", selected_stages, key="stage_select"  # Add a key
)

# Check if any of the selection boxes changed
if (
    selected_database != prev_selected_database
    or selected_schema != prev_selected_schema
    or selected_stage != prev_selected_stage
):
    st.session_state[
        "selected_full_svg_path"
    ] = None  # Clear full size selection on stage change

# Update previous selections in session state
st.session_state["prev_selected_database"] = selected_database
st.session_state["prev_selected_schema"] = selected_schema
st.session_state["prev_selected_stage"] = selected_stage


# --- Display Thumbnails and Radio Buttons ---
svg_file_paths = []
if selected_database and selected_schema and selected_stage:
    svg_file_paths = get_svg_file_paths_in_stage(
        selected_database, selected_schema, selected_stage
    )

# Create a mapping from simple file name to full file path for the radio button
file_name_to_path_map = {}
for path in svg_file_paths:
    if path.startswith("@"):
        file_name_to_path_map[path.split("/")[-1]] = path
    else:
        st.warning(f"Skipping invalid SVG path (not a stage path): {path}")
radio_options = list(file_name_to_path_map.keys())

if radio_options:
    st.subheader("Available SVG Files:")
    # Display thumbnails in columns
    num_columns = 4
    cols = st.columns(num_columns)

    # Read and display thumbnails. This loop runs every time.
    for i, file_name in enumerate(radio_options):
        file_path = file_name_to_path_map[file_name]
        with cols[i % num_columns]:  # Place in the current column
            st.markdown(f"**{file_name}**")
            svg_content_thumbnail = read_svg_content_from_stage(file_path)
            if svg_content_thumbnail:
                # Display thumbnail with a fixed small width
                try:
                    st.image(
                        svg_content_thumbnail,
                        width=100,
                        caption="",
                        use_container_width=False,
                    )
                except Exception as e:
                    if "DOCTYPE" in str(e) or "DOCTYPE" in svg_content_thumbnail:
                        st.warning(
                            "⚠️ SVG has DOCTYPE header - not supported by Streamlit"
                        )
                    else:
                        st.error(f"Error displaying SVG: {e}")
            else:
                st.write("Thumbnail not loaded.")

    st.markdown("---")

    # Radio button for selecting the full-size image
    selected_file_name_for_full_view = st.radio(
        "Select an SVG file to view full size:",
        radio_options,
        index=radio_options.index(
            st.session_state["selected_full_svg_path"].split("/")[-1]
        )
        if st.session_state["selected_full_svg_path"]
        and st.session_state["selected_full_svg_path"].split("/")[-1] in radio_options
        else 0,
        key="full_svg_radio",
    )

    # Update the session state with the full path of the selected radio option
    if selected_file_name_for_full_view:
        st.session_state["selected_full_svg_path"] = file_name_to_path_map[
            selected_file_name_for_full_view
        ]

else:
    st.info("No SVG files found in the selected stage, or stage not selected.")
    st.session_state[
        "selected_full_svg_path"
    ] = None  # Ensure full view is cleared if no files


# --- Display Full-Size SVG ---
if st.session_state["selected_full_svg_path"]:
    st.subheader("Full-Size SVG Display:")
    full_svg_content = read_svg_content_from_stage(
        st.session_state["selected_full_svg_path"]
    )
    if full_svg_content:
        file_name_full = st.session_state["selected_full_svg_path"].split("/")[-1]
        st.header(f"Displaying: {file_name_full}")

        # Option A: Using st.image (recommended)
        st.subheader("Using `st.image()`")
        try:
            st.image(
                full_svg_content,
                caption=f"Full size SVG: {file_name_full}",
                use_container_width=True,
            )
        except Exception as e:
            if "DOCTYPE" in str(e) or "DOCTYPE" in full_svg_content:
                st.warning("⚠️ SVG has DOCTYPE header - not supported by Streamlit")
            else:
                st.error(f"Error displaying SVG: {e}")

        st.markdown("---")

        # Option B: Using st.markdown with unsafe_allow_html=True
        st.subheader("Using `st.markdown(unsafe_allow_html=True)`")
        try:
            b64_svg_full = base64.b64encode(full_svg_content.encode("utf-8")).decode(
                "utf-8"
            )
            html_string_full = f'<img src="data:image/svg+xml;base64,{b64_svg_full}" style="max-width: 100%; height: auto;">'
            st.markdown(html_string_full, unsafe_allow_html=True)
            st.caption(f"Full size SVG with st.markdown: {file_name_full}")
        except Exception as e:
            if "DOCTYPE" in str(e) or "DOCTYPE" in full_svg_content:
                st.warning("⚠️ SVG has DOCTYPE header - not supported by Streamlit")
            else:
                st.error(f"Error displaying SVG: {e}")

        # Add a button to clear the full-size selection
        st.button(
            "Clear Full Size View",
            on_click=lambda: st.session_state.update(selected_full_svg_path=None),
        )
    else:
        st.warning("Failed to load the selected full-size SVG for full-size display.")
else:
    st.info(
        "Select a stage, and then select an SVG file from the list to see the full image."
    )
