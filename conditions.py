from utils import gen_hex


class Conditions:
    operators = [">", ">=", "<", "<=", "==", "!="]

    def __init__(self, scope):
        self.conditions = {}
        self.conditions_awaiting_end_line = []
        self.scope = scope

    def register(self, line, start_line, scope):
        condition_address = gen_hex()

        while condition_address in self.conditions.keys():
            condition_address = gen_hex()

        self.conditions[condition_address] = {
            "type": line[0],
            "scope": scope,
            "args": line[1:-1],
            "start_line": start_line,
            "end_line": None
        }

        self.conditions_awaiting_end_line.append(condition_address)

        return condition_address
    
    def get(self, address):
        return self.conditions.get(address)

    def read_condition(self, address):
        condition = self.conditions.get(address)

        if condition:
            parser = getattr(self, f"parse_{condition['type']}")
            return parser(condition)

    def register_end_line(self, end_line):
        if len(self.conditions_awaiting_end_line) > 0:
            condition = self.conditions[self.conditions_awaiting_end_line.pop(-1)]
            condition["end_line"] = end_line

    @property
    def awaiting_end_line(self):
        return len(self.conditions_awaiting_end_line) > 0

    def parse_if(self, data):
        scope = data["scope"]

        condition = []
        for arg in data["args"]:
            if arg[0].isalpha():
                var = scope.get_variable(arg)
                condition.append(var["value"])
            else:
                condition.append(arg)
        
        result = eval(" ".join(condition))
        data["result"] = result

        return result

    def parse_else(self, arg):
        return True