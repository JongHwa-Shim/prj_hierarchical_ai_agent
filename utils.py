from langchain.callbacks.base import BaseCallbackHandler
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
import json
class PrintStreamingSaveOutputCallback(BaseCallbackHandler):
    def __init__(self):
        self.result = ""  # 최종 결과 저장
    
    def on_llm_new_token(self, token: str, **kwargs):
        print(token, end="", flush=True)  # 실시간 출력
        self.result += token  # 문자열 저장

class AIScheduleParser:
    def __init__(self):
        self.parsing_prompt = """Please analyze the text below, which consists of multiple "Sub-Task" blocks. Each "Sub-Task #X" contains the following information that I want you to parse and structure in a machine-readable format (e.g., JSON):

1. Sub-Task Number
   - Noted as: "Sub-Task #1", "Sub-Task #2", etc.
   - Extract the integer value (e.g., 1, 2, 3...) as "subtask_num".

2. Sub-Task Description
   - Marked by: "- Sub-Task Description:"
   - Extract everything that follows this label as "subtask_description".

3. Assigned Sub-Module
   - Marked by: "- Assigned Sub-Module:"
   - Extract everything that follows this label as "assigned_submodule".

4. Input Parameters & Values
   - Marked by: "- Input Parameters & Values:"
   - Under this section, there may be multiple parameter blocks. Each parameter block follows this format:

       - <parameter_name>:
         - Input/Output Dependencies: ...
         - Input Parameter Values: ...

     Replace <parameter_name> with the actual parameter name in the text. For each parameter:
       - "input_name": the name that appears right after the dash (e.g., "- search_keyword:")
       - "io_dependency": the text that follows "Input/Output Dependencies:"
       - "value": the text that follows "Input Parameter Values:"
     Collect all parameter blocks in an array called "input".

5. Data Extraction Details
   - For each Sub-Task #X, capture all the above fields.
   - If any field (e.g., Assigned Sub-Module) is missing, do your best to extract all the other fields.
   - Some Sub-Tasks might have multiple parameters under "Input Parameters & Values:", so please be sure to capture them all in an array.

6. Output Format
   - Return the results as an array (e.g., JSON) of Sub-Task objects. For example:

     [
       {{
         "subtask_num": 1,
         "subtask_description": "Some description...",
         "assigned_submodule": "ModuleName",
         "input": [
           {{
             "input_name": "search_keyword",
             "io_dependency": "Sub-Task #2",
             "value": "None"
           }},
           {{
             "parameter_name": "search_method",
             "io_dependency": "None",
             "value": "some_value"
           }}
         ]
       }},
       {{
         "subtask_num": 2,
         "subtask_description": "...",
         "assigned_submodule": "...",
         "input": [...]
       }}
     ]

7. Task
   - Please read the text that follows and extract all the relevant fields according to the instructions above.
   - Then provide the parsed data in the specified JSON structure (or another structured format if needed).

[Constrains and Instructions]
Here are some important details and compliance rules you must adhere to while performing your work.
- Do not output json block indicator (```json ```) in the final output.
- Also, no matter how long the content of the input parameter values ​​is, do not abbreviate or omit it(e.g., use ellipses (...) ). Enter the entire content as is.
- Do not output any other strings such as greetings, formal responses, or closing remarks. Only output the extraction result. 

Now, here's the text to analyze: {input_text}"""

    def __call__(self, input_text):
        prompt = ChatPromptTemplate.from_messages([("user", self.parsing_prompt)])
        params = {
            "temperature": 0.0,         # 생성된 텍스트의 다양성 조정
            "max_tokens": 16384,          # 생성할 최대 토큰 수    
        }
        callback_handler = PrintStreamingSaveOutputCallback()
        llm = ChatOpenAI(model="gpt-4o", streaming=True, callbacks=[callback_handler],**params)
        output_parser = StrOutputParser()

        chain = prompt | llm | output_parser

        print("\n\n<<Start parsing schedule>>\n\n")
        parse_result = chain.invoke({'input_text': input_text})
        subtask_list = json.loads(parse_result)

        return subtask_list

class RegexScheduleParser:
    def __init__(self):
        None
    
    def __call__(self):
        None

class IODependencySolver:
    def __init__(self):
        self.dependency_prompt = """You are the '{submodule_name}' module with the following capabilities:
- {submodule_description}

The subtask you must perform is:
- {subtask_description}

To complete this subtask, we need a variable called '{input_name}', which:
- Serves as {input_description}
- Must strictly follow this format: {input_format}

Below is the provided output/data to examine. This data is the output from the previous subtask and contains relevant information for you to perform the subtask.:
Provided output/data: {required_subtask_output}

Your objectives are:
1. Identify the relevant information from "Provided output/data" that should be placed into '{input_name}'.
2. Convert or reformat that information so it adheres to the '{input_format}' specification.
3. Return only the final value of '{input_name}' in the correct format, without additional explanations or reasoning.

Important notes:
- If the data is unclear, please make the best possible inference. No matter what, you have to get a result. Don't output other text, such as an explanation of uncertainty.
- The result must always conform to the '{input_format}'.
- In your final response, output only the reformatted '{input_name}' value, with no extra commentary.
- Do not print quotes or double quotes to express sentences.
- Also, no matter how long the value of '{input_name} ​​is, do not abbreviate or omit it(e.g., use ellipses (...) ). Enter the entire value as is."""
    
    def __call__(self, required_subtask_output, subtask_description, submodule_name, submodule_description, input_name, input_description, input_format):
        prompt = ChatPromptTemplate.from_messages([("user", self.dependency_prompt)])
        params = {
            "temperature": 0.0,         # 생성된 텍스트의 다양성 조정
            "max_tokens": 16384,          # 생성할 최대 토큰 수    
        }
        callback_handler = PrintStreamingSaveOutputCallback()
        llm = ChatOpenAI(model="gpt-4o-mini", streaming=True, callbacks=[callback_handler],**params)
        output_parser = StrOutputParser()

        chain = prompt | llm | output_parser

        print("\n\n<<Solving IO Dependency>>\n\n")
        result = chain.invoke({'required_subtask_output': required_subtask_output, 'submodule_name': submodule_name,
                                     'subtask_description': subtask_description, 'submodule_description': submodule_description,
                                     'input_name': input_name, 'input_description': input_description, 'input_format': input_format})
        
        return result

import re
def parse_subtask_num(text: str):
    """'Sub-Task #n'에서 n만 추출하는 함수"""
    match = re.search(r"(?<=Sub-Task #)\d+", text)
    return int(match.group()) if match else None

if __name__ == "__main__":
    from env import *
    solver = IODependencySolver()
    solver(required_subtask_output="분석 결과, 요청을 처리하기 위해 적절한 부서는 경영본부 > ESG경영처 > 법무팀으로 판단됩니다.", 
           subtask_description="Format the identified department into the specified response format.", submodule_name="answer_module", 
           submodule_description="Converts the input sentence to the given answer format and answer conditions to provide the final answer.",
           input_name="input_sentence", input_description="The input sentence that needs to be converted to the answer format.", 
           input_format="A string that describes the input sentence.")