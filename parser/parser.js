import { find_comment, find_function, find_function_has_comment, find_function_only } from "./parse_funcs.js"
import fs from "fs";
import parser from "@solidity-parser/parser"
import parquetjs from "@dsnp/parquetjs"
import tqdm from "tqdm"
import { ArgumentParser } from "argparse"

function test_parser(file) {
    const data = fs.readFileSync(file, "utf-8");
    try {
        const ast = parser.parse(data, { loc: false });
        parser.visit(ast["children"], {
            Identifier: function (node) {
              console.log(node)
            },
        })
        return ast;
    } catch (e) {
        console.log("Error")
        if (e instanceof parser.ParserError) {
            console.log(e.errors);
        }
    }
}

function test_find_comment(file) {
    const sol_file = fs.readFileSync(file, "utf-8");
    const comments = find_comment(sol_file);
    for (let i = 0; i < comments.length; i++) {
        console.log(`${comments[i]["content"]}\n---------------------------------------------------------`);
    }
}

async function test_find_function() { //files_source
    // let sol_files = []
    // let reader = await parquetjs.ParquetReader.openFile(files_source)
    // let cursor = reader.getCursor()
    // let record = null
    // while (record = await cursor.next()) {
    //     sol_files.push(record)
    // }
    // const source = sol_files[0]["source_code"];
    const source = fs.readFileSync("/home/hieuvd/lvdthieu/CodeGen/experiment/check.sol", { encoding: 'utf8', flag: 'r' })
    const functions = find_function(source);
    // if (functions.length > 0) {
    //     for (let i = 0; i < functions.length; i++) {
    //         console.log(functions[i]["func"]);
    //         console.log("-----------------------------------");
    //     }
    // }
    console.log(functions[2]["contract_masked"])
}

async function test_find_function_has_comment(files_source, output_file) {
    let sol_files = []
    let reader = await parquetjs.ParquetReader.openFile(files_source)
    let cursor = reader.getCursor()
    let record = null
    while (record = await cursor.next()) {
        sol_files.push(record)
    }

    var schema = new parquetjs.ParquetSchema({
        source_idx: parquetjs.ParquetFieldBuilder.createStringField(),
        contract_name: parquetjs.ParquetFieldBuilder.createStringField(),
        func_name: parquetjs.ParquetFieldBuilder.createStringField(),
        masked_contract: parquetjs.ParquetFieldBuilder.createStringField(),
        func_body: parquetjs.ParquetFieldBuilder.createStringField(),
        // function: parquetjs.ParquetFieldBuilder.createStringField(),
        func_requirement: parquetjs.ParquetFieldBuilder.createStringField()
    })
    var writer = await parquetjs.ParquetWriter.openFile(schema, output_file)
    // for (const sol_file of tqdm(sol_files)) {
    //     try {
    //         const result = find_function_has_comment(sol_file["source_code"])
    //         if (result.length == 0) continue
    //         for (const record of result) {
    //             await writer.appendRow({
    //                 "source_idx": `${sol_file["source_idx"]}`,
    //                 "contract_name": record[0],
    //                 "func_name": record[1],
    //                 "masked_contract": record[2],
    //                 // "func_body": record[3],
    //                 "function": record[3],
    //                 "func_requirement": record[4]
    //             })
    //         }
    //     } catch (e) {
    //     }
    // }
    for (const sol_file of tqdm(sol_files)) {
        try {
            const result = find_function_has_comment(sol_file["contract_source"])
            if (result.length == 0) continue
            for (const record of result) {
                await writer.appendRow({
                    "source_idx": `${sol_file["source_idx"]}`,
                    "contract_name": record[0],
                    "func_name": record[1],
                    "masked_contract": record[2],
                    "func_body": record[3],
                    // "function": record[3],
                    "func_requirement": record[4]
                })
            }
        } catch (e) {
        }
    }
    
    writer.close()
}

async function test_find_function_only(files_source, output_file) {
    let sol_files = []
    let reader = await parquetjs.ParquetReader.openFile(files_source)
    let cursor = reader.getCursor()
    let record = null
    while (record = await cursor.next()) {
        sol_files.push(record)
    }

    var schema = new parquetjs.ParquetSchema({
        source_idx: parquetjs.ParquetFieldBuilder.createStringField(),
        contract_name: parquetjs.ParquetFieldBuilder.createStringField(),
        func_name: parquetjs.ParquetFieldBuilder.createStringField(),
        masked_contract: parquetjs.ParquetFieldBuilder.createStringField(),
        // func_body: parquetjs.ParquetFieldBuilder.createStringField(),
        function: parquetjs.ParquetFieldBuilder.createStringField(),
    })
    var writer = await parquetjs.ParquetWriter.openFile(schema, output_file)
    // for (const sol_file of tqdm(sol_files)) {
    //     try {
    //         const result = find_function_has_comment(sol_file["source_code"])
    //         if (result.length == 0) continue
    //         for (const record of result) {
    //             await writer.appendRow({
    //                 "source_idx": `${sol_file["source_idx"]}`,
    //                 "contract_name": record[0],
    //                 "func_name": record[1],
    //                 "masked_contract": record[2],
    //                 // "func_body": record[3],
    //                 "function": record[3],
    //                 "func_requirement": record[4]
    //             })
    //         }
    //     } catch (e) {
    //     }
    // }
    sol_files = sol_files.slice(0, 100)
    for (const sol_file of tqdm(sol_files)) {
        try {
            const result = find_function_only(sol_file["contract_source"])
            if (result.length == 0) continue
            for (const record of result) {
                await writer.appendRow({
                    "source_idx": `${sol_file["source_idx"]}`,
                    "contract_name": record["contract_name"],
                    "func_name": record["function_name"],
                    "masked_contract": record["contract_masked"],
                    // "func_body": record["body"]
                    "function": record["func"],
                })
            }
        } catch (e) {
        }
    }
    
    writer.close()
}

async function main() {
    const parser = new ArgumentParser()
    parser.add_argument('-i', '--input')
    parser.add_argument('-o', '--output')
    const args = parser.parse_args()
    // await test_find_function_has_comment(args.input, args.output)
    await test_find_function_only(args.input, args.output)

}

// main()

fs.writeFileSync("/home/hieuvd/lvdthieu/CodeGen/parse_sample.json", 
                JSON.stringify(test_parser("/home/hieuvd/lvdthieu/CodeGen/sample.sol")))
