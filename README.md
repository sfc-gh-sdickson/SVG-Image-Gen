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

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   # Copy the example configuration
   cp config.example.env .env
   
   # Edit .env with your Snowflake credentials
   nano .env
   ```

4. **Configure your Snowflake credentials** in `.env`:
   ```bash
   # Required
   SNOWFLAKE_ACCOUNT=your-account-identifier
   SNOWFLAKE_USER=your-username
   SNOWFLAKE_PASSWORD=your-password
   SNOWFLAKE_WAREHOUSE=your-warehouse-name
   
   # Optional
   SNOWFLAKE_DATABASE=your-database-name
   SNOWFLAKE_SCHEMA=your-schema-name
   SNOWFLAKE_ROLE=your-role-name
   ```

5. **Run the application**:
   ```bash
   streamlit run SVG-Image-Gen.py
   ```

## 🔐 Authentication

The application supports two authentication modes:

### SiS Environment (Automatic)
- Uses `get_active_session()` to automatically connect to your active Snowflake session
- No additional configuration required
- Inherits your current Snowflake context and permissions

### Local Environment (Manual)
- Uses environment variables for connection parameters
- Requires setting up `.env` file with your Snowflake credentials
- Supports all standard Snowflake authentication methods

## 🧪 Testing

Run the test suite to verify functionality:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run specific test categories
pytest -m "unit"      # Unit tests only
pytest -m "integration"  # Integration tests only
pytest -m "snowflake"    # Snowflake-specific tests
```

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
- **SiS Environment**: Ensure you're logged into Snowflake and have an active session
- **Local Environment**: Verify your `.env` file contains correct credentials

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

This project supports [python-dotenv](https://pypi.org/project/python-dotenv/). If you have a `.env` file in your project root, environment variables will be loaded automatically when you run the app locally. This is the recommended way to manage secrets and configuration for local development.

To use:
1. Install dependencies (python-dotenv is included in requirements.txt)
2. Copy `config.example.env` to `.env` and fill in your credentials
3. Run the app as usual

```bash
cp config.example.env .env
streamlit run SVG-Image-Gen.py
```
