import os
for project in os.listdir("/home/hieuvd/lvdthieu/repos/processed-projects"):

    name = '_'.join(project.split('_')[1:])
    
    cmd = (f"cd /home/hieuvd/lvdthieu/repos/processed-projects/{project}/{name} " +
           "&& /home/hieuvd/apache-maven-3.6.3/bin/mvn clean compile")
    os.system(cmd)
    