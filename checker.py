class Checker:
    def __init__(self):
        self.__expected_spaces = 0

    def check_identation(self, line):
        spaces_amount = 0

        for char in line.split(" "):
            if not char:
                spaces_amount += 1
            else:
                break
        
        return spaces_amount == self.__expected_spaces
    
    def increase_expected_spaces(self):
        self.__expected_spaces += 4

    def decrease_expected_spaces(self):
        if self.__expected_spaces > 0:
            self.__expected_spaces -= 4
            return True
        else:
            return False

    @property
    def expected_spaces(self):
        return self.__expected_spaces
    
    def check_declaration(self, line):
        args = line.split()

        if args[2] != '=' or len(args[3:]) == 0:
            raise "Invalid syntax"
        
        return args[3:]

    def check_integer(self, line, line_num, scope):
        args = self.check_declaration(line)

        self.check_equation(args, line_num, scope)
                
    def check_equation(self, args, line_num, scope):
        operators = ['+', '-', '*', '/']
        i = 0

        for arg in args:
            if i % 2 == 0:
                try:
                    int(arg)
                except:
                    if arg[0].isalpha():
                        var = scope.get_variable(arg)

                        if not var:
                            raise Exception(f"variable {arg} at line {line_num} not found")
                        else:
                            if var["var_type"] != "int":
                                raise Exception(f"invalid variable type {var['var_type']} on line {line_num}")
            else:
                if arg not in operators:
                    raise Exception(f"Invalid syntax on line {line_num}")

    def check_string(self, line, line_num, scope):
        args = " ".join(self.check_declaration(line))

        if not args.startswith('"') and not args.endswith('"'):
            raise Exception(f"Invalid syntax on line {line_num}")

    def check_reassign(self, line, line_num, scope):
        args = line.split()

        if args[1] != '=':
            raise Exception(f"Invalid syntax on line {line_num}")

        var = scope.get_variable(args[0])

        if var:
            if var["var_type"] == "int":
                self.check_equation(args[2:], line_num, scope)
            elif var["var_type"] == "string":
                val = " ".join(args[2:])
                if not val.startswith('"') and not val.endswith('"'):
                    raise Exception(f"Invalid syntax on line {line_num}")
        else:
            raise Exception(f"variable {args[0]} at line {line_num} not found")

    def check_if(self, line, line_num, scope):
        pass

    def check_else(self, line, line_num, scope):
        pass

    def check_for(self, line, line_num, scope):
        args = " ".join(line.split()[1:-1])[1:-1].split(';')

        self.check_for_declaration(args[0].split(), line_num, scope)

    def check_for_declaration(self, args, line_num, scope):
        if len(args) != 4 or args[0] != "int" or args[2] != '=':
            raise Exception(f"Invalid syntax on line {line_num}")
        
        scope.variables.register("int", args[1], [args[3]])

    def check_while(self, line, line_num, scope):
        pass

    def check_method(self, line, line_num, scope):
        pass