# Load environment variables from .env if present (for local development)
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # python-dotenv is optional; skip if not installed

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import streamlit as st
import toml
from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session

# Import state management decorators
from src.svg_image_generator.streamlit_integration import (
    get_state_manager,
    loading_context,
    step_context,
    track_form_data,
    track_loading,
    track_step,
    track_validation_errors,
)

# Initialize state manager
state_manager = get_state_manager()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Runtime detection and self-identification
import sys

# Initialize safe feature integration
try:
    from src.svg_image_generator.safe_integration import (
        initialize_safe_features,
        safe_ui_state,
    )

    ui_state_manager = initialize_safe_features()
except Exception as e:
    print(f"⚠️ Feature integration failed: {e}")
    ui_state_manager = None

if __name__ == "__main__":
    # This is the main entry point
    st.set_page_config(
        page_title="SVG Generator with Snowflake Cortex", page_icon="🎨", layout="wide"
    )
else:
    # This is being imported as a module
    st.set_page_config(
        page_title="SVG Generator with Snowflake Cortex", page_icon="🎨", layout="wide"
    )

st.title("🎨 SVG Generator with Snowflake Cortex")
st.markdown(
    "Generate SVG files using Snowflake Cortex AI and save them to a Snowflake stage"
)


# Model Management Functions
def get_available_cortex_models(session: Session) -> List[str]:
    """Get list of available Cortex models for the current user using Snowpark operations"""
    try:
        logger.info("Discovering available Cortex models...")

        # Try to get available models from Snowflake
        # Note: This is a simplified approach - in production you might want to cache this
        # or use a more sophisticated model discovery mechanism

        # Common Cortex models - we'll validate these exist
        potential_models = [
            "claude-3-5-sonnet",
            "claude-3-7-sonnet",
            "claude-4-sonnet",
            "openai-gpt-4o",
            "openai-gpt-4o-mini",
            "llama-3-8b-instruct",
            "llama-3-70b-instruct",
            "mistral-7b-instruct",
            "mixtral-8x7b-instruct",
        ]

        available_models = []

        # Test each model with a simple query using Snowpark operations
        for model in potential_models:
            try:
                test_query = (
                    f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', 'Hello') as test"
                )
                result = session.sql(test_query).collect()
                if result and result[0][0]:
                    available_models.append(model)
                    logger.info(f"Model {model} is available")
                else:
                    logger.warning(f"Model {model} returned no result")
            except Exception as e:
                error_msg = str(e).lower()
                if "unknown model" in error_msg or "model not found" in error_msg:
                    logger.info(f"Model {model} is not available: {e}")
                else:
                    # Other errors might be temporary, so we'll include the model
                    available_models.append(model)
                    logger.warning(f"Model {model} had error but including it: {e}")

        if not available_models:
            # Fallback to basic models that should be available
            logger.warning("No models discovered, using fallback models")
            available_models = ["claude-3-5-sonnet"]

        logger.info(
            f"Found {len(available_models)} available models: {available_models}"
        )
        return available_models

    except Exception as e:
        logger.error(f"Error discovering Cortex models: {e}")
        # Return a safe fallback
        return ["claude-3-5-sonnet"]


def validate_cortex_model(session: Session, model: str) -> bool:
    """Validate that a specific Cortex model is available using Snowpark operations"""
    try:
        logger.info(f"Validating Cortex model: {model}")

        # Simple test query using Snowpark operations
        test_query = (
            f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', 'Test') as validation"
        )
        result = session.sql(test_query).collect()

        if result and result[0][0]:
            logger.info(f"Model {model} is valid")
            return True
        else:
            logger.warning(f"Model {model} returned no result")
            return False

    except Exception as e:
        error_msg = str(e).lower()
        if "unknown model" in error_msg or "model not found" in error_msg:
            logger.error(f"Model {model} is not available: {e}")
            return False
        else:
            # For any other error (including SQL errors), return False
            logger.error(f"Model {model} validation failed: {e}")
            return False


def safe_cortex_call(
    session: Session, model: str, prompt: str, operation_name: str = "Cortex operation"
) -> Optional[str]:
    """Safely make a Cortex call with comprehensive error handling using Snowpark operations"""
    try:
        logger.info(f"Making safe Cortex call for {operation_name} with model {model}")

        # Validate model first
        if not validate_cortex_model(session, model):
            raise ValueError(f"Model '{model}' is not available")

        # Make the Cortex call using Snowpark operations
        query = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', $${prompt}$$) as result"
        result = session.sql(query).collect()

        if result and result[0][0]:
            logger.info(f"{operation_name} completed successfully")
            return result[0][0]
        else:
            logger.warning(f"{operation_name} returned no result")
            return None

    except Exception as e:
        error_msg = str(e).lower()

        if "unknown model" in error_msg:
            logger.error(f"Model validation failed for {operation_name}: {e}")
            raise ValueError(
                f"Model '{model}' is not available in this Snowflake environment"
            )
        elif "external function" in error_msg:
            logger.error(f"External function error for {operation_name}: {e}")
            raise ValueError(f"Cortex service error: {e}")
        elif "timeout" in error_msg:
            logger.error(f"Timeout for {operation_name}: {e}")
            raise ValueError(f"Request timed out: {e}")
        elif "insufficient privileges" in error_msg:
            logger.error(f"Permission error for {operation_name}: {e}")
            raise ValueError(f"Insufficient privileges for Cortex operations: {e}")
        else:
            logger.error(f"Unexpected error for {operation_name}: {e}")
            raise ValueError(f"Cortex operation failed: {e}")


# Context Discovery Functions
def discover_user_context(session: Session) -> Dict:
    """Discover user's accessible databases, schemas, and stages using Snowpark operations"""
    try:
        logger.info("Discovering user context...")

        # Get current user role and permissions - use Snowpark operations
        current_role = session.sql("SELECT CURRENT_ROLE()").collect()[0][0]
        current_warehouse = session.sql("SELECT CURRENT_WAREHOUSE()").collect()[0][0]

        # Get accessible databases
        databases = get_accessible_databases(session)

        # Get current database and schema
        current_database = session.sql("SELECT CURRENT_DATABASE()").collect()[0][0]
        current_schema = session.sql("SELECT CURRENT_SCHEMA()").collect()[0][0]

        # Get schemas for current database
        schemas = (
            get_accessible_schemas(session, current_database)
            if current_database
            else []
        )

        # Get stages for current database/schema
        stages = (
            get_accessible_stages(session, current_database, current_schema)
            if current_database and current_schema
            else []
        )

        # Get available Cortex models
        available_models = get_available_cortex_models(session)

        context = {
            "role": current_role,
            "warehouse": current_warehouse,
            "current_database": current_database,
            "current_schema": current_schema,
            "accessible_databases": databases,
            "accessible_schemas": schemas,
            "accessible_stages": stages,
            "available_models": available_models,
        }

        logger.info(f"User context discovered: {context}")
        return context

    except Exception as e:
        logger.error(f"Error discovering user context: {e}")
        return {}


def get_accessible_databases(session: Session) -> List[str]:
    """Get list of databases accessible to current user using Snowpark operations"""
    try:
        logger.info("Discovering accessible databases...")
        result_df = session.sql("SHOW DATABASES")
        databases = result_df.select("name").filter("name IS NOT NULL").collect()
        database_names = [row[0] for row in databases if row[0]]
        logger.info(
            f"Found {len(database_names)} accessible databases: {database_names}"
        )
        return database_names
    except Exception as e:
        logger.error(f"Error getting accessible databases: {e}")
        return []


def get_accessible_schemas(session: Session, database: str) -> List[str]:
    """Get list of schemas accessible in given database using Snowpark operations"""
    try:
        logger.info(f"Discovering accessible schemas in database: {database}")
        result_df = session.sql(f"SHOW SCHEMAS IN DATABASE {database}")
        schemas = result_df.select("name").filter("name IS NOT NULL").collect()
        schema_names = [row[0] for row in schemas if row[0]]
        logger.info(
            f"Found {len(schema_names)} accessible schemas in {database}: {schema_names}"
        )
        return schema_names
    except Exception as e:
        logger.error(f"Error getting accessible schemas for {database}: {e}")
        return []


def get_accessible_stages(session: Session, database: str, schema: str) -> List[str]:
    """Get list of stages accessible in given database/schema using Snowpark operations"""
    try:
        logger.info(f"Discovering accessible stages in {database}.{schema}")
        result_df = session.sql(f"SHOW STAGES IN SCHEMA {database}.{schema}")
        stages = result_df.select("name").filter("name IS NOT NULL").collect()
        stage_names = [row[0] for row in stages if row[0]]
        logger.info(
            f"Found {len(stage_names)} accessible stages in {database}.{schema}: {stage_names}"
        )
        return stage_names
    except Exception as e:
        logger.error(f"Error getting accessible stages for {database}.{schema}: {e}")
        return []


def validate_user_permissions(
    session: Session, database: str, schema: str, stage: str
) -> bool:
    """Validate user has required permissions using Snowpark operations"""
    try:
        logger.info(f"Validating permissions for {database}.{schema}.{stage}")

        # Test database access
        session.sql(f"USE DATABASE {database}").collect()

        # Test schema access
        session.sql(f"USE SCHEMA {schema}").collect()

        # Test stage access (try to list contents)
        session.sql(f"LIST @{stage}").collect()

        logger.info("Permission validation successful")
        return True

    except Exception as e:
        logger.error(f"Permission validation failed: {e}")
        return False


def handle_context_errors(error: Exception) -> str:
    """Handle context-related errors gracefully"""
    error_msg = str(error).lower()

    if "insufficient privileges" in error_msg or "access denied" in error_msg:
        return "❌ Insufficient permissions for the selected context. Please contact your administrator."
    elif "does not exist" in error_msg:
        return "❌ The selected resource does not exist or is not accessible."
    elif "not found" in error_msg:
        return "❌ Resource not found. Please check your selection."
    else:
        return f"❌ Context error: {str(error)}"


# Enhanced Prompt Sandwich Functions
def refine_prompt_with_cortex(session: Session, raw_prompt: str, model: str) -> str:
    """Use Cortex to refine and structure the user prompt"""
    try:
        logger.info(f"[Prompt Sandwich] Refining prompt with {model}")

        refinement_prompt = f"""You are an expert SVG generation assistant. Given this user request, create a clear, specific prompt for generating an SVG:

User Request: {raw_prompt}

Generate a refined prompt that:
1. Is specific about visual elements (colors, shapes, layout)
2. Includes appropriate dimensions if mentioned
3. Specifies style preferences
4. Is optimized for SVG generation
5. Maintains the user's original intent

Return only the refined prompt, no explanations."""

        refined_prompt = safe_cortex_call(
            session, model, refinement_prompt, "Prompt refinement"
        )

        if refined_prompt:
            logger.info(f"[Prompt Sandwich] Refined prompt: {refined_prompt}")
            return refined_prompt.strip()
        else:
            logger.warning(
                "[Prompt Sandwich] Refinement returned no result, using original prompt"
            )
            return raw_prompt

    except Exception as e:
        logger.error(f"[Prompt Sandwich] Error refining prompt: {e}")
        st.warning(f"⚠️ Prompt refinement failed: {str(e)}. Using original prompt.")
        return raw_prompt


def generate_svg_with_refined_prompt(
    session: Session, refined_prompt: str, model: str
) -> str:
    """Generate SVG using the refined prompt"""
    try:
        logger.info(f"[Prompt Sandwich] Generating SVG with {model}")

        generation_prompt = f"""Generate a complete, valid SVG file based on this description: {refined_prompt}

Return only the SVG code starting with <svg> and ending with </svg>.
Make sure the SVG is properly formatted and includes all necessary attributes like viewBox, width, and height.
Do not include any explanatory text, just the SVG code."""

        svg_content = safe_cortex_call(
            session, model, generation_prompt, "SVG generation"
        )

        if svg_content:
            logger.info(f"[Prompt Sandwich] SVG generation completed")
            return svg_content
        else:
            raise ValueError("SVG generation returned no content")

    except Exception as e:
        logger.error(f"[Prompt Sandwich] Error generating SVG: {e}")
        raise e


def implement_prompt_sandwich(
    session: Session, user_prompt: str, model: str
) -> Tuple[str, str, str]:
    """Implement complete prompt sandwich approach"""
    try:
        logger.info(f"[Prompt Sandwich] Starting prompt sandwich for: {user_prompt}")

        # Step 1: Refine the prompt
        refined_prompt = refine_prompt_with_cortex(session, user_prompt, model)

        # Step 2: Generate SVG
        svg_content = generate_svg_with_refined_prompt(session, refined_prompt, model)

        return user_prompt, refined_prompt, svg_content

    except Exception as e:
        logger.error(f"[Prompt Sandwich] Error in prompt sandwich: {e}")
        raise e


# Safe decorators for UI state tracking
def safe_track_step(step_name: str):
    """Safe decorator for tracking steps with graceful degradation."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Set step if UI tracking is available
            if ui_state_manager and hasattr(ui_state_manager, "set_current_step"):
                try:
                    ui_state_manager.set_current_step(step_name)
                except Exception as e:
                    print(f"⚠️ UI state tracking failed: {e}")

            # Execute the function
            result = func(*args, **kwargs)
            return result

        return wrapper

    return decorator


def safe_track_loading(component: str):
    """Safe decorator for tracking loading states with graceful degradation."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Set loading state if UI tracking is available
            if ui_state_manager and hasattr(ui_state_manager, "set_loading_state"):
                try:
                    ui_state_manager.set_loading_state(component, True)
                except Exception as e:
                    print(f"⚠️ UI state tracking failed: {e}")

            try:
                # Execute the function
                result = func(*args, **kwargs)
                return result
            finally:
                # Clear loading state if UI tracking is available
                if ui_state_manager and hasattr(ui_state_manager, "set_loading_state"):
                    try:
                        ui_state_manager.set_loading_state(component, False)
                    except Exception as e:
                        print(f"⚠️ UI state tracking failed: {e}")

        return wrapper

    return decorator


# Get the active Snowflake session
@st.cache_resource
def get_session() -> Session:
    """Get Snowflake session - supports both SiS environment and local development"""
    # Tier 1: Active Session (Streamlit in Snowflake)
    try:
        logger.info("Auth Tier 1: Attempting to get active session (for SiS)...")
        session = get_active_session()
        st.info("🔗 Using active Snowflake session (Streamlit in Snowflake environment)")
        logger.info("Auth Tier 1 Succeeded: Using active Snowflake session.")
        return session
    except Exception as e1:
        logger.info(
            f"Auth Tier 1 Failed: get_active_session() not available. Error: {e1}"
        )

        # Tier 2: Connection Parameters (connections.toml)
        st.warning(
            "⚠️ Active session not available. Trying connection from `connections.toml`..."
        )
        try:
            logger.info("Auth Tier 2: Attempting to use `connections.toml`...")

            snowflake_conn_path = Path.home() / ".snowflake" / "connections.toml"
            if not snowflake_conn_path.exists():
                raise FileNotFoundError("connections.toml not found")

            config = toml.load(snowflake_conn_path)

            # Be robust: check for 'default' or 'connections.default'
            conn_params = {}
            if "default" in config:
                conn_params = config["default"]
            elif "connections" in config and "default" in config["connections"]:
                conn_params = config["connections"]["default"]

            if not conn_params:
                raise ValueError("No [default] profile found in connections.toml")

            logger.info(
                "Found [default] profile in `connections.toml`. Creating session."
            )
            session = Session.builder.configs(conn_params).create()
            st.success("✅ Connected to Snowflake using `connections.toml`.")
            logger.info("Auth Tier 2 Succeeded: Connected using `connections.toml`.")
            return session

        except Exception as conn_param_error:
            logger.warning(
                f"Auth Tier 2 Failed: Could not connect using `connections.toml`. Error: {conn_param_error}"
            )

            st.warning(
                f"""
            ⚠️ `connections.toml` authentication failed. Attempting local connection via environment variables...

            > **Hint:** Could not connect using `~/.snowflake/connections.toml`. Please ensure a `[default]` profile is correctly configured.
            > See browser console for detailed logs.
            """
            )

            # Tier 3: Environment Variables
            logger.info(
                "Auth Tier 3: Attempting to connect using environment variables..."
            )
            account = os.environ.get("SNOWFLAKE_ACCOUNT")
            user = os.environ.get("SNOWFLAKE_USER")
            password = os.environ.get("SNOWFLAKE_PASSWORD")
            warehouse = os.environ.get("SNOWFLAKE_WAREHOUSE")
            database = os.environ.get("SNOWFLAKE_DATABASE")
            schema = os.environ.get("SNOWFLAKE_SCHEMA")
            role = os.environ.get("SNOWFLAKE_ROLE")

            if not all([account, user, password, warehouse]):
                logger.critical(
                    "Auth Tier 3 Failed: Missing required environment variables."
                )
                st.error(
                    """
                ❌ Cannot connect to Snowflake. Missing required environment variables:

                **Required:**
                - SNOWFLAKE_ACCOUNT
                - SNOWFLAKE_USER
                - SNOWFLAKE_PASSWORD
                - SNOWFLAKE_WAREHOUSE

                **Optional:**
                - SNOWFLAKE_DATABASE
                - SNOWFLAKE_SCHEMA
                - SNOWFLAKE_ROLE

                **For local development, set these in your environment or create a .env file.**
                """
                )
                st.stop()

            try:
                logger.info(
                    "Auth Tier 3: Creating session with environment variables..."
                )
                session = Session.builder.configs(
                    {
                        "account": account,
                        "user": user,
                        "password": password,
                        "warehouse": warehouse,
                        "database": database,
                        "schema": schema,
                        "role": role,
                    }
                ).create()
                st.success("✅ Connected to Snowflake using environment credentials.")
                logger.info(
                    "Auth Tier 3 Succeeded: Connected using environment credentials."
                )
                return session
            except Exception as conn_error:
                logger.critical(
                    f"Auth Tier 3 Failed: Could not connect using environment variables. Error: {conn_error}"
                )
                st.error(
                    f"❌ All connection methods failed. Please check your configuration. Final error: {conn_error}"
                )
                st.stop()


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

# Sidebar for dynamic context configuration
st.sidebar.header("🔧 Context Configuration")

# Show feature status if UI state management is available
if ui_state_manager and hasattr(ui_state_manager, "get_status"):
    try:
        status = ui_state_manager.get_status()
        if status.get("available"):
            st.sidebar.success("✅ UI State Tracking: Enabled")
        else:
            st.sidebar.info("ℹ️ UI State Tracking: Disabled")
    except Exception as e:
        st.sidebar.info("ℹ️ UI State Tracking: Unavailable")

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
            # Track step if UI state management is available
            if ui_state_manager and hasattr(ui_state_manager, "set_current_step"):
                try:
                    ui_state_manager.set_current_step("svg_generation")
                except Exception as e:
                    print(f"⚠️ UI state tracking failed: {e}")

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
                # Track loading state if UI state management is available
                if ui_state_manager and hasattr(ui_state_manager, "set_loading_state"):
                    try:
                        ui_state_manager.set_loading_state("prompt_sandwich", True)
                    except Exception as e:
                        print(f"⚠️ UI state tracking failed: {e}")

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
                finally:
                    # Clear loading state if UI state management is available
                    if ui_state_manager and hasattr(
                        ui_state_manager, "set_loading_state"
                    ):
                        try:
                            ui_state_manager.set_loading_state("prompt_sandwich", False)
                        except Exception as e:
                            print(f"⚠️ UI state tracking failed: {e}")

            if svg_content:
                # Clean up the SVG content (remove any extra text)
                svg_content = svg_content.strip()
                if not svg_content.startswith("<svg"):
                    # Try to extract SVG from the response
                    start_idx = svg_content.find("<svg")
                    end_idx = svg_content.rfind("</svg>") + 6
                    if start_idx != -1 and end_idx != 5:
                        svg_content = svg_content[start_idx:end_idx]

                st.success("✅ SVG generated successfully!")

                # Display the generated SVG
                st.subheader("🎨 Generated SVG Preview:")
                try:
                    st.components.v1.html(svg_content, height=1000)
                except Exception:
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
                    # Track loading state if UI state management is available
                    if ui_state_manager and hasattr(
                        ui_state_manager, "set_loading_state"
                    ):
                        try:
                            ui_state_manager.set_loading_state("upload_to_stage", True)
                        except Exception as e:
                            print(f"⚠️ UI state tracking failed: {e}")

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

                        if stage_files:
                            st.subheader("📁 Files in Stage:")
                            for file_info in stage_files:
                                st.text(f"📄 {file_info[0]} ({file_info[1]} bytes)")

                    except Exception as e:
                        st.error(f"❌ Upload failed: {str(e)}")
                        # Try to clean up temp table if it exists
                        try:
                            session.sql(f"DROP TABLE IF EXISTS {temp_table}").collect()
                        except Exception:
                            pass  # Ignore cleanup errors
                    finally:
                        # Clear loading state if UI state management is available
                        if ui_state_manager and hasattr(
                            ui_state_manager, "set_loading_state"
                        ):
                            try:
                                ui_state_manager.set_loading_state(
                                    "upload_to_stage", False
                                )
                            except Exception as e:
                                print(f"⚠️ UI state tracking failed: {e}")

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

        if stage_files:
            st.subheader("📁 Files in Stage:")
            for file_info in stage_files:
                st.text(f"📄 {file_info[0]} ({file_info[1]} bytes)")
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


def main():
    """Main entry point for the SVG Generator Streamlit app."""
    # All the existing Streamlit UI code is already here
    # This function serves as the entry point for tools and scripts
    pass


if __name__ == "__main__":
    main()
