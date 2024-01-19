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
        file_name: parquetjs.ParquetFieldBuilder.createStringField(),
        file_address: parquetjs.ParquetFieldBuilder.createStringField(),
        contract_name: parquetjs.ParquetFieldBuilder.createStringField(),
        func_name: parquetjs.ParquetFieldBuilder.createStringField(),
        masked_contract: parquetjs.ParquetFieldBuilder.createStringField(),
        func_body: parquetjs.ParquetFieldBuilder.createStringField(),
        func_requirement: parquetjs.ParquetFieldBuilder.createStringField()
    })
    var writer = await parquetjs.ParquetWriter.openFile(schema, output_file)
    
    // sol_files.forEach((sol_file, idx) => {
    //     console.log("Sol file idx:", idx)
    //     try {
    //         const result = find_function_has_comment(sol_file["source_code"])
    //         if (result.length == 0) return;
    //         result.forEach(async (record, id) => {
    //             // console.log(`Append row ${id} of sol file ${idx} start`)
    //             await writer.appendRow({
    //                 "source_idx": idx.toString(),
    //                 "contract_name": record[0],
    //                 "func_name": record[1],
    //                 "masked_contract": record[2],
    //                 "func_body": record[3],
    //                 "func_requirement": record[4]
    //             })
    //             // console.log(`Append row ${id} of sol file ${idx} end`)
    //         })      
    //     } catch (e) {
    //         console.log(e)
    //     }
    // })
    writer.setRowGroupSize(1048576)
    // const len = sol_files.length;
    // const num_chunk = Math.floor( len / 200)
    // for (let i = 0; i <= 5; i++) {
    //     const chunk = sol_files.slice(i * 200, Math.min((i + 1) * 200, len))
    //     console.log("start at chunk", i)
    await Promise.allSettled(sol_files.map(async (sol_file, idx) => {
        try {
            console.log("Sol file", idx)
            const result = find_function_has_comment(sol_file["source_code"])
            if (result.length == 0) return;
            await Promise.allSettled(result.map(async (record) => {
                await writer.appendRow({
                    "source_idx": `${idx}`,
                    "file_name": sol_file["file_name"],
                    "file_address": sol_file["file_address"],
                    "contract_name": record[0],
                    "func_name": record[1],
                    "masked_contract": record[2],
                    "func_body": record[3],
                    "func_requirement": record[4]
                })
            }))
        } catch (e) {
            console.log(e)
        }
    })) 
    writer.close()
    console.log("Close writer")
}


test_find_function_has_comment("./data/solfile/train_file.parquet", "./data/data/train_data.parquet");