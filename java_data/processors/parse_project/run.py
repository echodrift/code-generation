import subprocess

import pandas as pd
from tqdm import tqdm

base_dir = "/data/hieuvd/lvdthieu/repos/processed-projects"
parse_project = "/home/hieuvd/lvdthieu/parse_project"
# projects = [
#     # "PlexPt_chatgpt-java",
#     # "Pay-Group_best-pay-sdk",
#     # "eirslett_frontend-maven-plugin",
#     # "obsidiandynamics_kafdrop",
#     # "DerekYRC_mini-spring",
#     # "houbb_sensitive-word",
#     # "google_truth",
#     # "joelittlejohn_jsonschema2pojo",
#     # "Kong_unirest-java",
#     # "qiujiayu_AutoLoadCache",
#     # "ainilili_ratel",
#     # "logfellow_logstash-logback-encoder",
#     # "elunez_eladmin",
#     # "PlayEdu_PlayEdu",
#     # "javamelody_javamelody",
#     # "subhra74_snowflake",
#     # "jeecgboot_jeecg-boot",
#     # "mapstruct_mapstruct",
#     # "spring-cloud_spring-cloud-gateway",
#     # "docker-java_docker-java",
#     # "YunaiV_ruoyi-vue-pro",
#     # "zhkl0228_unidbg",
#     # "pmd_pmd",
#     # "graphhopper_graphhopper",
#     # "jitsi_jitsi",
#     # "orientechnologies_orientdb",
# ]

class_path = "." f":'{parse_project}/target/dependency/*'"

for project in tqdm(projects, total=len(projects), desc="Parsing"):
    cmd = (
        f"cd {parse_project}/target/classes "
        f"&& java -cp {class_path} "
        "Main "
        f"{base_dir} "
        f"{project}"
    )
    try:
        subprocess.run(cmd, shell=True)
    except:
        print("<encounter_error>", project)
