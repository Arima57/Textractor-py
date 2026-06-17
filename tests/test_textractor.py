from textractor_py import textractor

test = textractor()
test.attach(2764)
print("attached, listening...")

for line in test.listen(hook="HW-4*14", pid=2764):
    print(line)