from utils import gen_hex


class Loops:
    operators = [">", ">=", "<", "<=", "==", "!="]

    def __init__(self, scope):
        self.loops = {}
        self.loops_awaiting_end_line = []
        self.scope = scope

    def register(self, line, start_line, scope):
        loop_address = gen_hex()

        while loop_address in self.loops.keys():
            loop_address = gen_hex()

        self.loops[loop_address] = {
            "type": line[0],
            "scope": scope,
            "args": line[1:-1],
            "start_line": start_line,
            "end_line": None
        }

        self.loops_awaiting_end_line.append(loop_address)

        return loop_address
    
    def get(self, address):
        return self.loops.get(address)

    def read_loop(self, address):
        loop = self.loops.get(address)

        if loop:
            parser = getattr(self, f"parse_{loop['type']}")
            return parser(loop)

    def register_end_line(self, end_line):
        if len(self.loops_awaiting_end_line) > 0:
            loop = self.loops[self.loops_awaiting_end_line.pop(-1)]
            loop["end_line"] = end_line

    @property
    def awaiting_end_line(self):
        return len(self.loops_awaiting_end_line) > 0

    def parse_for(self, data):
        scope = data["scope"]
        args = " ".join(data["args"])[1:-1].split("; ")

        var_name = args[0].split()[1]
        var = scope.get_variable(var_name)

        if var["value"] is None:
            scope.read_variable(var_name)
        else:
            raw_equation = args[2].split()
            scope.reassign_variable(raw_equation, None)
        
        raw_condition = args[1]
        condition = []

        for arg in raw_condition.split():
            if arg[0].isalpha():
                var = scope.get_variable(arg)
                condition.append(var["value"])
            else:
                condition.append(arg)

        result = eval(" ".join(condition))
        return result

    def parse_while(self, data):
        scope = data["scope"]

        condition = []
        for arg in data["args"]:
            if arg[0].isalpha():
                var = scope.get_variable(arg)
                condition.append(var["value"])
            else:
                condition.append(arg)
        
        result = eval(" ".join(condition))
        return result