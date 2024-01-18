import { find_comment, find_function, find_function_has_comment } from "./parse_funcs.js";
import fs from "fs";
import parser from "@solidity-parser/parser";
import parquetjs from "@dsnp/parquetjs"

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

async function test_find_function(sol_file) {
    let sol_files = []
    let reader = await parquetjs.ParquetReader.openFile(sol_file)
    let cursor = reader.getCursor()
    let record = null
    while (record = await cursor.next()) {
        sol_files.push(record)
    }
    const source = sol_files[0]["source_code"];
    
    const functions = find_function(source);
    if (functions.length > 0) {
        for (let i = 0; i < functions.length; i++) {
            console.log(functions[i]["function_name"]);
            console.log("-----------------------------------");
        }
    }
}

async function test_find_function_has_comment(sol_file, output_file) {
    let sol_files = []
    let reader = await parquetjs.ParquetReader.openFile(sol_file)
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
        func_requirement: parquetjs.ParquetFieldBuilder.createStringField()
    })
    var writer = await parquetjs.ParquetWriter.openFile(schema, output_file)

    await Promise.all(sol_files.map(async (sol_file, idx) => {
        console.log("Sol file idx:", idx)
        try {
            const result = find_function_has_comment(sol_file["source_code"])
            if (result.length == 0) return;
            
            await Promise.all(Array(result.length).fill(0).map(async (_, i) => {
                await writer.appendRow({
                    "source_idx": idx.toString(),
                    "contract_name": result[i][0],
                    "func_name": result[i][1],
                    "masked_contract": result[i][2],
                    "func_body": result[i][3],
                    "func_requirement": result[i][4]
                })
            }))
        } catch (e) {
            console.log(e)
        }
    }))
    writer.close()
}


test_find_function_has_comment("./data/solfile/test_file.parquet", "./data/data/test_data.parquet");