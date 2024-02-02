from consts import Config

class Utils:
   @classmethod
   def snake_case(cls, string: str) -> str:
    """
    Converts the given string into snake case.
    THIS IS A ONE-WAY FUNCTION. Converting back from snake case is not foolproof.
    """
    string = string.lower()
    string = string.replace(' ', '_')
    string = ''.join(char for char in string if Config.FILE_RE.match(char))
    # Ensure that we don't have any double underscores as a result
    while '__' in string:
        string = string.replace('__', '_')
    return string