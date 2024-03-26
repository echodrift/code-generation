import { find_comment, find_function, find_function_has_comment, find_function_only } from "./parse_funcs.js"
import fs from "fs";
import parser from "@solidity-parser/parser"
import parquetjs, { ParquetSchema } from "@dsnp/parquetjs"
import tqdm from "tqdm"
import { ArgumentParser } from "argparse"

function test_parser(file) {
    const data = fs.readFileSync(file, "utf-8");
    try {
        const ast = parser.parse(data, { loc: true });
        fs.writeFileSync("/home/hieuvd/lvdthieu/CodeGen/parse_sample.json", JSON.stringify(ast))
    } catch (e) {
        console.log("Error")
        if (e instanceof parser.ParserError) {
            console.log(e.errors);
        }
    }
}

async function read_parquet(file_path) {
    let df = []
    let reader = await parquetjs.ParquetReader.openFile(file_path)
    let cursor = reader.getCursor()
    let record = null
    while (record = await cursor.next()) {
        df.push(record)
    }
    return df
}

async function transform_function_has_comment(input_file, output_file) {
    const df = await read_parquet(input_file)

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

    for (const row of tqdm(df)) {
        try {
            const result = find_function_has_comment(row["contract_source"])
            if (result.length == 0) continue
            for (const record of result) {
                await writer.appendRow({
                    "source_idx": `${row["source_idx"]}`,
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

async function transform_function_only(input_file, output_file) {
    const df = await read_parquet(input_file)

    var schema = new parquetjs.ParquetSchema({
        source_idx: parquetjs.ParquetFieldBuilder.createStringField(),
        contract_name: parquetjs.ParquetFieldBuilder.createStringField(),
        func_name: parquetjs.ParquetFieldBuilder.createStringField(),
        masked_contract: parquetjs.ParquetFieldBuilder.createStringField(),
        // func_body: parquetjs.ParquetFieldBuilder.createStringField(),
        function: parquetjs.ParquetFieldBuilder.createStringField(),
    })
    var writer = await parquetjs.ParquetWriter.openFile(schema, output_file)
    for (const row of tqdm(df)) {
        try {
            const result = find_function_only(row["contract_source"])
            if (result.length == 0) continue
            for (const record of result) {
                await writer.appendRow({
                    "source_idx": `${row["source_idx"]}`,
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

async function transfrom_parse_file(input_file, output_file) {
    const df = await read_parquet(input_file)
    var schema = new parquetjs.ParquetSchema({
        source_idx: parquetjs.ParquetFieldBuilder.createStringField(),
        contract_name: parquetjs.ParquetFieldBuilder.createStringField(),
        contract_source: parquetjs.ParquetFieldBuilder.createStringField(),
        contract_ast: parquetjs.ParquetFieldBuilder.createStringField(),
        count: parquetjs.ParquetFieldBuilder.createStringField()
    })
    var writer = await parquetjs.ParquetWriter.openFile(schema, output_file)
    for (const row of tqdm(df)) {
        const source = row["contract_source"].replace('\r\n', '\n')
        let ast_string = "<PARSER_ERROR>"
        try {
            const ast = parser.parse(source, {loc: true})
            ast_string = JSON.stringify(ast)
        } catch (e) {
            fs.appendFileSync("parse_error.sol", `${source}\n__________________________________________________________________________________________________\n`)
        } finally {
            await writer.appendRow({
                "source_idx": `${row["source_idx"]}`,
                "contract_name": row["contract_name"],
                "contract_source": row["contract_source"],
                "contract_ast": ast_string,
                "count": `${row["count"]}`
            })
        }
    }
    writer.close()
}

async function transform_inherited_element(input_file, output_file) {
    const df = await read_parquet(input_file)

    var schema = new parquetjs.ParquetSchema({

    })
    var writer = await parquetjs.ParquetWriter.openFile(schema, output_file)

    for (const row of tqdm(df)) {
        console.log(row)   
    }
}

async function main() {
    const parser = new ArgumentParser()
    parser.add_argument('-i', '--input')
    parser.add_argument('-o', '--output')
    const args = parser.parse_args()
    // await test_find_function_has_comment(args.input, args.output)
    // await test_find_function_only(args.input, args.output)
    await transform_inherited_element(args.input, args.output)  
}

// main()
test_parser("/home/hieuvd/lvdthieu/CodeGen/parse_sample.sol")

