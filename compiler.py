from random import random
from checker import Checker
from conditions import Conditions
from loops import Loops
from methods import Methods
from scope import Scope
from utils import gen_hex


class Compiler:
    def __init__(self, path):
        self.checker = Checker()
        self.conditions = Conditions(self)
        self.loops = Loops(self)
        self.methods = Methods()
        self.declarations = {
            "int": self.checker.check_integer,
            "string": self.checker.check_string
        }
        self.conditions_checker = {
            "if": self.checker.check_if,
            "else": self.checker.check_else
        }
        self.loops_checker = {
            "for": self.checker.check_for,
            "while": self.checker.check_while
        }
        self.methods_checker = {
            "show": self.checker.check_method
        }
        self.scopes = {}
        self.steps = []

        self.code = open(path, 'r')
        self.line = None
        self.line_count = 0
        self.expected_ends = []

        self.scope = Scope("global", gen_hex())

    def compile(self):
        while True:
            self.line = self.code.readline()
            self.line_count += 1

            if not self.line:
                break

            if len(self.line.split()) == 0:
                self.steps.append({
                    "type": "blank",
                    "line": self.line_count
                })
                continue

            if self.line.split()[0] == "end":
                if len(self.expected_ends) > 0:
                    self.expected_ends.pop()(self.line_count)

                    self.scope = self.scope.parent
                    self.checker.decrease_expected_spaces()

                    self.steps.append({
                        "type": "end",
                        "line": self.line_count
                    })
                    
                    continue
                else:
                    raise Exception(f"'end' was not expected on line {self.line_count}")

            line_class, check = self.classify()

            if line_class == "condition" and self.line.split()[0] == "else":
                self.checker.decrease_expected_spaces()
                self.scope = self.scope.parent

                if self.conditions.awaiting_end_line:
                    self.conditions.register_end_line(self.line_count)

            valid_identation = self.checker.check_identation(self.line)

            if not valid_identation:
                raise Exception(
                    f"Invalid identation, expected {self.checker.expected_spaces} spaces on line {self.line_count}"
                )
            
            check(self.line, self.line_count, self.scope)

            if line_class == "condition":
                self.checker.increase_expected_spaces()
                self.scope = self.scope.create_scope("cond")
                condition_address = self.conditions.register(self.line.split(), self.line_count, self.scope)

                if self.line.split()[0] == "if":
                    self.expected_ends.append(self.conditions.register_end_line)

                self.steps.append({
                    "args": self.line.split(),
                    "type": line_class,
                    "line": self.line_count,
                    "runner": self.conditions.read_condition,
                    "data": {
                        "condition_address": condition_address
                    }
                })
            elif line_class == "declaration":
                args = self.line.split()
                self.scope.variables.register(args[0], args[1], args[3:])

                self.steps.append({
                    "args": [args[1]],
                    "type": line_class,
                    "line": self.line_count,
                    "runner": self.scope.read_variable
                })
            elif line_class == "loop":
                self.checker.increase_expected_spaces()
                self.scope = self.scope.create_scope("loop")
                loop_address = self.loops.register(self.line.split(), self.line_count, self.scope)

                self.expected_ends.append(self.loops.register_end_line)

                self.steps.append({
                    "args": self.line.split(),
                    "type": line_class,
                    "line": self.line_count,
                    "runner": self.loops.read_loop,
                    "data": {
                        "loop_address": loop_address
                    }
                })
            elif line_class == "reassign":
                reassign_address = self.scope.variables.register_reassign(self.scope)

                self.steps.append({
                    "args": self.line.split(),
                    "type": line_class,
                    "line": self.line_count,
                    "runner": self.scope.reassign_variable,
                    "data": {
                        "reassign_address": reassign_address
                    }
                })
            elif line_class == "method":
                call_address = self.methods.register_call(self.scope)
                self.steps.append({
                    "args": self.line.split(),
                    "type": line_class,
                    "line": self.line_count,
                    "runner": self.methods.run,
                    "data": {
                        "call_address": call_address
                    }
                })
            else:
                self.steps.append({
                    "type": "wip",
                    "line": self.line_count
                })

            self.scope.add_line(self.line_count)

    def run(self):
        running_loop = None
        running_step = 0

        while True:
            if running_step >= len(self.steps):
                break

            if running_loop and running_step == running_loop["end_line"] - 1:
                running_step = running_loop["start_line"] - 1

            step = self.steps[running_step]

            step_type = step["type"]

            if step_type in ["blank", "end", "wip"]:
                running_step += 1
                continue

            step_args = step["args"]
            step_data = step.get("data")

            if step_type == "declaration":
                step["runner"](step_args[0])
            elif step_type == "reassign":
                step["runner"](step_args, step_data["reassign_address"])
            elif step_type == "condition":
                condition = self.conditions.get(step_data["condition_address"])
                condition_end_line = condition["end_line"]
                condition_end_step = self.steps[condition_end_line - 1]

                if not step_data.get("run", True):
                    running_step = condition_end_line
                    continue

                result = step["runner"](step_data["condition_address"])

                if condition_end_step["type"] == "condition":
                    condition_end_step["data"]["run"] = not result

                if result:
                    pass
                else:
                    running_step = condition_end_line - 1
                    continue
            elif step_type == "loop":
                loop = self.loops.get(step_data["loop_address"])

                result = step["runner"](step_data["loop_address"])

                if result:
                    running_loop = loop
                else:
                    running_step = loop["end_line"] - 1
                    running_loop = None
                    continue
            elif step_type == "method":
                step["runner"](" ".join(step_args), step_data["call_address"])

            running_step += 1

    def show_variables(self, scope):
        print(scope.name)
        print(scope.variables.keys())

        for child_scope in scope.scopes.values():
            self.show_variables(child_scope)
    
    def add_scope(self, name):
        scope_key, scope_data = self.create_scope(name)
        self.get_current_scope()["scopes"][scope_key] = scope_data
        self.scope_path.append(scope_key)

    def classify(self):
        first_arg = self.line.split()[0]

        if first_arg in self.declarations.keys():
            return "declaration", self.declarations.get(first_arg)
        elif first_arg in self.conditions_checker.keys():
            return "condition", self.conditions_checker.get(first_arg)
        elif first_arg in self.loops_checker.keys():
            return "loop", self.loops_checker.get(first_arg)
        elif '(' in first_arg and first_arg.split("(")[0] in self.methods_checker.keys():
            return "method", self.checker.check_method
        elif self.scope.get_variable(first_arg):
            return "reassign", self.checker.check_reassign
        
        return None, None

    def read_declaration(self):
        pass

    def read_condition(self):
        pass

    def read_loop(self):
        pass

    def read_method(self):
        pass

    def check_integer(self, arg):
        pass