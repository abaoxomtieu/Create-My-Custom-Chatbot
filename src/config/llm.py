from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI

llm_2_0 = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash", temperature=0.1, max_retries=2
)

llm_4o_mini = ChatOpenAI(model="gpt-4o-mini")
llm_4o = ChatOpenAI(model="gpt-4o")

embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

# Add this function for dynamic model selection
def get_llm(model_name: str, **kwargs):
    if model_name == "gemini-2.0-flash":
        return ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.1, max_retries=2, **kwargs)
    elif model_name == "gpt-4o-mini":
        return ChatOpenAI(model="gpt-4o-mini", **kwargs)
    elif model_name == "gpt-4o":
        return ChatOpenAI(model="gpt-4o", **kwargs)
    else:
        raise ValueError(f"Unknown model: {model_name}")
