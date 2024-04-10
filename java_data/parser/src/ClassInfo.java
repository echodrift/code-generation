public class ClassInfo {
    String filePath;
    String sourceCode;
    String className;
    String classQualifiedName;
    String extendedClassQualifiedName;
    public ClassInfo(String filePath, String sourceCode, String className, String classQualifiedName, String extendedClassQualifiedName) {
        this.filePath = filePath;
        this.sourceCode = sourceCode;
        this.className = className;
        this.classQualifiedName = classQualifiedName;
        this.extendedClassQualifiedName = extendedClassQualifiedName;
    }
}
