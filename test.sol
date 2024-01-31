program my_program 
let
    counter -> integer;
    result -> real;
    flag -> boolean;
    i -> integer;
begin
    prompt(counter)
    if counter >= 0 goto count
    if counter <= 0 goto print
    for i = 1 to 2 do
      log(result)
    end
    if result > 0 goto positive_label
    if result < 0 goto negative_label
    if result == 0 goto zero_label
    if result != 0 goto no_zero_label

count:
    result = counter * 10 / 3 - 3 ^ 2 + 2
print:
    log(counter)
positive_label:
    flag = true
negative_label:
    flag = false
zero_label:
    flag = false
no_zero_label:
    flag = true
    
finish
stop







