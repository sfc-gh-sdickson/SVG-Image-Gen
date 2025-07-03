# 🎨 SVG Image Generation with Snowflake Cortex

<img src="Snowflake_Logo.svg" width="200">

This project is a Streamlit application that runs within Snowflake (Streamlit in Snowflake - SiS) or locally for development. It provides a user-friendly interface to generate SVG (Scalable Vector Graphics) images from text-based descriptions using the power of Snowflake Cortex AI. Generated SVGs are then saved directly to a specified Snowflake stage.

## ✨ Features

-   **AI-Powered SVG Generation**: Utilizes Snowflake Cortex's generative AI models to create SVG images from natural language prompts.
-   **Model Selection**: Allows users to choose from various powerful AI models, including `openai-gpt-4.1`, `claude-4-sonnet`, `claude-3-7-sonnet`, and `claude-3-5-sonnet`.
-   **Direct-to-Stage Upload**: Seamlessly uploads the generated SVG files to a user-defined Snowflake stage.
-   **Interactive UI**: A simple and intuitive web interface built with Streamlit for easy interaction.
-   **Live SVG Preview**: Displays a preview of the generated SVG directly in the application before saving.
-   **Dynamic File Naming**: Automatically suggests a unique filename for each SVG based on the current timestamp.
-   **Session Context Awareness**: Displays the current Snowflake role, warehouse, database, and schema, and allows for context switching.
-   **Stage Management**: Includes functionality to list the current contents of the target stage.
-   **In-App Guidance**: Provides instructions, example prompts, and troubleshooting tips to enhance the user experience.
-   **Dual Environment Support**: Works both in Streamlit in Snowflake (SiS) and local development environments.

## ⚙️ Technologies Used

-   **Python**: The core programming language for the application.
-   **Streamlit**: For building the interactive web application.
-   **Snowflake**: The backend platform providing the compute, storage, and AI capabilities.
-   **Snowflake Cortex**: The intelligent, fully managed AI service used for SVG generation.
-   **Snowpark for Python**: For native data programmability and interaction with Snowflake.

## ✅ Requirements

To run this application, you will need:

-   A Snowflake account with **Snowflake Cortex** enabled.
-   Permissions to perform the following actions in your Snowflake environment:
    -   `CREATE STAGE` in a schema.
    -   `USE` a warehouse.
    -   Run queries against `SNOWFLAKE.CORTEX`.
    -   Upload files to a stage.

## 🚀 Installation and Running

### Option 1: Streamlit in Snowflake (SiS) - Production

This is the recommended approach for production use.

1.  **Create a new Streamlit App** in your Snowflake account.
2.  **Copy and paste** the content of the `SVG-Image-Gen.py` file into the editor.
3.  **Save and Run** the application. The app will use your active Snowflake session, so no additional login is required.

### Option 2: Local Development

For development, testing, and local use:

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd SVG-Image-Gen
   ```

2. **Install dependencies** (choose one option):

   **Option A: Using uv (recommended for faster, more reliable dependency management)**:
   ```bash
   # Install uv if you don't have it
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Install dependencies
   uv pip install -r requirements.txt
   ```

   **Option B: Using pip**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:

   You must set the following environment variables in your shell or environment before running the application. **Never create or use a .env or example .env file in the project directory.**

   **Required:**
   - `SNOWFLAKE_ACCOUNT` (e.g., xy12345.us-east-1)
   - `SNOWFLAKE_USER` (your Snowflake username)
   - `SNOWFLAKE_PASSWORD` (your Snowflake password)
   - `SNOWFLAKE_WAREHOUSE` (your Snowflake warehouse name)

   **Optional:**
   - `SNOWFLAKE_DATABASE` (your database name)
   - `SNOWFLAKE_SCHEMA` (your schema name)
   - `SNOWFLAKE_ROLE` (your role name)
   - `STREAMLIT_SERVER_PORT` (default: 8501)
   - `STREAMLIT_SERVER_ADDRESS` (default: 0.0.0.0)
   - `STREAMLIT_SERVER_HEADLESS` (default: true)

   Example (bash):
   ```bash
   export SNOWFLAKE_ACCOUNT=xy12345.us-east-1
   export SNOWFLAKE_USER=myuser
   export SNOWFLAKE_PASSWORD=mypassword123
   export SNOWFLAKE_WAREHOUSE=COMPUTE_WH
   # Optional:
   export SNOWFLAKE_DATABASE=MY_DB
   export SNOWFLAKE_SCHEMA=PUBLIC
   export SNOWFLAKE_ROLE=MY_ROLE
   ```

4. **Run the application**:
   ```bash
   streamlit run src/svg_image_generator/app.py
   ```

## 🔐 Authentication

The application supports a three-tier authentication system with graceful fallback:

### 1. Active Session (SiS Environment) - Primary
- Uses `get_active_session()` to automatically connect to your active Snowflake session
- No additional configuration required
- Inherits your current Snowflake context and permissions
- Ideal for Streamlit in Snowflake (SiS) environments

### 2. Connection Parameters (Various Snowflake Environments) - Secondary
- Uses `Session.builder.create()` to detect and use connection parameters
- Automatically detects connection parameters from:
  - Snowflake worksheets and native apps
  - Connection profiles and configurations
  - Snowflake CLI configuration
  - Other Snowflake environment configurations
- No manual configuration required when parameters are available

### 3. Environment Variables (Local Development) - Fallback
- Uses `Session.builder.configs()` with explicit environment variables
- Requires setting up environment variables in your shell or environment
- Supports all standard Snowflake authentication methods
- Ideal for local development and testing

The system automatically tries each method in order and falls back to the next if the previous fails, ensuring maximum compatibility across different Snowflake environments.

## 🧪 Testing

Run the test suite to verify functionality:

```bash
# Install development dependencies
# Option A: Using uv (recommended)
uv pip install -r requirements-dev.txt

# Option B: Using pip
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run specific test categories
pytest -m "unit"      # Unit tests only
pytest -m "integration"  # Integration tests only
pytest -m "snowflake"    # Snowflake-specific tests
```

### Type Checking and Stub Management

We use **mypy** for static type checking. If you encounter missing type stub errors:

```bash
# Automatic stub management (recommended)
python scripts/fix-missing-type-stubs.py

# Manual approach
mypy src/
# Add missing types-<package> to requirements-dev.txt
pip install -r requirements-dev.txt
```

For detailed development guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

## 📖 How to Use

1.  **Configure the Stage**: In the sidebar, specify the `Stage Name` where you want to save the SVG files. You can also optionally specify a different `Database` and `Schema`.
2.  **Describe the SVG**: In the main panel, enter a detailed text description of the SVG image you want to create. For best results, be specific about shapes, colors, and text.
3.  **Choose an AI Model**: Select one of the available Cortex AI models from the dropdown list.
4.  **Set a Filename**: A unique filename is generated for you, but you can change it if needed (do not include the `.svg` extension).
5.  **Generate and Upload**: Click the **"Generate SVG and Upload to Stage"** button.
    -   The application will call Snowflake Cortex to generate the SVG code.
    -   A preview of the generated SVG will be displayed.
    -   The SVG file will be uploaded to your specified Snowflake stage.
6.  **Retrieve Your File**: After a successful upload, the application will provide SQL commands that you can use in a Snowflake worksheet or SnowSQL to download the file or load it into a table.

### Example Prompts

-   "Create a modern logo with a gradient blue background, white geometric shapes, and the text 'TechCorp' in a clean sans-serif font."
-   "Generate a simple icon of a house with a red roof, white walls, and a brown door, sized 100x100."
-   "Make an abstract pattern with interconnected circles in various shades of green on a transparent background."

## 🔧 Troubleshooting

### Common Issues

**Authentication Errors**:
- **Active Session (SiS)**: Ensure you're logged into Snowflake and have an active session
- **Connection Parameters**: Verify connection parameters are properly configured in your Snowflake environment
- **Environment Variables**: Verify your environment variables are set correctly for local development
- **General**: The system automatically tries three authentication methods - check the status messages for which method succeeded or failed

**Private Key Authentication Gotcha**:
- **Error**: `Expected bytes or RSAPrivateKey, got <class 'NoneType'>`
- **Cause**: Snowflake Snowpark library expects private key content, not file paths
- **Solution**: Our application automatically detects `private_key_path` in `connections.toml` and loads the key file content
- **Configuration**: Ensure your `~/.snowflake/connections.toml` has the correct format:
  ```toml
  [default]
  account = "your-account"
  user = "your-user"
  private_key_path = "~/.ssh/snowflake_key.pem"
  private_key_passphrase = "optional-passphrase"  # if key is encrypted
  warehouse = "your-warehouse"
  ```
- **Testing**: Run the private key tests to verify your setup:
  ```bash
  uv run pytest tests/test_authentication.py -k "private_key" -v
  ```

**Connection Issues**:
- Check your Snowflake account identifier format
- Verify network connectivity to Snowflake
- Ensure your warehouse is running

**Permission Errors**:
- Verify you have `CREATE STAGE` permissions
- Check that your role has access to the specified database/schema
- Ensure Cortex AI access is enabled for your account

**Cortex AI Errors**:
- Confirm Cortex AI is enabled in your Snowflake account
- Check that your role has access to `SNOWFLAKE.CORTEX`
- Verify the selected model is available in your region

The application includes a "Troubleshooting" section that covers common issues such as:

-   Stage not found errors.
-   Cortex AI not being available.
-   Permission errors related to your Snowflake role.
-   File upload failures.

Refer to this section within the app for performance tips and solutions to common problems.

## 📄 License

Please add your own license information here. A common choice for open-source projects is the MIT License.

## 🛠️ Local Development with python-dotenv

This project supports [python-dotenv](https://pypi.org/project/python-dotenv/). If you have a `.env` file in your project root, environment variables will be loaded automatically when you run the app locally. **However, .env files must never be present in the project repository or committed to version control.**

To use for local, untracked development only:
1. Install dependencies (python-dotenv is included in requirements.txt)
2. Set environment variables in your shell, or create a `.env` file locally (never tracked or committed)
3. Run the app as usual

Example `.env` (for local, untracked use only):
```
SNOWFLAKE_ACCOUNT=xy12345.us-east-1
SNOWFLAKE_USER=myuser
SNOWFLAKE_PASSWORD=mypassword123
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
# Optional:
SNOWFLAKE_DATABASE=MY_DB
SNOWFLAKE_SCHEMA=PUBLIC
SNOWFLAKE_ROLE=MY_ROLE
```

**Never commit or share .env files. All environment variable documentation is in this README.**

### Environment Validation

The project includes tools to validate your environment setup:

```bash
# Validate environment variables
make validate-env

# Or run the validation script directly
python scripts/validate_env.py
```

This will check that all required environment variables are present and provide clear error messages if any are missing.

**Security Note**: Never commit `.env` files to version control. The project includes pre-commit hooks and `.gitignore` rules to prevent accidental credential exposure.

## 🔥 Real Connection Smoke Test

To verify your Snowflake connection profile in `~/.snowflake/connections.toml`, run the smoke test:

```bash
uv run pytest tests/test_authentication.py -k "test_smoke_connect_via_connections_toml" -v -s
```

By default, this uses the `[default]` profile. To use a different profile, set the environment variable:

```bash
export SNOWFLAKE_DEFAULT_CONNECTION_NAME=YOUR_PROFILE_NAME
uv run pytest tests/test_authentication.py -k "test_smoke_connect_via_connections_toml" -v -s
```

This will attempt to connect and run `SELECT 1` using the specified profile. The test will be skipped if the connection cannot be established or the profile is missing.

## Business Authority vs Platform Safety

**IMPORTANT**: This project follows a key principle: **The business owns the business**.

Snowflake (and many enterprise platforms) implement "safety" rules that are actually designed to protect the platform's liability, not your business interests. These rules can accidentally expand compliance/IT authority at the expense of business agility.

### Key Principles:
- **Platform safety ≠ Business authority**: Snowflake's grant/ownership rules protect Snowflake, not your business
- **Don't cede control by default**: Bean-counters, lawyers, and compliance should not run your business
- **Understand the difference**: Platform safety rules exist to protect the vendor's legal/operational risk
- **Business agility matters**: If you want to make money, you need to move fast and own your decisions

### The CISO Problem:
Platform safety rules can degrade the respect and power that accrues to a sensible CISO. If your CISO is just a cop enforcing vendor-imposed restrictions, how is that helpful? A good CISO should be a strategic business partner who understands risk in business terms, not just a rule enforcer for platform vendors.

### Examples in this codebase:
- The `REVOKE CURRENT GRANTS` clause in SQL scripts exists because Snowflake wants bulletproof audit trails
- Runtime detection prevents operations that could expose Snowflake to liability
- These are platform-protective measures, not user-protective features

**Bottom line**: Use these tools to maintain business control while working within platform constraints. Don't let compliance creep expand beyond what's actually necessary for your business success. And don't let platform rules turn your CISO into just another cop.
