import com.google.gson.*;
import flute.config.Config;
import flute.jdtparser.FileParser;
import flute.jdtparser.ProjectParser;
import org.eclipse.jdt.core.dom.CompilationUnit;
import org.eclipse.jdt.core.dom.TypeDeclaration;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
public class Main {
    private static ArrayList<ClassInfo> parseFile(String projectName, String projectPath, String filePath) {
        Config.autoConfigure(projectName, projectPath);
        ProjectParser projectParser = new ProjectParser(Config.PROJECT_DIR, Config.SOURCE_PATH, Config.ENCODE_SOURCE, Config.CLASS_PATH, Config.JDT_LEVEL, Config.JAVA_VERSION);
        FileParser fileParser = new FileParser(projectParser, new File(filePath), 0, 0);
        CompilationUnit cu = fileParser.getCu();
        int numClass = cu.types().size();
        ArrayList<ClassInfo> classInfos = new ArrayList<>();
        for (int i = 0; i < numClass; i++) {
            TypeDeclaration class_ = (TypeDeclaration) cu.types().get(i);
            try {
                classInfos.add(new ClassInfo(
                        filePath,
                        class_.toString(),
                        class_.resolveBinding().getName(),
                        class_.resolveBinding().getQualifiedName(),
                        class_.resolveBinding().isInterface() ? "" : class_.resolveBinding().getSuperclass().getQualifiedName()
                ));
            } catch (Exception e) {
                throw e;
            }
        }
        return classInfos;
    }
    private static HashMap<String, ArrayList<String>> readFromJsonFile(String filePath) {
        HashMap<String, ArrayList<String>> hashMap = new HashMap<>();
        try {
            FileReader fileReader = new FileReader(filePath);
            JsonParser jsonParser = new JsonParser();
            JsonElement jsonElement = jsonParser.parse(fileReader);
            if (jsonElement.isJsonObject()) {
                JsonObject jsonObject = jsonElement.getAsJsonObject();

                // Iterate over the entries
                for (String key : jsonObject.keySet()) {
                    JsonElement value = jsonObject.get(key);
                    hashMap.put(key, new ArrayList<String>());
                    // Check if the value is a JsonArray
                    if (value.isJsonArray()) {
                        JsonArray jsonArray = value.getAsJsonArray();

                        // Iterate over the array
                        for (JsonElement element : jsonArray) {
                            // Check if the element is a JsonPrimitive (string)
                            if (element.isJsonPrimitive()) {
                                String stringValue = element.getAsString();
                                hashMap.get(key).add(stringValue);
                            }
                        }
                    }
                }

            } else {
                System.out.println("Unexpected JSON structure. Expected an array.");
            }
            fileReader.close();
        } catch (IOException e) {
            e.printStackTrace();
        } catch (JsonParseException e) {
            System.out.println("Failed to parse JSON: " + e.getMessage());
        }
        return hashMap;
    }
    private static void storeToJsonFile(Object o, String outputFile) {
        Gson gson = new GsonBuilder().setPrettyPrinting().create();
        String json = gson.toJson(o);
        try (FileWriter writer = new FileWriter(outputFile)) {
            writer.write(json);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void main(String[] args) {
        Config.JAVAFX_DIR = "/var/data/lvdthieu/javafx-sdk-22/lib";
        // Parse args
        String filePath = args[0];
        String outputFile = args[1];

        HashMap<String, ArrayList<String>> projects = readFromJsonFile(filePath);
        ArrayList<Project> projectInfos = new ArrayList<>();
        int projectCount = 0;
        for (String projectPath : projects.keySet()) {
            projectCount += 1;
            ArrayList<String> javaFilePaths = projects.get(projectPath);
            String[] parts = projectPath.split("/");
            String projectName = parts[parts.length - 1];
            int javaFileCount = 0;
            int totalFile = javaFilePaths.size();
            for (String javaFilePath : javaFilePaths) {
//                System.out.println("Project Name: " + projectName + "\n" + "Project Path: " + projectPath + "\n" + "Java File Path: " + javaFilePath + "\n" + "---------------------------------------------");
                javaFileCount += 1;
                System.out.println("Processing file " + javaFileCount + "/" + totalFile + " in project "+ projectCount);
                try {
                    ArrayList<ClassInfo> classInfos = parseFile(projectName, projectPath, javaFilePath);
                    for (ClassInfo classInfo : classInfos) {
                        projectInfos.add(new Project(
                                projectName,
                                projectPath,
                                classInfo
                        ));
                    }
                } catch (Exception e) {
                    System.out.println(javaFilePath);
                }
            }
        }
//        System.out.println(projectInfos);

        storeToJsonFile(projectInfos, outputFile);
    }
}
