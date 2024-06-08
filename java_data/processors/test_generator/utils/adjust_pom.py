import argparse
import logging
import os
import xml.etree.ElementTree as ET
from subprocess import run

import pandas as pd
from tqdm import tqdm

# def remove_ns_prefix(elem):
#     for subelem in elem.iter():
#         if subelem.tag.startswith("{"):
#             subelem.tag = subelem.tag.split("}", 1)[1]
#     return elem


# def add_plugin_to_build(pom_file_path, new_plugins):
#     tree = ET.parse(pom_file_path)

#     root = tree.getroot()

#     # Define the namespaces
#     namespaces = {"mvn": "http://maven.apache.org/POM/4.0.0"}

#     # Find or create the <build> element
#     build_element = root.find("mvn:build", namespaces)
#     if build_element is None:
#         build_element = ET.SubElement(root, "build")
#     # Check if <directory> exists within <build>
#     directory_element = build_element.find("mvn:directory", namespaces)
#     if directory_element is None:
#         directory_element = ET.SubElement(build_element, "directory")
#         directory_element.text = "${project.basedir}/target"
#     else:
#         directory_element.text = "${project.basedir}/target"

#     # Find or create the <plugins> element
#     plugins_element = build_element.find("mvn:plugins", namespaces)
#     if plugins_element is None:
#         plugins_element = ET.SubElement(build_element, "plugins")

#     # Parse the new plugin XML string into an Element
#     for new_plugin in new_plugins:
#         new_plugin_element = ET.fromstring(new_plugin)
#         plugins_element.append(new_plugin_element)

#     root = remove_ns_prefix(root)
#     # Write the modified pom.xml back to file
#     modified_pom = ET.tostring(root, encoding="utf-8").decode("utf-8")

#     with open(pom_file_path, "w", encoding="utf-8") as f:
#         f.write(modified_pom)


def add_plugin_to_build(pom_file_path, new_plugins):
    # Parse the new plugin XML string

    new_plugin_elements = [
        ET.fromstring(new_plugin) for new_plugin in new_plugins
    ]

    # Function to ensure a tag exists
    def ensure_tag_exists(parent, tag_name):
        tag = parent.find(tag_name)
        if tag is None:
            tag = ET.SubElement(parent, tag_name)
        return tag

    def strip_namespace(element):
        for elem in element.iter():
            if "}" in elem.tag:
                elem.tag = elem.tag.split("}", 1)[1]

    # Parse the original pom.xml
    tree = ET.parse(pom_file_path)
    root = tree.getroot()
    # Strip namespaces from the root and all its descendants
    strip_namespace(root)
    # Ensure <build> and <plugins> tags exist
    build = ensure_tag_exists(root, "build")
    plugins = ensure_tag_exists(build, "plugins")

    # Check if the plugin already exists to avoid duplicates
    for new_plugin_element in new_plugin_elements:
        plugin_exists = any(
            plugin.find("artifactId").text
            == new_plugin_element.find("artifactId").text
            for plugin in plugins.findall("plugin")
        )
        if not plugin_exists:
            plugins.append(new_plugin_element)
        else:
            plugins.append(new_plugin_element)

    # Write the modified tree back to the original file
    tree.write(pom_file_path, encoding="utf-8", xml_declaration=True)

    # # To preserve formatting, you can use a library like `xml.dom.minidom`
    # from xml.dom.minidom import parseString

    # # Read the modified XML content
    # with open('pom.xml', 'r') as file:
    #     content = file.read()

    # # Pretty print and write back to the file
    # pretty_content = parseString(content).toprettyxml(indent="  ")
    # with open('pom.xml', 'w') as file:
    #     file.write(pretty_content)
    print("Plugins added successfully!")


pom_file_path = "/home/hieuvd/lvdthieu/code-generation/java_data/processors/test_generator/utils/test.xml"  # Path to your pom.xml file
new_plugins = [
    """
<plugin>
    <artifactId>maven-assembly-plugin</artifactId>
    <executions>
        <execution>
            <phase>package</phase>
            <goals><goal>single</goal></goals>
        </execution>
    </executions>
    <configuration>
        <descriptorRefs>
            <descriptorRef>jar-with-dependencies</descriptorRef>
        </descriptorRefs>
    </configuration>
</plugin>
""",
    #     """
    # <plugin>
    #     <groupId>org.apache.maven.plugins</groupId>
    #     <artifactId>maven-dependency-plugin</artifactId>
    #     <configuration>
    #         <outputDirectory>${project.build.directory}/lib</outputDirectory>
    #         <excludeTransitive>false</excludeTransitive>
    #         <stripVersion>false</stripVersion>
    #     </configuration>
    #     <executions>
    #         <execution>
    #             <id>copy-dependencies</id>
    #             <phase>package</phase>
    #             <goals>
    #                 <goal>copy-dependencies</goal>
    #             </goals>
    #         </execution>
    #     </executions>
    # </plugin>
    # """,
    #     """
    # <!-- Add LIB folder to classPath -->
    # <plugin>
    #     <groupId>org.apache.maven.plugins</groupId>
    #     <artifactId>maven-jar-plugin</artifactId>
    #     <version>2.4</version>
    #     <configuration>
    #         <archive>
    #             <manifest>
    #                 <addClasspath>true</addClasspath>
    #                 <classpathPrefix>lib/</classpathPrefix>
    #             </manifest>
    #         </archive>
    #     </configuration>
    # </plugin>
    # """,
]
# add_plugin_to_build(pom_file_path, new_plugins)


def main(args):
    print(f"Reading {args.input}")
    df = pd.read_parquet(args.input)
    print(f"Initializing list to store results")

    # for _, row in tqdm(df.iterrows()):
    #     repo = "_".join(row["proj_name"].split("_")[1:])
    #     working_dir = f"{args.base_dir}/{row['proj_name']}/{repo}"
    #     if os.path.exists(f"{working_dir}/pom.xml"):
    #         ori_pom_xml = f"{working_dir}/pom.xml".replace(
    #             "tmp-projects", "processed-projects"
    #         )
    #         cmd = (
    #             f"rm {working_dir}/pom.xml "
    #             f"&& cp {ori_pom_xml} {working_dir}/pom.xml"
    #         )
    #         result = run(cmd, shell=True, capture_output=True, text=True)
    #         if result.returncode != 0:
    #             logging.info(
    #                 f"Failed to copy {ori_pom_xml} to {working_dir}/pom.xml"
    #             )
    #     if os.path.exists(f"{working_dir}/loc.txt"):
    #         os.remove(f"{working_dir}/loc.txt")

    logger = logging.getLogger("adjust_pom")
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.FileHandler(f"{args.log_dir}/adjust_pom1.log"))

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Adjusting pom.xml"):

        repo = "_".join(row["proj_name"].split("_")[1:])
        working_dir = f"{args.base_dir}/{row['proj_name']}/{repo}"
        if os.path.exists(f"{working_dir}/loc.txt"):
            continue
        os.system(f"touch {working_dir}/loc.txt")
        pom_file_path = f"{working_dir}/pom.xml"
        if os.path.exists(pom_file_path):
            try:
                add_plugin_to_build(pom_file_path, new_plugins)
                cmd = f"cd {working_dir} && /home/hieuvd/apache-maven-3.6.3/bin/mvn clean install -DskipTests"
                result = run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    logger.error(f"Failed to compile {pom_file_path}")
                else:
                    logger.info(f"Compiled {pom_file_path}")

            except:
                logger.error(f"Failed to compile {pom_file_path}")

        else:
            logger.error(f"Failed to find {pom_file_path}")

    for _, row in df.iterrows():
        repo = "_".join(row["proj_name"].split("_")[1:])
        working_dir = f"{args.base_dir}/{row['proj_name']}/{repo}"
        if os.path.exists(f"{working_dir}/loc.txt"):
            os.system(f"rm {working_dir}/loc.txt")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", dest="input")
    parser.add_argument("--base-dir", dest="base_dir")
    parser.add_argument("--log-dir", dest="log_dir")
    args = parser.parse_args()
    main(args)
