public class Project {
    String projectName;
    String projectPath;
    ClassInfo classInfos;
    public Project(String projectName, String projectPath, ClassInfo classInfos) {
        this.projectName = projectName;
        this.projectPath = projectPath;
        this.classInfos = classInfos;
    }
}
