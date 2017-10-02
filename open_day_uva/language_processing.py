
class LanguageProcessing:
    def __init__(self):
        pass

    def is_break(self, q):
        if (("stop" in q or "sleep" in q or "break") and ("another" in q or "a bit" in q or "now" in q or "a while" in q or "a second" in q or "me" in q or "i want" in q or "talking" in q)) or ("shut up" in q):
            return True
        return False

    def is_quit(self, q)
        if (("stop" in q or "quit" in q or "done" in q) and "conv" in q) or q == "stop" or q == "quit":
            return True

    def is_greeting(self, q):
        if ("hello" in q or "greeting" or "hi" or "nice to") and ("beth" in q):
            return True

    # Analyzes a sentence to extract some kind of instruction
    def get_command(self, q):

        command = {}
        return command