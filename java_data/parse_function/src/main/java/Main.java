import flute.config.Config;
import org.eclipse.jdt.core.dom.*;

import java.io.IOException;
import java.nio.file.*;

import java.util.List;
import java.util.Map;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashSet;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class Main {
    public static CompilationUnit parse(String source) {
        ASTParser parser = ASTParser.newParser(AST.getJLSLatest());
        parser.setSource(source.toCharArray());
        parser.setKind(ASTParser.K_COMPILATION_UNIT);
        return (CompilationUnit) parser.createAST(null);
    }

    public static class MethodFinderVisitor extends ASTVisitor {
        private final String methodName;
        private MethodDeclaration foundMethod;
        private String methodRaw;

        public MethodFinderVisitor(String methodName) {
            this.methodName = methodName;
        }

        @Override
        public boolean visit(MethodDeclaration node) {
            if (node.getName().getIdentifier().equals(methodName)) {
                foundMethod = node;
                methodRaw = node.toString();
            }
            return super.visit(node);
        }

        public MethodDeclaration getFoundMethod() {
            return foundMethod;
        }

        public String getMethodRaw() {
            return methodRaw;
        }
    }

    public static class Visitor extends ASTVisitor {
        private final HashMap<String, String> variables = new HashMap<>();
        private final List<String> methodNames = new ArrayList<>();
    
        @Override
        public boolean visit(FieldDeclaration node) {
            for (Object fragment : node.fragments()) {
                VariableDeclarationFragment varFragment = (VariableDeclarationFragment) fragment;
                variables.put(varFragment.getName().getIdentifier(), node.getType().toString());
            }
            return super.visit(node);
        }

        @Override
        public boolean visit(VariableDeclarationFragment node) {
            if (node.getParent() instanceof VariableDeclarationStatement) {
                VariableDeclarationStatement declaration = (VariableDeclarationStatement) node.getParent();
                variables.put(node.getName().getIdentifier(), declaration.getType().toString());
            }
            return super.visit(node);
        }

        @Override
        public boolean visit(SingleVariableDeclaration node) {
            variables.put(node.getName().getIdentifier(), node.getType().toString());
            return super.visit(node);
        }

        @Override
        public boolean visit(QualifiedName node) {
            if (node.getQualifier() instanceof SimpleName) {
                String typeName = node.getQualifier().getFullyQualifiedName();
                String variableName = node.getName().getFullyQualifiedName();
                variables.put(variableName, typeName);
            }
            return super.visit(node);
        }

        @Override
        public boolean visit(MethodInvocation node) {
            methodNames.add(node.getName().getIdentifier());
            return super.visit(node);
        }

        @Override
        public boolean visit(MethodDeclaration node) {
            methodNames.add(node.getName().getIdentifier());
            return super.visit(node);
        }

        public List<String> getMethodNames() {
            return methodNames;
        }

        public HashMap<String, String> getVariables() {
            return variables;
        }
    }

    public static void main(String[] args) {
        Config.JAVAFX_DIR = "/home/hieuvd/lvdthieu/javafx-jmods-17.0.10";
        String sourcePath = args[0];
        String methodName = args[1];
        try {
            String source = new String(Files.readAllBytes(Paths.get(sourcePath)));
            CompilationUnit funcCU = parse(source);

            MethodFinderVisitor visitor = new MethodFinderVisitor(methodName);
            funcCU.accept(visitor);

            MethodDeclaration foundMethod = visitor.getFoundMethod();
            
            if (foundMethod != null) {
                String methodRaw = visitor.getMethodRaw();
                Visitor contentVisitor = new Visitor();
                funcCU.accept(contentVisitor);
                List<String> methodNames = contentVisitor.getMethodNames();
                HashMap<String, String> variables = contentVisitor.getVariables();
                
                // Filter method name not in target method
                LinkedHashSet<String> methodNamesInTargetMethod = new LinkedHashSet<>();
                for (String name : methodNames) {
                    Pattern pattern = Pattern.compile("\\." + name + "\\(");
                    Matcher matcher = pattern.matcher(methodRaw);
                    if (matcher.find()) {
                        methodNamesInTargetMethod.add(name);
                    }
                }
                // Filter variable name not in target method
                LinkedHashSet<String> fieldNamesInTargetMethod = new LinkedHashSet<>();
                LinkedHashSet<String> typeNamesInTargetMethod = new LinkedHashSet<>();
                for (Map.Entry<String, String> mapElement : variables.entrySet()) {
                    Pattern pattern = Pattern.compile("\\b" + mapElement.getKey() + "\\b");
                    Matcher matcher = pattern.matcher(methodRaw);
                    if (matcher.find()) {
                        fieldNamesInTargetMethod.add(mapElement.getKey());
                        typeNamesInTargetMethod.add(mapElement.getValue());
                    }
                }   
                System.out.println("Types: " + typeNamesInTargetMethod);
                System.out.println("Methods: " + methodNamesInTargetMethod);
                System.out.println("Fields: " + fieldNamesInTargetMethod);

            } else {
                System.out.println("Method not found: " + methodName);
            }
        } catch (IOException e) {
            System.out.println(e.getMessage());
        } catch (Exception e) {
            System.out.println(e.getMessage());
        }    
    }
}
