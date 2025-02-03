from prompt import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from utils import PrintStreamingSaveOutputCallback
from utils import IODependencySolver

class BasicModule:
    def __init__(self, module_config):
        self.prompt_template = PromptTemplate
        self.prompt_dict = {}
        self.module_config = module_config
        self.meta_data = ModuleMetaData(module_config.module_name, module_config.layer, module_config.input_arg, module_config.input_description, module_config.module_description)
        
        try:
            self.pre_function = module_config.pre_function
        except:
            self.pre_function = None
        
        try:
            self.post_function = module_config.post_function
        except:
            self.post_function = None
        
        if module_config.schedule_parser == "ai_parser":
            from utils import AIScheduleParser
            self.schedule_parser = AIScheduleParser()
        elif module_config.schedule_parser == "regex_parser":
            from utils import RegexScheduleParser
            self.schedule_parser = RegexScheduleParser()
        else:
            raise ValueError("Invalid schedule parser type. Choose from 'ai_parser' or 'regex_parser'.")
        
        self.dependency_solver = IODependencySolver()

        self._init_scheduling_prompt()

    def _init_scheduling_prompt(self):
        self.prompt_dict["scheduling_with_module_role"] = self.prompt_template.scheduling_basic.partial(module_role = self.module_config.module_role)

    def init_submodule_info(self, submodule_dict):
        def _init_scheduling_prompt_submodule_info(self, submodule_dict):
            submodule_info_list = []
            for submodule_name, submodule_instance in submodule_dict.items():
                input_name_list = []
                input_info_list = []
                for input_info in submodule_instance.meta_data.input_description:
                    input_name = input_info["input_name"]
                    input_description = input_info["description"]
                    input_format = input_info["format"]

                    input_name_list.append(input_name)

                    single_input_info_prompt = self.prompt_template.submodule_input_info.partial(input_name=input_name, input_description=input_description, input_format=input_format)
                    input_info_list.append(single_input_info_prompt)
                
                input_name_prompt = ", ".join(input_name_list)
                
                input_info_list = [input_info.format() for input_info in input_info_list]
                input_info_prompt = "".join(input_info_list)

                submodule_description = submodule_instance.meta_data.module_description

                prompt_submodule_info = self.prompt_template.submodule_info
                prompt_submodule_info = prompt_submodule_info.partial(submodule_name=submodule_name, submodule_description=submodule_description,
                                                                      submodule_parameters=input_name_prompt, submodule_input_parameters=input_name_prompt, 
                                                                      submodule_input_description=input_info_prompt)
                submodule_info_list.append(prompt_submodule_info)
            
            submodule_info_list = [submodule_info.format() for submodule_info in submodule_info_list]
            submodule_info_prompt = "\n\n".join(submodule_info_list)
            self.prompt_dict["scheduling_final"] = self.prompt_dict["scheduling_with_module_role"].partial(submodule_info=submodule_info_prompt)

        self.submodule_dict = submodule_dict
        _init_scheduling_prompt_submodule_info(self, submodule_dict)

    # def init_system_prompt(self): #!
    #     self._init_scheduling_prompt()

    def scheduling(self, request_task): # TODO: 설정 같은건 외부(module_config)에서 불러오도록 고쳐야함
        scheduling_prompt = self.prompt_dict["scheduling_final"].format(request_task=request_task)
        prompt = ChatPromptTemplate.from_messages([("user", scheduling_prompt)])
        params = {
            "temperature": 0.0,         # 생성된 텍스트의 다양성 조정
            "max_tokens": 16384,          # 생성할 최대 토큰 수    
        }
        callback_handler = PrintStreamingSaveOutputCallback()
        llm = ChatOpenAI(model="gpt-4o", streaming=True, callbacks=[callback_handler],**params)
        output_parser = StrOutputParser()

        chain = prompt | llm | output_parser

        print(f"<<Start scheduling for request task>>\n")
        schedule = chain.invoke({'input': None})

        return schedule
    
    def parse_schedule(self, schedule):
        subtask_list = self.schedule_parser(schedule)
        return subtask_list

    
    def handling_io_dependency(self, subtask, subtask_output):
        def solve_io_dependency(io_dependency, submodule, subtask_description, input_name, subtask_output):
            from utils import parse_subtask_num
            subtask_num = parse_subtask_num(io_dependency)
            required_subtask_output = subtask_output[subtask_num]
            submodule_description = submodule.meta_data.module_description
            submodule_name = submodule.meta_data.module_name
            for input_info in submodule.meta_data.input_description:
                if input_info["input_name"] == input_name:
                    input_description = input_info["description"]
                    input_format = input_info["format"]
                    break

            input_value = self.dependency_solver(required_subtask_output, submodule_name, subtask_description, submodule_description, 
                                                 input_name, input_description, input_format)
            return input_value
        
        for input in subtask["input"]:
            if not input["io_dependency"] == "None":
                
                input_value = solve_io_dependency(input["io_dependency"], self.submodule_dict[subtask["assigned_submodule"]], 
                                                  subtask["subtask_description"], input["input_name"], subtask_output)
                input["value"] = input_value
        return subtask

    def collect_subtask_input(self, inputs):
        collected_input_dict = {}
        for input in inputs:
            collected_input_dict[input["input_name"]] = input["value"]
        return collected_input_dict

    def __call__(self, input):
        # Check for the existence of required input parameter.
        for input_arg in self.meta_data.input_arg:
            try:
                input[input_arg]
            except:
                raise ValueError(f"The value for parameter {input_arg} was not given.")

        # Preprocessing input or execute preliminary function.
        if self.pre_function is None:
            request_task = input["request_task"] # assuming input have only "request_task"
        else:
            request_task = self.pre_function(input)

        # Scheduling sub-tasks.
        schedule = self.scheduling(request_task)
        subtask_list = self.parse_schedule(schedule)

        """
        [subtask and subtask_outputs structure]

        subtask = {"subtask_num": <n>, "assigned_submodule": <submodule instance>, "input": [{"input_name": <text of input parameter name>, 
        "io_dependency": <text of io_dependecy>, "value": <value of input parameter}, ...]
        }

        subtask_outputs = {<subtask_name1>: <subtask_output1>, <subtask_name2>: <subtask_output2>, ...}
        """

        # Execute sub-tasks
        subtask_outputs = {}
        for subtask in subtask_list:
            subtask = self.handling_io_dependency(subtask, subtask_outputs) # Provides input parameter value that have io dependencies, referring to the results of the previous sub-task.

            assigned_submodule = self.submodule_dict[subtask["assigned_submodule"]]
            subtask_input = self.collect_subtask_input(subtask["input"])
            subtask_output = assigned_submodule(subtask_input)
            subtask_outputs[subtask["subtask_num"]] = subtask_output

        # postprocessing input or execute posterior function.
        if self.post_function is None:
            module_output = subtask_output # bypass
        else:
            module_output = self.post_function(input)

        return module_output

class TopModule(BasicModule):
    def __call__(self, input):
        None

class IntermediateModule(BasicModule):
    def __call__(self, input):
        None
    
class ToolModule(BasicModule):
    def __call__(self, input):
        # Check for the existence of required input parameter.
        for input_arg in self.meta_data.input_arg:
            try:
                input[input_arg]
            except:
                raise ValueError(f"The value for parameter {input_arg} was not given.")

        # execute tool function.
        module_output = self.pre_function(**input)

        return module_output

class ModuleMetaData:
    def __init__(self, module_name, layer, input_arg, input_description, module_description):
        self.module_name = module_name
        self.layer = layer
        self.input_arg = input_arg
        self.input_description = input_description
        self.module_description = module_description

class module_config:
    def __init__(self, module_name,
                 layer,
                 input_arg,
                 input_description,
                 module_description,
                 module_role=None,
                 schedule_parser="ai_parser",
                 pre_function=None,
                 post_function=None,
                 ):
        '''
        Args:
            module_name (str): name of module.
            
            layer (str): layer of module. 
                allowed values:
                - 'top'
                - 'intermediate'
                - 'tool'

            input_type (str): type of input (formal, informal) --> deprecated
                allowed values:
                - 'formal': structured text or argument
                - 'informal': free-style text.

            input_arg (List of str): definition of input argument as json format. Follow the prompt format of the example.
                Examples: 
                    >>> input_fotmat = ["search_keyword, file_path"]

            input_description (List of dictionary): Detailed format and description of input argument. Follow the format of the example (python dictionary).
                If input_type = 'formal', provide the specific format of the input. 
                Examples:
                    >>> input_description = [{
                            'input_name': 'file_path',
                            'description': "'search_keyword'와 관련있는 자료를 포함하고 있는 텍스트 파일의 파일 경로입니다. 해당 모듈은 'file_path' 경로에 있는 텍스트 파일 내용을 읽어들여 'search_keyword'와 관련된 정보를 찾습니다.",
                            'format': "'example/of/the/file/path.txt'와 같이 구체적인 파일 경로를 명시해야하며, 파일의 확장자는 텍스트 파일 확장자인 .txt여야 합니다. 파일 경로 이외의 다른 문자열을 포함하면 안됩니다."
                        }, ...]
                If input_type = 'informal', provide abstract conditions on the input format.
                Examples:
                    >>> input_description = [{
                            'input_name': 'search_keyword',
                            'description': "의미론적 탐색을 수행할 검색 키워드 입니다. 해당 모듈은 'search_keyword'를 기반으로 의미론적 탐색을 수행합니다.",
                            'format': "몇개의 단어로 구성되야합니다. 검색 키워드 이외에 다른 문자열을 포함하면 안됩니다."
                        }, ...] 

            module_description (str): Simple description of the module. It should include what input module takes, what module does, and what output it returns.
                Examples:
                    >>> module_description = "해당 모듈은 입력 키워드 search_keyword와 텍스트 파일 경로 file_path를 입력받아 의미론적 탐색을 수행합니다. file_path 경로의 텍스트 파일을 열어 내용을 읽고, 텍스트 파일의 텍스트들을 여러개의 텍스트 묶음인 text chunk로 분할합니다. 그 이후, search_keyword와 text chunk 간의 텍스트 임베딩 벡터의 코사인 유사도를 통해 search_keyword와 text chunk 간의 유사도를 계산합니다. 마지막으로 가장 코사인 유사도가 높은 text chunk를 반환합니다."

            schedule_parser (str): select parser for scheduling output.
                allowed values:
                - 'ai_parser'
                - 'regex_parser'
            
            pre_function (function): user-defined function

            post_function (functin): user-defined function
        '''
        self.module_name = module_name
        self.layer = layer
        self.input_arg = input_arg
        self.input_description = input_description
        self.module_description = module_description
        self.module_role = module_role
        self.schedule_parser = schedule_parser
        self.pre_function = pre_function
        if post_function == "None":
            self.post_function = self.basic_post_function
        else:
            self.post_function = post_function

    @ classmethod
    def basic_pre_function():
        None
    
    @ classmethod
    def basic_post_function():
        None