from module_class import *

service_module_config = module_config(module_name="service_module",
              layer="top",
              input_arg=["request_task"],
              input_description=[{'input_name': 'request_task', 'description': "various requested tasks that you must perform faithfully.", 
                                  'format': 'A string that describes the request task.'}],
              module_description="As the top-level module that receives user requests, this module appropriately distributes the requested tasks to various sub-modules.",
              module_role="As the top-level module that receives user requests, this module appropriately distributes the requested tasks to various sub-modules.",
              schedule_parser="ai_parser",
              pre_function=None,
              post_function=None)

def inference(inference_task, inference_topic, reference_data):
    inference_prompt_template = """
당신은 높은 수준의 논리적 사고와 비판적 사고를 수행할 수 있는 전문가 AI입니다. 주어진 정보와 지식, 맥락, 그리고 참고 자료를 토대로 철저하고 단계적인 추론 과정을 거쳐 최적의 답변을 도출하세요. 가능하면 **합리적인 근거와 논리적 전개 과정을 간략히 설명**하고, **최종 결론**을 제시해 주세요.

1. 추론해야 할 작업 (inference_task):
   "{inference_task}"

2. 추론 작업의 주제 (inference_topic):
   "{inference_topic}"

3. 참고할 데이터 / 정보 (reference_data):
   "{reference_data}"

위의 세 가지 정보를 바탕으로, 다음 내용을 수행해 주세요:

- **1) 추론 과정**  
  - 해당 작업(inference_task)을 해결하기 위해 필요한 전제, 가정, 추가 정보 등이 무엇인지 단계별로 정리해 주세요.  
  - 참고 데이터(reference_data)를 어떻게 활용할 수 있는지, 유의해야 할 점은 무엇인지 논리적으로 서술해 주세요.

- **2) 결론 도출**  
  - 위에서 정리한 논리적 근거 및 정보를 종합하여 최종 결론을 제시해 주세요.  
  - 결론 도출의 이유 또는 근거를 한두 문장으로 간단히 요약해 주세요."""
    
    prompt = ChatPromptTemplate.from_messages([("user", inference_prompt_template)])
    params = {
        "temperature": 0.0,         # 생성된 텍스트의 다양성 조정
        "max_tokens": 16384,          # 생성할 최대 토큰 수    
    }
    callback_handler = PrintStreamingSaveOutputCallback()
    llm = ChatOpenAI(model="gpt-4o-mini", streaming=True, callbacks=[callback_handler],**params)
    output_parser = StrOutputParser()

    chain = prompt | llm | output_parser

    print("\n\n<<Inference Module Executed>>\n\n")
    result = chain.invoke({'inference_task': inference_task, 'inference_topic': inference_topic, 'reference_data': reference_data})
    
    return result
inference_module_config = module_config(module_name="inference_module",
                                        layer="tool",
                                        input_arg=['inference_task', 'reference_data'],
                                        input_description=[{'input_name': 'inference_task', 'description': "Detailed description of tasks and situations that require logical reasoning.",
                                                            'format': "A string that describes the task that requires logical reasoning."},
                                                            {'input_name': 'inference_topic', 'description': "Detailed Description of the topic of inference.", 'format': "A string."},
                                                            {'input_name': 'reference_data', 'description': "Data to be referenced when making inferences",
                                                             'format': "A string that describes the data that can be used as a reference for logical reasoning."}
                                                            ],
                                        module_description="Solve given problems through logical reasoning.",
                                        schedule_parser='ai_parser',
                                        pre_function=inference,
                                        post_function=None)

def answer(input_sentence, answer_instructions):
    inference_prompt_template = """You have two variables:
1) `input_sentence`: 사용자로부터 입력된 문장
2) `answer_instructions`: 최종 답변이 따라야 할 형식(Format)이나 규칙(Rules)

Your task is to transform `input_sentence` according to the description in `answer_instructions`. Then, provide the final answer in the specified format.

Constraints:
- Output ONLY the final reformatted answer.
- Do not include any additional explanations, debug logs, or reasoning steps.
- Follow exactly what `answer_instructions` prescribes.
- Bring in as many and as wide a range of values ​​as possible to avoid excluding any required values.
---

Input to the model:
- `input_sentence`: {input_sentence}
- `answer_instructions`: {answer_instructions}"""

    prompt = ChatPromptTemplate.from_messages([("user", inference_prompt_template)])
    params = {
        "temperature": 0.0,         # 생성된 텍스트의 다양성 조정
        "max_tokens": 16384,          # 생성할 최대 토큰 수    
    }
    callback_handler = PrintStreamingSaveOutputCallback()
    llm = ChatOpenAI(model="gpt-4o-mini", streaming=True, callbacks=[callback_handler],**params)
    output_parser = StrOutputParser()

    chain = prompt | llm | output_parser

    print("\n\n<<Answer Module Executed>>\n\n")
    result = chain.invoke({'input_sentence': input_sentence, 'answer_instructions': answer_instructions})
    
    return result
answer_module_config = module_config(module_name="answer_module",
                                     layer='tool',
                                     input_arg=['input_sentence', 'answer_instructions'],
                                     input_description=[{'input_name': 'input_sentence', 'description': "The input sentence that needs to be converted to the answer format.", 
                                                         'format': "Free text format."}, 
                                                         {'input_name': 'answer_instructions', 'description': "Detailed description of the answer format and conditions under which the input sentence must be converted.",
                                                          'format': "Free text format"}],
                                     module_description="Converts the input sentence to the given answer format and answer conditions to provide the final answer.",
                                     schedule_parser='ai_parser',
                                     pre_function=answer,
                                     post_function=None)

if __name__ == "__main__":
    None    