from lark import Lark, exceptions

with open("email_grammar.lark", 'r') as f:
    grammar_text = f.read()

email_parser = Lark(grammar_text, parser="lalr", start="start")

def validate_email_address(email):
    try:
        email_parser.parse(email)
        return True
    except exceptions.LarkError:
        return False
