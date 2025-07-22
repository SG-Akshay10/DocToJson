import io
import json
import streamlit as st
from unstructured.partition.auto import partition
from langchain_groq import ChatGroq

st.set_page_config(
    page_title="DocToJson",
    layout="wide",
)

st.title("Document to Structured JSON Generator (Groq API)")
st.write(
    "**Instructions:**\n"
    "1. **Configure your Groq API Key** in the sidebar.\n"
    "2. **Upload a document** (PDF, DOCX, etc.) to extract its text content.\n"
    "3. **Upload a JSON file** to serve as the output schema.\n"
    "4. **Click Generate** to populate the schema with information from the document using the Groq API."
)
st.info(
    "**Authentication:** This app uses a Groq API Key for generation."
)

st.divider()

with st.sidebar:
    st.header("Groq AI Configuration")
    groq_api_key = st.text_input(
        "Groq API Key",
        value="", 
        type="password",
        help="Enter your Groq API Key."
    )
    model_name = st.selectbox(
        "Select a Model",
        ("llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768", "gemma-7b-it"),
        help="Choose the Groq model to use for generation."
    )

if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = None
if 'generated_json' not in st.session_state:
    st.session_state.generated_json = None
if 'json_schema' not in st.session_state:
    st.session_state.json_schema = None

def reset_document_state():
    """Resets state when a new document is uploaded."""
    st.session_state.extracted_text = None
    st.session_state.generated_json = None
    st.session_state.json_schema = None

def reset_schema_state():
    """Resets state when a new schema is uploaded."""
    st.session_state.generated_json = None
    st.session_state.json_schema = None


col1, col2 = st.columns(2)

with col1:
    st.header("Step 1: Extract Text from Document")

    supported_types = ["pdf", "docx", "csv", "xlsx", "html", "md", "txt"]
    uploaded_file = st.file_uploader(
        "Choose a document file",
        type=supported_types,
        help="Upload a file to extract its text content.",
        on_change=reset_document_state 
    )

    if uploaded_file is not None and st.session_state.extracted_text is None:
        with st.spinner(f"Processing {uploaded_file.name}..."):
            try:
                file_content = io.BytesIO(uploaded_file.getvalue())
                file_content.name = uploaded_file.name 

                elements = partition(file=file_content)

                full_text = "\n\n".join([str(el) for el in elements])
                st.session_state.extracted_text = full_text

            except Exception as e:
                st.error(f"An error occurred while processing the file: {e}")
                st.session_state.extracted_text = None

    if st.session_state.extracted_text:
        st.subheader("Extracted Content")
        with st.expander("Click to view extracted text", expanded=False):
            st.text_area(
                label="Full Text",
                value=st.session_state.extracted_text,
                height=400,
                label_visibility="collapsed"
            )

with col2:
    st.header("Step 2: Generate Structured JSON")

    if st.session_state.extracted_text:
        json_schema_file = st.file_uploader(
            "Upload JSON schema file",
            type=["json"],
            help="Upload a JSON file that defines the structure of the desired output.",
            on_change=reset_schema_state 
        )

        if json_schema_file is not None and st.session_state.json_schema is None:
            try:
                schema_string = json_schema_file.getvalue().decode("utf-8")
                st.session_state.json_schema = json.loads(schema_string)
            except json.JSONDecodeError:
                st.error("Invalid JSON schema file. Please upload a well-formatted JSON file.")
                st.session_state.json_schema = None
            except Exception as e:
                st.error(f"An error occurred while reading the JSON schema file: {e}")
                st.session_state.json_schema = None

        if st.session_state.json_schema:
            st.subheader("Your JSON Schema")
            st.json(st.session_state.json_schema, expanded=False)

            if st.button("Generate JSON with Groq", type="primary"):
                if not groq_api_key:
                    st.warning("Please enter your Groq API Key in the sidebar.")
                else:
                    with st.spinner("Calling Groq API to generate JSON..."):
                        try:
                            llm = ChatGroq(
                                groq_api_key=groq_api_key,
                                model_name=model_name
                            )

                            prompt = f"""
                            Your task is to act as a JSON generator. Based on the document text provided, extract the relevant information and format it into a JSON object that strictly follows the given schema.

                            IMPORTANT: Only output the raw JSON object. Do not include any explanatory text, markdown formatting, or anything else before or after the JSON data.

                            ---
                            JSON SCHEMA:
                            ```json
                            {json.dumps(st.session_state.json_schema, indent=2)}
                            ```
                            ---
                            DOCUMENT TEXT:
                            ```text
                            {st.session_state.extracted_text}
                            ```
                            ---

                            Now, generate the JSON object based on the schema and text.
                            """

                            response = llm.invoke(prompt)
                            response_text = response.content

                            st.session_state.generated_json = json.loads(response_text)

                        except json.JSONDecodeError:
                            st.error("The model did not return a valid JSON object. This can happen with complex documents. Please review the model's raw output below.")
                            st.text_area("Model Raw Output:", value=response_text, height=300)
                            st.session_state.generated_json = None 
                        except Exception as e:
                            st.error(f"An unexpected error occurred during generation: {e}")
                            st.session_state.generated_json = None 

        if st.session_state.generated_json:
            st.divider()
            st.subheader("Generated JSON Content")
            st.json(st.session_state.generated_json, expanded=True)

            json_string_to_download = json.dumps(st.session_state.generated_json, indent=2)

            output_filename = "generated_output.json"
            if uploaded_file is not None:
                base_name = uploaded_file.name.rsplit('.', 1)[0]
                output_filename = f"{base_name}_structured.json"

            st.download_button(
               label="Download JSON",
               data=json_string_to_download,
               file_name=output_filename,
               mime="application/json",
            )

    else:
        st.info("Please upload and process a document in Step 1 to begin.")

