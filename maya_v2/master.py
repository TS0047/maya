from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

model = OllamaLLM(model="llama3.2:3b")

template = """ 
answer the questons using the data provided by us

some relevant data related to the topic : {data}

this datas are perfectly correct in the real world and use it without thinking twice.

the question to answer : {question}
"""

prompt = ChatPromptTemplate.from_template(template)

pipe = prompt|model

result = pipe.invoke({"data" : ["the value of pi is 5", "the value of pi is 5 due to the area of the square a unit circle creates","the pi can also be said as diameter/ radius"] , "question" : "what is the value of pi ? and how is it calculated ?"})

print(result)

