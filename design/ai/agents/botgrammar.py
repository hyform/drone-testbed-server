from lark import Lark, inline_args, Transformer, v_args, Visitor

import sys
import json

class BotGrammar():

    # initialize
    def __init__(self, type):


        if type == 'designbot':

            # define boat grammar
            bot_grammar = r"""

                sentence: want | working | ping | NO | UNSATISFIED | HELP | SUGGESTION | "bot" want | "bot" working | "bot" ping | "bot" NO | "bot" UNSATISFIED | ITERATE | "bot" ITERATE | "bot" HELP | "bot" SUGGESTION
                want: ref? "want" want_cond+                                                            -> want
                working: "working" want_cond+                                                           -> working
                want_cond: PREFDIR? VARIABLE "of"? "than"? "as"? SIGNED_NUMBER? "and"?                        -> want_cond
                PREFDIR: "lower" | "higher" | "less" | "more" | "same"
                VARIABLE: "range" | "capacity" | "cost"
                ref: "@" REF_CHAR+ ":"?                                                                 -> reference
                REF_CHAR : LETTER
                    | DIGIT
                    | SPECIAL_CHAR
                NO: "no"
                UNSATISFIED: "unsatisfied"
                ITERATE: "iterate"
                HELP: "help"
                SUGGESTION: "suggestion"

                SPECIAL_CHAR: "_" | "{" | "}" | "~" | "!" | "#" | "$" | "%" | "^" | "&" | "*" | "(" | ")" | "-" | "+" | "="

                ?ping: "ping" ping_cond
                ping_cond: VARIABLE?                                                                    -> ping_var
                    | "status"                                                                          -> ping_status
                    | "satisfied" ref?                                                                  -> ping_satisfied
                    | "unsatisfied" VARIABLE?                                                           -> ping_unsatisfied
                    | "response" VARIABLE "of"? SIGNED_NUMBER?                                          -> ping_response
                    | "start"                                                                           -> ping_start


                string : ESCAPED_STRING

                %import common.LETTER
                %import common.DIGIT
                %import common.ESCAPED_STRING
                %import common.SIGNED_NUMBER
                %import common.WS
                %ignore WS

            """

            self.parser = Lark(bot_grammar, start='sentence', parser='lalr', transformer=BotTransformer())

        elif type == "opsbot":

            # define boat grammar
            bot_grammar = r"""

                sentence: want | working | ping | NO | UNSATISFIED | HELP | SUGGESTION | "bot" want | "bot" working | "bot" ping | "bot" NO | "bot" UNSATISFIED | ITERATE | "bot" ITERATE | "bot" HELP | "bot" SUGGESTION
                want: ref? "want" want_cond+ GEO*                                                       -> want
                working: "working" want_cond+                                                           -> working
                want_cond: PREFDIR? VARIABLE "of"? "than"? "as"? SIGNED_NUMBER? "and"?                  -> want_cond
                PREFDIR: "lower" | "higher" | "less" | "more" | "same"
                VARIABLE: "cost" | "profit" | "customers"
                ref: "@" REF_CHAR+ ":"?                                                                 -> reference
                REF_CHAR : LETTER
                    | DIGIT
                    | SPECIAL_CHAR
                GEO : "north" | "south" | "east" | "west"
                NO: "no"
                UNSATISFIED: "unsatisfied"
                ITERATE: "iterate"
                HELP: "help"
                SUGGESTION: "suggestion"

                SPECIAL_CHAR: "_" | "{" | "}" | "~" | "!" | "#" | "$" | "%" | "^" | "&" | "*" | "(" | ")" | "-" | "+" | "="

                ?ping: "ping" ping_cond
                ping_cond: VARIABLE?                                                                    -> ping_var
                    | "status"                                                                          -> ping_status
                    | "satisfied" ref?                                                                  -> ping_satisfied
                    | "unsatisfied" VARIABLE?                                                           -> ping_unsatisfied
                    | "response" VARIABLE "of"? SIGNED_NUMBER?                                          -> ping_response
                    | "start"                                                                           -> ping_start


                string : ESCAPED_STRING

                %import common.LETTER
                %import common.DIGIT
                %import common.ESCAPED_STRING
                %import common.SIGNED_NUMBER
                %import common.WS
                %ignore WS

            """

            self.parser = Lark(bot_grammar, start='sentence', parser='lalr', transformer=BotTransformer())


    def parse(self, s):
        return self.parser.parse(s)

    def get_json_of_chat(self, chat):
        try:
            res = self.parse(chat)
            json_str = json.dumps(res)
            json_obj =  json.loads(json_str)
            return json_obj
        except Exception as e:
            print(e)
        return None

# is there a better way ?
class BotTransformer(Transformer):

    def sentence(self, args):
        return args[0]

    def want(self, args):
        json_obj = {}
        json_obj['type'] = "want"
        json_obj['conditions'] = []
        for arg in args:
            json_obj['conditions'].append(arg)
        print("args", args)
        return json_obj

    def working(self, args):
        json_obj = {}
        json_obj['type'] = "working"
        json_obj['conditions'] = []
        for arg in args:
            json_obj['conditions'].append(arg)
        return json_obj

    def want_cond(self, args):
        return self.convert_to_json(args, 'want_cond')

    def ping_response_var(self, args):
        return self.convert_to_json(args, 'ping_response')

    def ping_var(self, args):
        json_obj = {}
        json_obj['type'] = "ping_variable"
        json_obj['variable'] = args[0].value
        return json_obj

    def ping_status(self, args):
        json_obj = {}
        json_obj['type'] = "ping_status"
        return json_obj

    def ping_satisfied(self, args):
        json_obj = {}
        json_obj['type'] = "ping_satisfied"
        json_obj['conditions'] = []
        for arg in args:
            json_obj['conditions'].append(arg)
        return json_obj

    def ping_response(self, args):
        json_obj = {}
        json_obj['type'] = "ping_response"
        for arg in args:
            json_obj[arg.type] = arg.value
        return json_obj

    def ping_unsatisfied(self, args):
        json_obj = {}
        json_obj['type'] = "ping_unsatisfied"
        for arg in args:
            json_obj['variable'] = arg.value
        return json_obj

    def ping_start(self, args):
        json_obj = {}
        json_obj['type'] = "ping_start"
        return json_obj

    def reference(self, args):
        ref_name = ""
        for arg in args:
            ref_name += arg.value
        json_obj = {}
        json_obj['type'] = "reference"
        json_obj['name'] = ref_name
        return json_obj

    def geo(self, args):
        geo_name = ""
        for arg in args:
            geo_name += arg.value
        json_obj = {}
        json_obj['type'] = "geo"
        json_obj['name'] = geo_name
        return json_obj

    def convert_to_json(self, args, type):
        var_name = args[0]
        var_value = args[1]
        json_obj = {}
        json_obj['type'] = type
        for arg in args:
            json_obj[arg.type] = arg.value
        return json_obj
