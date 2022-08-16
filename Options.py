import os
import Io
import Global
import argparse

# description of an option and what to do with it
class Option(object):
  def __init__(self, name:str, prompt:str, value) -> None:
        self.name = name            # option name
        self.prompt = prompt        # prompt for interactive entry
        self.value = value          # thing to set
        self.getFunc = None         # function to get value interactively
        self.type = None

class StringOption(Option):
    def __init__(self, name:str, prompt:str, value:str):
        super().__init__(name, prompt, value)
        self.getFunc = Io.getStr
        self.type = type(str)

class BoolOption(Option):
    def __init__(self, name:str, prompt:str, value:bool):
        super().__init__(name, prompt, value)
        self.getFunc = Io.getBool
        self.type = type(bool)

fightFlush:BoolOption = BoolOption("flush", "Flush typeahead during battle: ", False)
jump:BoolOption = BoolOption("jump", "Show position only at end of run: ", False)
slowInvent:BoolOption = BoolOption("step", "Do inventories one line at a time: ", False)
askMe:BoolOption = BoolOption("askme", "Ask me about unidentified things: ", False)
fruitName:StringOption = StringOption("fruit", "Fruit: ", "Slime mold")
whoami:StringOption = StringOption("name", "Name: ", "player")
fileName:StringOption = StringOption("file", "Save file: ", os.path.join(".", "data", "rogue.save"))

optionList = [
    fightFlush,
    jump,
    slowInvent,
    askMe,
    fruitName,
    whoami,
    fileName
]

# option:
# print and then set options from the terminal
def option() -> None:
    global optionList

    Global.helpWindow.clear()
    Global.helpWindow.touchwin()

    # Display current values of options
    for opt in optionList:
        Global.helpWindow.addstr(f"{opt.prompt}{opt.value}\n")

    # Set values
    Global.helpWindow.move(0, 0)
    index:int = 0
    while True:
        opt = optionList[index]
        Global.helpWindow.addstr(index, 0, f"{opt.prompt}")
        Global.helpWindow.standout()
        type, opt.value = opt.getFunc(opt.value, Global.helpWindow)
        Global.helpWindow.standend()
        Global.helpWindow.addstr(index, 0, f"{opt.prompt}{opt.value}")
        if type == Io.InputValueType.Quit:
            break
        elif type == Io.InputValueType.Minus:
            index -= 1
            if index < 0:
                index = len(optionList) -1
            continue
        else:
            index += 1
            index %= len(optionList)

    # Switch back to original screen
    Global.helpWindow.addstr(Global.cursesLines - 1, 0, "--Press space to continue--")
    Global.helpWindow.refresh()
    Io.waitFor(" ")
    Global.playerWindow.clearok(True)
    Global.playerWindow.touchwin()
    Global.after = False

# parseOption:
def parseOption(string:str):
    global optionList

    parser = argparse.ArgumentParser(prog="Rogue options is are")
    for option in optionList:
        if option.type == type(bool):
            parser.add_argument(f"--{option.name}", help=option.prompt, action="store_true")
        else:
            parser.add_argument(f"--{option.name}", help=option.prompt)

    args = parser.parse_args(string.split(" "))

    for arg in args:
        print(arg)
