import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from main import AIPROSCore

core = AIPROSCore()

print("=== CHAT TEST ===")
print(core.process_input("how are you"))

print("\n=== INFO TEST ===")
print(core.process_input("what is euro truck simulator 2"))

print("\n=== COMMAND TEST ===")
print(core.process_input("open notepad"))

print("\n=== GAME TEST ===")
print(core.process_input("open ets2"))
