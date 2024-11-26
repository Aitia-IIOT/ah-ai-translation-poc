#node call:Agent->RAG->ellenőrző->USER

#Install the required packages:
#pip install -r requirements.txt


import os, getpass
from IPython.display import Image
from langgraph.graph import START, StateGraph, add_messages,END
from langgraph.prebuilt import tools_condition, ToolNode
from langchain_core.messages import BaseMessage
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
from typing import Annotated, Literal, Sequence
from typing_extensions import TypedDict
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from langchain_core.documents import Document
from dotenv import load_dotenv 
import glob
import os
import datetime
load_dotenv()
def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

_set_env("OPENAI_API_KEY")
_set_env("LANGCHAIN_API_KEY")
_set_env("USER_AGENT")
llm = ChatOpenAI(model="gpt-4o")



file_list = glob.glob(os.path.join("test", "*.txt"))

docs = []

for file_path in file_list:
    with open(file_path) as f_input:
        docs.append( Document (page_content=f_input.read(), metadata={"source": file_path} ) )


text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=10, chunk_overlap=1
)
doc_splits = text_splitter.split_documents(docs)
#print(doc_splits)



# Add to vectorDB
vectorstore = Chroma.from_documents(
    documents=doc_splits,
    collection_name="AITIA_Docs_test",
    embedding=OpenAIEmbeddings(),
)
retriever = vectorstore.as_retriever()



retriever_tool = create_retriever_tool(
    retriever,
    "Retrieve_document_from_database", # description argument.
    "Search and return information about a type of batteries", # prompt argument.
)

tools = [retriever_tool]

class AgentState(TypedDict):
    # The add_messages function defines how an update should be processed
    # Default is to replace. add_messages says "append"
    messages: Annotated[Sequence[BaseMessage], add_messages]



def grade_documents(state) -> Literal["generate", "retry"]:
    """
    Determines whether the output is in the correct format or not.

    Args:
        state (messages): The current state

    Returns:
        str: A decision for whether the format is correct or not
    """

    print("---CHECK FORMAT---")

    # Data model
    class grade(BaseModel):
        """Binary score for format check."""

        binary_score: str = Field(description="format score 'yes' or 'no'")

    # LLM
    model = ChatOpenAI(temperature=0, model="gpt-4o", streaming=True)

    # LLM with tool and validation
    llm_with_tool = model.with_structured_output(grade)

    # Prompt
    prompt = PromptTemplate(
        template="""You are a grader assessing the format of an output from an LLM. \n 
        Here is the output: \n\n {context} \n\n
        Here is the expected format: {expected_format} \n
        If the document adheres the expected format, grade it as relevant. \n
        Give a binary score 'yes' or 'no' score to indicate whether the document is in the correct format or no.""",
        input_variables=["context", "expected_format"],
    )

    # Chain
    chain = prompt | llm_with_tool

    messages = state["messages"]
    last_message = messages[-1]

    expected_format = messages[0].content
    docs = last_message.content

    scored_result = chain.invoke({"expected_format": expected_format, "context": docs})

    score = scored_result.binary_score

    if score == "yes":
        print("---DECISION: FORMAT CORRECT---")
        return "generate"

    else:
        print("---DECISION: FORMAT INCORRECT---")
        print(score)
        return "retry"


### Nodes


def agent(state):
    """
    Invokes the agent model to generate a response based on the current state. Given
    the question, it will decide to retrieve using the retriever tool, or simply end.

    Args:
        state (messages): The current state

    Returns:
        dict: The updated state with the agent response appended to messages
    """
    print("---CALL AGENT---")
    messages = state["messages"]
    model = ChatOpenAI(temperature=0, streaming=True, model="gpt-4o")
    model = model.bind_tools(tools)
    response = model.invoke(messages)
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}


def retry(state):
    """
    Returns the input state without the last LLM response.

    Args:
        state (messages): The current state

    Returns:
        dict: The  state without the last LLM formatting.
    """

    print("---RETRY FORMATTING--")
    messages = state["messages"]
    messages = messages[:-1]
    state["messages"] = messages
    return {"messages": [state]}


def generate(state):
    """
    Outputs the document in the correct format.

    Args:
        state (messages): The current state

    Returns:
         dict: The updated state with re-phrased question
    """
    print("---GENERATE---")
    messages = state["messages"]
    return {"messages": [messages[0]]}


def User_approval(state) -> Literal["save_document", "retry"]:
    """
    Outputs the document in the correct format.

    Args:
        state (messages): The current state

    Returns:
         dict: The updated state with re-phrased question
    """
    print("---User_approval---")
    print()
    print()
    print(state["messages"][0])
    print()
    print("Do you approve the document? (yes/no)")
    score=input()
    messages = state["messages"]
    if score == "yes":
        print("---DECISION: FORMAT CORRECT---")
        return "save_document"

    else:
        print("---DECISION: FORMAT INCORRECT---")
        print(score)
        return "retry"

def save_document(state):
    """
    saves the output in a file.

    Args:
        state (messages): The current state

    Returns:
         dict: The updated state with re-phrased question
    """
    print("---GENERATE---")
    
    ct = datetime.datetime.now()
    print("current time: ", ct)
    messages = state["messages"]
    return {"messages": [messages[0]]}

# Define a new graph
workflow = StateGraph(AgentState)

# Define the nodes we will cycle between
workflow.add_node("agent", agent)  # agent
retrieve = ToolNode([retriever_tool])
workflow.add_node("retrieve", retrieve)  # retrieval
workflow.add_node("retry", retry)  # retrying the formatting
workflow.add_node("generate", generate)  # Generating a response after we know the documents are in the correct format
workflow.add_node("save_document", save_document)  # Saving a response after we know the documents are in the correct format

# Call agent node to decide to retrieve or not
workflow.add_edge(START, "agent")


# Decide whether to retrieve
workflow.add_conditional_edges(
    "agent",
    # Assess agent decision
    tools_condition,
    {
        # Translate the condition outputs to nodes in our graph
        "tools": "retrieve",
        END: END,
    },
)

# Edges taken after the `action` node is called.
workflow.add_conditional_edges(
    "retrieve",
    # Assess agent decision
    grade_documents,
)
workflow.add_conditional_edges(
    "generate",
    User_approval,
    )
workflow.add_edge("retry", "agent")
workflow.add_edge("save_document", END)    
# Compile
graph = workflow.compile()

from IPython.display import Image

try:
    img = Image(graph.get_graph(xray=True).draw_mermaid_png())
    with open("graph_image.png", "wb") as f:
        f.write(img.data)
except Exception:
    # This requires some extra dependencies and is optional
    pass