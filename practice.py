from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_core.prompts import PromptTemplate
from utils import PrintStreamingSaveOutputCallback
from env import * # TODO: llm 종류, temperature 등 다양한 환경 변수 설정 추가 필요

callback_handler = PrintStreamingSaveOutputCallback()
from prompt import scheduling_practice
prompt = ChatPromptTemplate.from_messages([("user", scheduling_practice)])

params = {
    "temperature": 0.0,         # 생성된 텍스트의 다양성 조정
    "max_tokens": 16384,          # 생성할 최대 토큰 수    
}
llm = ChatOpenAI(model="gpt-4o", streaming=True, callbacks=[callback_handler],**params)
output_parser = StrOutputParser()

# chain 연결
chain = prompt | llm | output_parser

# chain 실행
# result = chain.stream({'input': None})
result = chain.invoke({'input': None})

print("stream 결과:")
for chunk in result:
    print(chunk, end="", flush=True)
print()
a = 1