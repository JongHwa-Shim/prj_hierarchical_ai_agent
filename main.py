from module_class import *
from predifined_modules import *
from agent import *
from env import * 
from request_task import *

if __name__ == "__main__":
    service_module = BasicModule(service_module_config)
    inference_module = ToolModule(inference_module_config)
    answer_module = ToolModule(answer_module_config)
    
    module_dict = {'service_module': service_module, 'answer_module': answer_module, 'inference_module': inference_module}
    module_layer_dict = {'top': 'service_module', 'tool': ['inference_module', 'answer_module']}
    module_hierarchy_dict = [{'super_module':'service_module', 'sub_module': ['answer_module', 'inference_module']}]

    agent = HierarchicalAIAgent(module_dict=module_dict, module_layer_dict=module_layer_dict, module_hierarchy=module_hierarchy_dict)

    request_task_type = "department_type"

    if request_task_type == "department_type":
        request_task = request_task_department_type
    elif request_task_type == "service_type":
        request_task = request_task_service_type
    
    question1 = """운동할 때 쓰는 고무 튜빙밴드를 공항검색대나 기내반입이 가능한가요?고무로 된 긴 줄이라 불안하네요 어디에도 안된다고 적혀있지는 않지만 그래도 여행가서도 운동 조금씩 하려는데위탁수화물로는 보내봤지만 이번엔 위탁수화물 없이 기내수화물로만 여행하는거라 반입여부가 궁금하네요운동용 고무 튜빙밴드 공항검색대 반입 되는지 답변 부탁드립니다!"""
    question2 = """인천공항 어디에서 흡연해야 하나요? 흡연실 위치를 알려주세요."""
    question3 = """대한민국 애국가를 영어로 번역해주세요."""

    request_task = request_task.format(question2)
    agent(request_task)