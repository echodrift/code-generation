import org.eclipse.jdt.core.*;
import org.eclipse.jdt.core.dom.*;
import java.util.*;

public class JavaParser {
    public static void main(String[] args) throws JavaModelException {
        // Create a Java project
        IJavaProject project = JavaCore.create(ResourcesPlugin.getWorkspace().getRoot().getProject("/data/hieuvd/lvdthieu/maven_projects/zxing_zxing"));

        // Traverse compilation units
        for (IPackageFragment pkg : project.getPackageFragments()) {
            for (ICompilationUnit unit : pkg.getCompilationUnits()) {
                // Parse compilation unit
                ASTParser parser = ASTParser.newParser(AST.JLS8);
                parser.setSource(unit);
                CompilationUnit astRoot = (CompilationUnit) parser.createAST(null);

                // Traverse AST and print class and method names
                astRoot.accept(new ASTVisitor() {
                    @Override
                    public boolean visit(TypeDeclaration node) {
                        System.out.println("Class: " + node.getName());
                        return true;
                    }

                    @Override
                    public boolean visit(MethodDeclaration node) {
                        System.out.println("Method: " + node.getName());
                        return true;
                    }
                });
            }
        }
    }
}
