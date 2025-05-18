from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI

llm_2_0 = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash", temperature=0.1, max_retries=2
)
llm_1_5_pro = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro", temperature=0.1, max_retries=2
)
llm_2_5_pro = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro-exp-03-25", temperature=0.1, max_retries=2
)

embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

