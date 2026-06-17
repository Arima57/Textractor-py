from textractor_py import Textractor

test = Textractor()
test.attach(6328)
print("attached, listening...")

for line in test.listen(hook="HW-4*14", pid=6328):
    print(line)