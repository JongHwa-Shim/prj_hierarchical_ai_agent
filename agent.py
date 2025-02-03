class HierarchicalAIAgent:
    def __init__(self, module_dict, module_layer_dict, module_hierarchy):
        self.module_dict = module_dict
        self.module_layer = module_layer_dict
        self.module_hierarchy = module_hierarchy

        self._init_submodule_info()
    
    def _init_submodule_info(self):
        for hierarchy in self.module_hierarchy:
            super_module = self.module_dict[hierarchy["super_module"]]
            # submodule_dict = [{submodule: self.module_dict[submodule]} for submodule in hierarchy["sub_module"]]
            submodule_dict = {}
            for submodule in hierarchy["sub_module"]:
                submodule_dict[submodule] = self.module_dict[submodule]
            super_module.init_submodule_info(submodule_dict)

    def __call__(self, user_input):
        top_module = self.module_dict[self.module_layer["top"]]
        input_dict = {'request_task': user_input}
        result = top_module(input_dict)
        return result


