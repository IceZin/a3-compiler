from utils import gen_hex


class Methods:
    def __init__(self):
        self.methods = {}
        self.methods_call = {}
        self.register("show", ["value"], self.show)

    def register(self, name, args, pointer):
        if name in self.methods.keys():
            return
        
        self.methods[name] = {
            "args": args,
            "pointer": pointer
        }

    def register_call(self, scope):
        call_address = gen_hex()

        while call_address in self.methods_call.keys():
            call_address = gen_hex()

        self.methods_call[call_address] = {
            "scope": scope,
        }

        return call_address

    def run(self, line, call_address):
        scope = self.methods_call.get(call_address, {}).get("scope")
        method = self.methods.get(line.split("(")[0])
        args = line.split("(")[1][:-1].split(", ")
        args_parsed = []

        for arg in args:
            if arg.startswith('"'):
                args_parsed.append(arg[1:-1])
            elif arg[0].isalpha():
                var = scope.get_variable(arg)
                if var["var_type"] == "int":
                    args_parsed.append(float(var["value"]))
                else:
                    args_parsed.append(var["value"])
            elif arg[0].isnumeric():
                args_parsed.append(int(arg))

        if method:
            method["pointer"](*args_parsed)

    def show(self, value):
        print(value)