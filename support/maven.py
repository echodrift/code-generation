"""Run maven
"""

from subprocess import run

import pandas as pd

test = pd.read_parquet("/home/hieuvd/lvdthieu/test.parquet")
test_projects = test["proj_name"].unique()

for project in test_projects:

    REPO = "_".join(project.split("_")[1:])

    cmd = (
        f"cd /home/hieuvd/lvdthieu/repos/tmp-projects/{project}/{REPO} "
        + "&& /home/hieuvd/apache-maven-3.6.3/bin/mvn clean compile"
    )
    output = run(cmd, shell=True, text=True, capture_output=True, check=True)
    if "BUILD FAILURE" in output.stdout:
        with open("/home/hieuvd/lvdthieu/log.txt", "a", encoding="utf-8") as f:
            f.write(project + "COMPILE FAILURE" + "\n")
    else:
        with open("/home/hieuvd/lvdthieu/log.txt", "a", encoding="utf-8") as f:
            f.write(project + "COMPILE SUCCESS" + "\n")
    # cmd = (
    #     f"rm -rf /home/hieuvd/lvdthieu/repos/tmp-projects/{project}"
    #     f" && cp -r /home/hieuvd/lvdthieu/repos/processed-projects/{project}"
    #     f" /home/hieuvd/lvdthieu/repos/tmp-projects/{project}"
    # )
