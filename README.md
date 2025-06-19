# 🎨 SVG Image Generation with Snowflake Cortex

<img src="Snowflake_Logo.svg" width="200">

This project is a Streamlit application that runs within Snowflake (Streamlit in Snowflake - SiS). It provides a user-friendly interface to generate SVG (Scalable Vector Graphics) images from text-based descriptions using the power of Snowflake Cortex AI. Generated SVGs are then saved directly to a specified Snowflake stage.

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

## ⚙️ Technologies Used

-   **Python**: The core programming language for the application.
-   **Streamlit**: For building the interactive web application.
-   **Snowflake**: The backend platform providing the compute, storage, and AI capabilities.
-   **Snowflake Cortex**: The intelligent, fully managed AI service used for SVG generation.
-   **Snowpark for Python**: For native data programmability and interaction with Snowflake.

## ✅ Requirements

To run this application, you will need:

-   A Snowflake account with **Streamlit in Snowflake (SiS)** and **Snowflake Cortex** enabled.
-   Permissions to perform the following actions in your Snowflake environment:
    -   `CREATE STAGE` in a schema.
    -   `USE` a warehouse.
    -   Run queries against `SNOWFLAKE.CORTEX`.
    -   Upload files to a stage.

## 🚀 Installation and Running

This application is designed to run as a Streamlit app within Snowflake.

1.  **Create a new Streamlit App** in your Snowflake account.
2.  **Copy and paste** the content of the `SVG-Image-Gen.py` file into the editor.
3.  **Save and Run** the application. The app will use your active Snowflake session, so no additional login is required.

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

The application includes a "Troubleshooting" section that covers common issues such as:

-   Stage not found errors.
-   Cortex AI not being available.
-   Permission errors related to your Snowflake role.
-   File upload failures.

Refer to this section within the app for performance tips and solutions to common problems.

## 📄 License

Please add your own license information here. A common choice for open-source projects is the MIT License.
