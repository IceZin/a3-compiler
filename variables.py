from utils import gen_hex


class Variables:
    def __init__(self, scope):
        self.__variables = {}
        self.__reassigns = {}
        self.scope = scope

    def register(self, var_type, name, args):
        if not self.check_availability(name):
            raise Exception(f"variable {name} already declared")
        
        self.__variables[name] = {
            "var_type": var_type,
            "args": args,
            "value": None,
            "scope": self.scope
        }

    def register_reassign(self, scope):
        reassign_address = gen_hex()

        while reassign_address in self.__reassigns.keys():
            reassign_address = gen_hex()

        self.__reassigns[reassign_address] = {
            "scope": scope
        }

        return reassign_address

    def check_availability(self, name):
        if name in self.__variables.keys():
            return False
        
        parent_scope = self.scope.parent

        while parent_scope is not None:
            if name in parent_scope.variables.keys():
                return False
            
            parent_scope = parent_scope.parent

        return True
    
    def keys(self):
        return self.__variables.keys()
    
    def get(self, name):
        return self.__variables.get(name)

    def read_int(self, var):
        scope = var["scope"]
        equation = []

        for arg in var["args"]:
            if arg[0].isalpha():
                replace_value = scope.get_variable(arg)["value"]
                equation.append(replace_value)
            else:
                equation.append(arg)

        equation = " ".join(equation)
        result = str(eval(equation))
        var["value"] = result

    def reassign_int(self, var, args, reassign_address):
        if reassign_address:
            scope = self.__reassigns[reassign_address]["scope"]
        else:
            scope = self.scope
        equation = []

        for arg in args:
            if arg[0].isalpha():
                replace_value = scope.get_variable(arg)
                equation.append(replace_value["value"])
            else:
                equation.append(arg)

        equation = " ".join(equation)
        result = str(eval(equation))
        var["value"] = result

    def read_string(self, var):
        var["value"] = (" ".join(var["args"])).replace('"', '')