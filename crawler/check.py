# import re
# def check_duplicates(file_url: str):
#     std = lambda x: x.replace('\\n', '').replace('\\t1', '').replace('\n', '')
#     with open(file_url, "r") as f:
#         java_proj_url = map(std, f.readlines())
    
#     return set(java_proj_url)

# x1 = check_duplicates("/data/hieuvd/lvdthieu/maven_projects/uncompilable.txt")
# x2 = check_duplicates("/data/hieuvd/lvdthieu/maven_projects/compilable.txt")

# x1.remove('')
# x2.remove('')
# print("/data/hieuvd/lvdthieu/maven_projects/compilable.txt" in x1)
# print(len(x2))

# print(len(x1 | x2))
    
