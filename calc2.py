def calculate(expression):
    expression = expression.replace(" ", "")

    while "(" in expression:
        start = expression.rfind("(")        
        end = expression.find(")", start)    
        inside = expression[start+1:end]    
        value = calculate(inside)            
        expression = expression[:start] + str(value) + expression[end+1:]

    tokens = []
    number = ""
    for char in expression:
        if char.isdigit():
            number += char
        else:
            tokens.append(int(number))
            tokens.append(char)
            number = ""
    if number:
        tokens.append(int(number))

    i = 0
    while i < len(tokens):
        if tokens[i] == "*":
            result = tokens[i-1] * tokens[i+1]
            tokens[i-1:i+2] = [result]
            i -= 1
        elif tokens[i] == "/":
            result = tokens[i-1] // tokens[i+1]   
            tokens[i-1:i+2] = [result]
            i -= 1
        else:
            i += 1

    i = 0
    while i < len(tokens):
        if tokens[i] == "+":
            result = tokens[i-1] + tokens[i+1]
            tokens[i-1:i+2] = [result]
            i -= 1
        elif tokens[i] == "-":
            result = tokens[i-1] - tokens[i+1]
            tokens[i-1:i+2] = [result]
            i -= 1
        else:
            i += 1

    return tokens[0]

user_input = input("Введіть вираз: ")
print("Результат:", calculate(user_input))
