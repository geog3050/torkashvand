num_list = [23, 56, 12, 34, 67,23, 8, 6]
print("list of numbers: ", num_list)

for n in num_list:
    count = num_list.count(n)
    if count != 1:
        print("The list contains duplicate value")
        non_duplicate_list = list(set(num_list))
        print("The list without duplicate value: ", non_duplicate_list)
        break
    else:
        print("The list does not contain duplicate values")
        break
