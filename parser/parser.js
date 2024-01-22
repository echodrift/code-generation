import { find_comment, find_function, find_function_has_comment } from "./parse_funcs.js"
import fs from "fs";
import parser from "@solidity-parser/parser"
import parquetjs from "@dsnp/parquetjs"
import tqdm from "tqdm"
import { ArgumentParser } from "argparse"

function test_parser(file) {
    const data = fs.readFileSync(file, "utf-8");
    try {
        const ast = parser.parse(data, { loc: true });
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
        // func_body: parquetjs.ParquetFieldBuilder.createStringField(),
        function: parquetjs.ParquetFieldBuilder.createStringField(),
        func_requirement: parquetjs.ParquetFieldBuilder.createStringField()
    })
    var writer = await parquetjs.ParquetWriter.openFile(schema, output_file)
    

    for (const sol_file of tqdm(sol_files)) {
        try {
            const result = find_function_has_comment(sol_file["source_code"])
            if (result.length == 0) continue
            for (const record of result) {
                await writer.appendRow({
                    "source_idx": `${sol_file["source_idx"]}`,
                    "contract_name": record[0],
                    "func_name": record[1],
                    "masked_contract": record[2],
                    // "func_body": record[3],
                    "function": record[3],
                    "func_requirement": record[4]
                })
            }
        } catch (e) {
        }
    }
    writer.close()
    console.log("Close writer")
}


async function main() {
    const parser = new ArgumentParser()
    parser.add_argument('-i', '--input')
    parser.add_argument('-o', '--output')
    const args = parser.parse_args()
    await test_find_function_has_comment(args.input, args.output)
}

main()

