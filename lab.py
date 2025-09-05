num1 = int(input("Enter your first num: "))
op = input("Enter operator (+, -,*,/): ")
num2 = int(input("Enter your second num: "))
res = ()
if op == "+":
    res = num1 + num2
    print(res)

elif op == "-":
    res = num1 - num2
    print(res)
    
elif op == "*":
    res = num1 * num2
    print(res)
    
elif op == "/":
    res = num1 / num2
    print(res)
    