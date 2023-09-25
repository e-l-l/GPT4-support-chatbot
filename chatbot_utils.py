import os
from PyPDF2 import PdfReader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
import requests
from wit import Wit

os.environ["OPENAI_API_KEY"] = "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"
client = Wit("SPOYTVVVGBOKG4NLGM73X6BVJRF26HU4")

def getLangs():
    url = "https://text-translator2.p.rapidapi.com/getLanguages"
    headers = {
        "X-RapidAPI-Key": "2820853ee3mshf9b0447869d2d4cp1c6e27jsned29a81f764a",
        "X-RapidAPI-Host": "text-translator2.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers)
    langs=response.json()["data"]["languages"]
    return langs

doc_reader = PdfReader('../ga.pdf')
raw_text = ''
for i, page in enumerate(doc_reader.pages):
    text = page.extract_text()
    if text:
        raw_text += text

text_splitter = CharacterTextSplitter(
    separator = "\n",
    chunk_size = 1000,
    chunk_overlap  = 200, #striding over the text
    length_function = len,
)
texts = text_splitter.split_text(raw_text)

embeddings = OpenAIEmbeddings()
docsearch = FAISS.from_texts(texts, embeddings)
chain = load_qa_chain(OpenAI(),
                      chain_type="stuff")

def translate(text,src,code):
    url = "https://text-translator2.p.rapidapi.com/translate"
    payload = {
        "source_language": src,
        "target_language": code,
        "text": text
    }
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "X-RapidAPI-Key": "2820853ee3mshf9b0447869d2d4cp1c6e27jsned29a81f764a",
        "X-RapidAPI-Host": "text-translator2.p.rapidapi.com"
    }
    response = requests.post(url, data=payload, headers=headers)
    return response.json()["data"]["translatedText"]

def reply(name,prompt,code):
    t_query=prompt
    if(code!='en'):
        t_query=translate(prompt,code,"en")
    chain.llm_chain.prompt.template="If it is only a greeting, greet them back,If the question is vague or it is vulgar, just say that you cant answer otherwise Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer tell them to contact the customer support at customersupport@abc.in. Answer queries related to ABC only, no other application allowed.Answer like customer support in detail. Use this customer information to make the conversation more human like. "+name+". Use bullet points where required.\n\n{context}\n\nQuestion: {question}\nHelpful Answer:"
    docs = docsearch.similarity_search(t_query)
    text=chain.run(input_documents=docs, question=t_query)
    witresponse=client.message(t_query)
    if(len(witresponse["intents"])==0):
        text=text
    elif(witresponse["intents"][0]["name"])=="orders":
        text=text+"\n You can view your orders at https://www.abc.com/gp/your-account/order-history"
    elif(witresponse["intents"][0]["name"])=="returns":
        text=text+"\n You can view your returns at https://www.abc.com/gp/css/returns/homepage.html"
    elif(witresponse["intents"][0]["name"])=="account_management":
        text=text+"\n You can view/edit your account details at https://www.abc.com/gp/css/accounts.html"
    if(code=="en"):
        return text
    else:
        return translate(text,"en",code)