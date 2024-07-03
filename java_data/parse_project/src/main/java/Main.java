import flute.config.Config;
import flute.utils.file_processing.FileProcessor;
import me.tongfei.progressbar.ProgressBar;

import org.eclipse.jdt.core.JavaCore;
import org.eclipse.jdt.core.dom.*;
import org.eclipse.jdt.core.dom.rewrite.ASTRewrite;
import org.eclipse.jface.text.Document;
import org.eclipse.text.edits.TextEdit;

import com.google.gson.*;

import java.io.File;
import java.io.OutputStreamWriter;
import java.io.FileOutputStream;
import java.io.Writer;
import java.nio.file.*;

import java.util.Hashtable;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import java.util.List;
import java.util.ArrayList;
import java.util.logging.Level;
import java.util.logging.Logger;

public class Main {
    private static class Visitor extends ASTVisitor {
        private String relativePath;
        private String currentClassName;
        private JsonArray fields = new JsonArray();
        private JsonArray methods = new JsonArray();

        public Visitor(String relativePath) {
            super();
            this.relativePath = relativePath;
        }

        @Override
        public boolean visit(TypeDeclaration node) {
            currentClassName = node.getName().toString();
            return super.visit(node);
        }

        @Override
        public void endVisit(TypeDeclaration node) {
            currentClassName = null;
            super.endVisit(node);
        }

        @Override
        public boolean visit(FieldDeclaration node) {
            // Get the type of the field
            String type = node.getType().toString();

            // Get the modifiers of the field
            String modifiers = "";
            for (Object modifier : node.modifiers()) {
                modifiers += modifier.toString() + " ";
            }
            modifiers = modifiers.replaceAll("\\s+$", "");

            for (Object fragment : node.fragments()) {
                VariableDeclarationFragment varFrag = (VariableDeclarationFragment) fragment;
                String name = varFrag.getName().toString();
                JsonObject field = new JsonObject();
                field.addProperty("relative_path", relativePath);
                field.addProperty("class", currentClassName);
                field.addProperty("type", type);
                field.addProperty("modifiers", modifiers);
                field.addProperty("name", name);
                field.addProperty("raw", node.toString());
                fields.add(field);
            }
            return super.visit(node);
        }

        @Override
        public boolean visit(MethodDeclaration node) {
            JsonObject method = new JsonObject();
            method.addProperty("relative_path", relativePath);
            method.addProperty("class", currentClassName);
            String name = node.getName().toString();
            method.addProperty("name", name);
            String returnType = node.getReturnType2() != null ? node.getReturnType2().toString() : "void";
            method.addProperty("return_type", returnType);
            String modifiers = "";
            for (Object modifier : node.modifiers()) {
                modifiers += modifier.toString() + ' ';
            }
            modifiers = modifiers.replaceAll("\\s+$", "");
            method.addProperty("modifiers", modifiers);
            JsonArray parameters = new JsonArray();
            for (Object param : node.parameters()) {
                SingleVariableDeclaration paramDecl = (SingleVariableDeclaration) param;
                String paramType = paramDecl.getType().toString();
                String paramName = paramDecl.getName().toString();
                JsonObject paramInfo = new JsonObject();
                paramInfo.addProperty("type", paramType);
                paramInfo.addProperty("name", paramName);
                parameters.add(paramInfo);
            }
            method.add("parameters", parameters);
            String raw = node.toString();
            method.addProperty("raw", raw);
            methods.add(method);
            return super.visit(node);
        }

        public JsonArray getFields() {
            return fields;
        }

        public JsonArray getMethods() {
            return methods;
        }
    }

    public static CompilationUnit parse(String source) {
        ASTParser parser = ASTParser.newParser(AST.getJLSLatest());
        parser.setSource(source.toCharArray());
        parser.setKind(ASTParser.K_COMPILATION_UNIT);
        return (CompilationUnit) parser.createAST(null);
    }
    
    public static class MethodSignatureVisitor extends ASTVisitor {
        private final ASTRewrite rewriter;

        public MethodSignatureVisitor(ASTRewrite rewriter) {
            this.rewriter = rewriter;
        }

        @Override
        public boolean visit(MethodDeclaration node) {
            // Remove the method body to retain only the signature
            rewriter.set(node, MethodDeclaration.BODY_PROPERTY, null, null);
            return super.visit(node);
        }
    }

    private static CompilationUnit createCU(String projectName, String projectDir, String file) {
        try {
            Config.autoConfigure(projectName, projectDir);
        } catch (Exception e) {
            Config.JDT_LEVEL = AST.getJLSLatest();
            Config.JAVA_VERSION = "17";
        }
        ASTParser parser = ASTParser.newParser(Config.JDT_LEVEL);
        parser.setResolveBindings(true);
        parser.setKind(ASTParser.K_COMPILATION_UNIT);
        parser.setBindingsRecovery(true);
        parser.setStatementsRecovery(true);
        Hashtable<String, String> options = JavaCore.getOptions();
        JavaCore.setComplianceOptions(Config.JAVA_VERSION, options);
        parser.setCompilerOptions(options);
        parser.setEnvironment(Config.CLASS_PATH, Config.SOURCE_PATH, Config.ENCODE_SOURCE, true);
        parser.setUnitName(file);
        parser.setSource(FileProcessor.read(new File(file)).toCharArray());
        CompilationUnit cu = (CompilationUnit) parser.createAST(null);
        return cu;
    }

    private static JsonArray parseType(CompilationUnit cu, String relativePath, Logger logger) {
        int numType = cu.types().size();
        if (numType == 0) {
            logger.info("The file has no class: " + relativePath);
            return null;
        } else {
            JsonArray result = new JsonArray();

            for (int i = 0; i < numType; i++) {
                JsonObject typeInfo = new JsonObject();
                typeInfo.addProperty("relative_path", relativePath);
                AbstractTypeDeclaration type = (AbstractTypeDeclaration) cu.types().get(i);
                typeInfo.addProperty("name", type.getName().toString());
                String modifiers = "";
                for (Object modifier : type.modifiers()) {
                    modifiers += modifier.toString() + " ";
                }
                modifiers = modifiers.replaceAll("\\s+$", "");
                typeInfo.addProperty("modifiers", modifiers);
                ITypeBinding binding = type.resolveBinding();
                if (binding == null) {
                    typeInfo.addProperty("qualified_name", "<cant_resolve_binding>");
                } else {
                    typeInfo.addProperty("qualified_name", binding.getQualifiedName());
                }
                
                
                // Get the superclass name
                try {
                    TypeDeclaration classType = (TypeDeclaration) type;
                    Type superClassType = classType.getSuperclassType();
                    if (superClassType != null) {
                        typeInfo.addProperty("extend", superClassType.toString());
                    } else {
                        typeInfo.addProperty("extend", "");
                    }
                    String interfaces = "";
                    for (Object interfaceType : classType.superInterfaceTypes()) {
                        interfaces += interfaceType.toString() + ' ';
                    }
                    interfaces = interfaces.replaceAll("\\s+$", "");
                    typeInfo.addProperty("implements", interfaces);
                } catch (Exception e) {
                    typeInfo.addProperty("extend", "");
                    typeInfo.addProperty("implements", "");
                }
                typeInfo.addProperty("raw", type.toString());
                try {
                    String source = type.toString();
                    CompilationUnit classCU = parse(source);
                    AST ast = classCU.getAST();
                    ASTRewrite rewriter = ASTRewrite.create(ast);
                    MethodSignatureVisitor visitor = new MethodSignatureVisitor(rewriter);
                    classCU.accept(visitor);
                    Document document = new Document(source);
                    TextEdit edits = rewriter.rewriteAST(document, null);
                    try {
                        edits.apply(document);
                        typeInfo.addProperty("abstract", document.get());
                    } catch (Exception e) {
                        typeInfo.addProperty("abstract", "error");
                    }
                } catch (Exception e) {
                    typeInfo.addProperty("abstract", "error");
                }
                result.add(typeInfo);
            }
            return result;
        }
    }

    private static JsonArray parseField(CompilationUnit cu, String relativePath, Logger logger) {
        Visitor fieldVisitor = new Visitor(relativePath);
        cu.accept(fieldVisitor);
        return fieldVisitor.getFields();
    }

    private static JsonArray parseMethod(CompilationUnit cu, String relativePath, Logger logger) {
        Visitor methodVisitor = new Visitor(relativePath);
        cu.accept(methodVisitor);
        return methodVisitor.getMethods();
    }

    public static void main(String[] args) {
        Config.JAVAFX_DIR = "/home/hieuvd/lvdthieu/javafx-jmods-17.0.10";
        String baseDir = args[0];
        String projectName = args[1];
        String projectDir = baseDir + "/" + projectName;
        Logger logger = Logger.getLogger("parse_proj");
        logger.setLevel(Level.INFO);
        String fileExtension = ".java";
        List<String> files = new ArrayList<>();
        try (Stream<Path> walk = Files.walk(Paths.get(projectDir))) {
            files.addAll(walk.filter(p -> Files.isRegularFile(p) && p.toString().endsWith(fileExtension))
                    .map(Path::toString)
                    .collect(Collectors.toList()));
        } catch (Exception e) {
            logger.severe(e.getMessage());
        }
        JsonArray types = new JsonArray();
        // JsonArray methods = new JsonArray();
        // JsonArray fields = new JsonArray();
        if (files.size() > 0) {
            for (String file : files) {
                try {
                    CompilationUnit cu = createCU(projectName, projectDir, file);
                    String relativePath = file.replace(baseDir + '/', "");
                    JsonArray typeInfos = parseType(cu, relativePath, logger);
                    if (typeInfos != null) {
                        types.addAll(typeInfos);
                    }
                    // JsonArray fieldInfos = parseField(cu, relativePath, logger);
                    // if (fieldInfos != null) {
                    //     fields.addAll(fieldInfos);
                    // }
                    // JsonArray methodInfos = parseMethod(cu, relativePath, logger);
                    // if (methodInfos != null) {
                    //     methods.addAll(methodInfos);
                    // }
                } catch (Exception e) {
                    logger.severe(e.getMessage());
                }
            }
        }
        try (Writer writer = new OutputStreamWriter(new FileOutputStream(projectName + "_type.json"), "UTF-8")) {
            Gson gson = new GsonBuilder().create();
            gson.toJson(types, writer);
        } catch (Exception e) {
            logger.severe(e.getMessage());
        }
        // try (Writer writer = new OutputStreamWriter(new FileOutputStream(projectName + "_fields.json"), "UTF-8")) {
        //     Gson gson = new GsonBuilder().create();
        //     gson.toJson(fields, writer);
        // } catch (Exception e) {
        //     logger.severe(e.getMessage());
        // }
        // try (Writer writer = new OutputStreamWriter(new FileOutputStream(projectName + "_methods.json"), "UTF-8")) {
        //     Gson gson = new GsonBuilder().create();
        //     gson.toJson(methods, writer);
        // } catch (Exception e) {
        //     logger.severe(e.getMessage());
        // }

    }
}
