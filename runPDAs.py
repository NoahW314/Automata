from textBasedPDA import PushDownAutomaton

PDA = PushDownAutomaton("TestPDA.txt")
PDA.runAcceptOnString("0011")

# PDA = PushDownAutomaton("NestedCFG.txt")
# PDA.runAcceptOnString("(()())()")

# PDAtoCFG = PushDownAutomaton("PDAtobeCFG.txt")
# CFGrules = PushDownAutomaton.convertToCFG(PDAtoCFG)
# for rule in CFGrules:
#     print(rule)