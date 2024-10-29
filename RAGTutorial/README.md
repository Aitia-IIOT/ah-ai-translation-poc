# AITIA's RAG Tutorial

This repository is a tutorial on implementing **Retrieval-Augmented Generation (RAG)** using OpenAI's **ChatGPT-4** and **Chroma** as the vector database. We use **distiluse-base-multilingual-cased-v2** from Hugging Face for embedding text chunks. 

This tutorial walks you through three main functionalities:

1. **Creating a Chroma Database**: We create an initial Chroma vector database by embedding text and storing the vectors.
2. **Updating the Database**: New chunks of data are embedded and added to the existing Chroma database.
3. **Answering a User-Defined Question**: Based on the user's input question, we retrieve relevant chunks from the database and generate an answer using ChatGPT-4.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [1. Creating a Chroma Database](#1-creating-a-chroma-database)
  - [2. Updating the Database with New Chunks](#2-updating-the-database-with-new-chunks)
  - [3. Answering a User-Defined Question](#3-answering-a-user-defined-question)

---

## Installation

### Prerequisites

Before you begin, make sure you have the following installed:

- Python 3.8+


### Steps

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/rag-tutorial.git
    cd rag-tutorial
    ```

2. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

---

## Usage

The program has a user friendly GUI, it requires no knownledge of how RAG works.


### 1. Creating a Chroma Database
Simply click on the *"Create database"* button, choose a folder with the files you want to be in the database, and click on the "Go" button.

### 2. Updating the database with new chunks
Select the *"Update database"* menupoint and then select a folder with your desired files that you want to be represented in te database.

### 3. Answering a user defined question

Under the menupoint of *"User question"* you can write a question which will be answerd by the LLM using your database.