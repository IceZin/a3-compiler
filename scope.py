from utils import gen_hex
from variables import Variables


class Scope:
    def __init__(self, name, address, parent=None):
        self.name = name
        self.__scopes = {}
        self.__address = address
        self.__lines = []
        self.__parent = parent
        self.__variables = Variables(self)

    @property
    def parent(self):
        return self.__parent
    
    @property
    def scopes(self):
        return self.__scopes
    
    @property
    def variables(self) -> Variables:
        return self.__variables
    
    def get_variable(self, name):
        var = self.__variables.get(name)

        if var:
            return var
        
        scope = self.parent
        while scope is not None:
            var = scope.variables.get(name)

            if var:
                return var
            
            scope = scope.parent

        return None
    
    def read_variable(self, name):
        var = self.get_variable(name)

        if var:
            reader = getattr(self.variables, f"read_{var['var_type']}")
            reader(var)

    def reassign_variable(self, args, reassign_address):
        var = self.get_variable(args[0])

        if var:
            reader = getattr(self.variables, f"reassign_{var['var_type']}")
            reader(var, args[2:], reassign_address)
    
    def create_scope(self, name):
        scope_address = gen_hex()

        while scope_address in self.__scopes.keys():
            scope_address = gen_hex()

        scope = Scope(name, scope_address, self)
        self.__scopes[scope_address] = scope

        return scope

    def add_line(self, line_num):
        self.__lines.append(line_num)