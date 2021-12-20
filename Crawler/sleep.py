fail_cnt = 0
try:
    a = 2
    b = 0
    c = a/b
except Exception as e:
    fail_cnt +=1
    pass

print(fail_cnt)