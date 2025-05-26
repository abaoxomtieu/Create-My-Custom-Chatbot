from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings

llm_2_0 = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=1, max_retries=2)

llm_2_5_flash_preview = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-preview-05-20", temperature=1, max_retries=2
)


embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")


# Add this function for dynamic model selection
def get_llm(model_name: str, **kwargs):
    if model_name == "gemini-2.0-flash":
        return llm_2_0
    elif model_name == "gemini-2.5-flash-preview-05-20":
        return llm_2_5_flash_preview
    else:
        raise ValueError(f"Unknown model: {model_name}")
