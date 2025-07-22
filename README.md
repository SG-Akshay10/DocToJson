# DocToJSON: Unstructured Text to Structured JSON Extraction

**DocToJSON** is a powerful and scalable system designed to convert unstructured documents (like PDFs, DOCX, and text files) into structured JSON, strictly following a complex, user-defined schema. It intelligently overcomes the context window limitations of modern LLMs to handle massive documents and schemas with ease.

### The Architectural Vision

This repository is a proof-of-concept implementation of a much larger architectural idea. The complete system design, which details the full-scale approach, can be found here:

* **Full System Design Document:** [`DocToJSON - System Design.pdf`](https://github.com/SG-Akshay10/DocToJson/blob/main/DocToJSON%20-%20System%20Design.pdf)

The core idea is a robust, "divide and conquer" strategy to solve this problem:

* **Schema Decomposition:** Instead of tackling one giant schema, the system programmatically breaks the target JSON schema into smaller, logical "mini-schemas." This allows the LLM to focus on one manageable task at a time, dramatically improving accuracy.
* **Retrieval-Augmented Generation (RAG):** The entire source document is indexed into a vector database. For each mini-schema, the system performs a semantic search to retrieve only the most relevant text chunks. This feeds the LLM exactly the context it needs, without ever exceeding the context window.

### Key Features

* **Process Huge Documents:** Ingest and extract data from documents of virtually any size.
* **Handle Complex Schemas:** Reliably populates deeply nested JSON structures.
* **Built-in Validation:** Uses Pydantic models generated on-the-fly to validate every piece of extracted data, ensuring type safety and structural correctness.
* **Extensible Pipeline:** Designed with a clear, four-stage pipeline that's easy to understand and extend.

### How It Works

1.  **Prep Work:** Decomposes the master JSON schema into smaller parts and creates validation models.
2.  **Indexing:** Chunks and indexes the source document into a vector database.
3.  **Extraction & Validation:** For each small schema, it retrieves relevant context from the document and prompts an LLM to generate the structured data, which is then immediately validated.
4.  **Composition:** Stitches all the validated JSON parts back together into the final, complete document.

### Running the Demo Locally

The current implementation is a Streamlit demo that showcases the core functionality. To run the demo on your machine:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/SG-Akshay10/DocToJson.git
    cd DocToJson
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the Streamlit app:**
    ```bash
    streamlit run main.py
    ```
4.  **Use the application:**
    * This will open a locally hosted webpage.
    * Configure your Groq API Key in the sidebar.
    * Upload a document (PDF, DOCX, etc.) to extract its text content.
    * Upload a JSON file to serve as the output schema.
    * Click **Generate** to populate the schema with information from the document.
    * Download your prepared JSON using the download button.

### Usage Example & Demo

As a practical example, I used this system to convert my own resume into a structured JSON format.

* **Input Resume:** [`Akshay_Resume.pdf`](https://github.com/SG-Akshay10/DocToJson/blob/main/Input/Akshay_Resume.pdf)
* **Target JSON Format:** [`Akshay_Resume_structured.json`](https://github.com/SG-Akshay10/DocToJson/blob/main/Output/Akshay_Resume_structured.json)

This repository contains the core architecture and proposal for the DocToJSON system.
