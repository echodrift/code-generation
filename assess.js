import parquetjs from "@dsnp/parquetjs"
import parser from "@solidity-parser/parser"
import { get_location } from "./parse_funcs.js"

function fill_contract(source_code, contract_name, function_name, fill_content) {
    const source = source_code.replace("\r\n", "\n")
    try {
        const sourceUnit = parser.parse(source, {loc: true})
        for (let i = 0; i < sourceUnit["children"].length; i++) {
            if (sourceUnit["children"][i]["type"] == "ContractDefinition" &&
                sourceUnit["children"][i]["kind"] == "contract" &&
                sourceUnit["children"][i]["name"] == contract_name) {
                let child = sourceUnit["children"][i]
                for (let j = 0; j < child["subNodes"].length; j++) {
                    if (child["subNodes"][j]["type"] == "FunctionDefinition" &&
                        child["subNodes"][j]["name"] == function_name) {
                        let [body_start, body_end] = get_location(source, child["subNodes"][j]["body"])
                        const filled_source = source.slice(0, body_start + 1) + fill_content + source.slice(body_end - 1)
                        return filled_source
                    }
                }
            }
        }
    } catch {

    }
}


async function parsable(test_file) {
    let test_cases = []
    let reader = await parquetjs.ParquetReader.openFile(test_file)
    let cursor = reader.getCursor()
    let record = null
    while (record = await cursor.next()) {
        test_cases.push(record)
    }
    let error_case = []
    let source_code = null
    let contract_name = null
    let function_name = null
    let fill_content = null
    let filled_source = null
    let cnt = 0

    for (let i = 0; i < test_cases.length; i++){
        console.log(i)
        source_code = test_cases[i]["source_code"]
        contract_name = test_cases[i]["contract_name"]
        function_name = test_cases[i]["func_name"]
        if (!function_name) {
            function_name = ""
        }
        fill_content = test_cases[i]["func_body"]
        filled_source = fill_contract(source_code, contract_name, function_name, fill_content)
        if (filled_source) {
            
            try {
                let sourceUnit = parser.parse(filled_source)
                cnt += 1
            } catch (e) {
                console.log("Error")
                if (e instanceof parser.ParserError) {
                    console.log(e.errors);
                }    
            }
        }
        
    }
    return cnt
}




async function make_test_suite(test_file, test_suite) {
    let test_cases = []
    let reader = await parquetjs.ParquetReader.openFile(test_file)
    let cursor = reader.getCursor()
    let record = null
    while (record = await cursor.next()) {
        test_cases.push(record)
    }
    let source_code = null
    let contract_name = null
    let function_name = null
    let fill_content = null
    let filled_source = null
    let file_name = null
    let file_address = null
    var schema = new parquetjs.ParquetSchema({
        file_name: parquetjs.ParquetFieldBuilder.createStringField(),
        file_address: parquetjs.ParquetFieldBuilder.createStringField(),
        contract_name: parquetjs.ParquetFieldBuilder.createStringField(),
        func_name: parquetjs.ParquetFieldBuilder.createStringField(),
        source_code: parquetjs.ParquetFieldBuilder.createStringField(),
        source_code_with_deepseek_output: parquetjs.ParquetFieldBuilder.createStringField()
    })
    var writer = await parquetjs.ParquetWriter.openFile(schema, test_suite)
    for (let i = 0; i < test_cases.length; i++){
        console.log(i)
        source_code = test_cases[i]["source_code"]
        contract_name = test_cases[i]["contract_name"]
        function_name = test_cases[i]["func_name"]
        file_name = test_cases[i]["file_name"]
        file_address = test_cases[i]["file_address"]
        if (!function_name) {
            function_name = ""
        }
        fill_content = test_cases[i]["deepseek_output"]
        filled_source = fill_contract(source_code, contract_name, function_name, fill_content)
        if (filled_source) {
            await writer.appendRow({
                "file_name": file_name,
                "file_address": file_address,
                "contract_name": contract_name,
                "func_name": function_name,
                "source_code": source_code,
                "source_code_with_deepseek_output": filled_source
            })
        }
        
    }
    writer.close()
}

make_test_suite("./data/test/test.parquet", "./data/test/test-v2.parquet")