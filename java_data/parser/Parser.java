import org.eclipse.jdt.core.dom.AST;
import org.eclipse.jdt.core.dom.ASTParser;
import org.eclipse.jdt.core.dom.ASTVisitor;
import org.eclipse.jdt.core.dom.CompilationUnit;
import org.eclipse.jdt.core.dom.SimpleName;
import org.eclipse.jdt.core.dom.VariableDeclarationFragment;
import org.eclipse.jdt.core.dom.MethodDeclaration;
import java.util.*;
import java.io.FileReader;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.FileNotFoundException;


public class Parser {
    public static void parseFile(String filePath) {
        try {
            FileReader file = new FileReader(filePath);
            BufferedReader reader = new BufferedReader(file);

            String source = "";
            String line = reader.readLine();

            while (line != null) {
                source += (line + '\n');
                line = reader.readLine();
            }
            
            ASTParser parser = ASTParser.newParser(AST.JLS3);
            parser.setKind(ASTParser.K_COMPILATION_UNIT);
            parser.setSource(source.toCharArray());
            parser.setResolveBindings(true);
            CompilationUnit cu = (CompilationUnit) parser.createAST(null);

            cu.accept(new ASTVisitor() {

                @Override
                public boolean visit(MethodDeclaration node) {
                    return true;
                }

                @Override
                public void endVisit(MethodDeclaration node) {
                    System.out.println("Method " + node.getName().getFullyQualifiedName() + " is visited");
                }

            });
        } catch (FileNotFoundException e) {
            System.out.println(e);
        } catch (IOException e) {
            System.out.println(e);
        }
    }
    public static void main(String[] args) {
        String filePath = args[0];
        parseFile(filePath);
    }
}
    // public static void main(String[] args) {
    //     String projectName = args[0]
    //     IWorkspaceRoot root = ResourcesPlugin.getWorkspace().getRoot();
    //     IProject project = root.getProject(projectName);
    //     project.create(null);
    //     project.open(null);
    //     IProjectDescription description = project.getDescription();
    //     description.setNatureIds(new String[] { JavaCore.NATURE_ID });
    //     project.setDescription(description, null);
    //     IJavaProject javaProject = JavaCore.create(project); 
    //     ASTParser parser = ASTParser.newParser(AST.JLS8);
    //     parser.setKind(ASTParser.K_COMPILATION_UNIT);
    //     parser.setProject(javaProject);
    // }
// }