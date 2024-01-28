import parquetjs from "@dsnp/parquetjs"
import parser from "@solidity-parser/parser"
import { get_location } from "./parse_funcs.js"
import stringSimilarity from "string-similarity"
import { ArgumentParser } from "argparse"
import tqdm from "tqdm"
import fs from "fs"
/**
 * This function aim to create full version of a solididy files to test file compilability
 * @param {string} file_source Masked Solidity source code
 * @param {string} contract_name Contract has function masked       
 * @param {string} func_name Masked function
 * @param {string} func_body Body of masked function (ground truth) 
 * @param {string} deepseek_output Body of masked function that base LLM model generated 
 * @param {string} codellama_output Body of masked function that finetuned LLM model generated [, codellama_output]
 * @returns {Optional[List]} a list of filled contracts with func_body, deepseek_output, codellama_output respectively
 */
function fill_contract(file_source, contract_name, func_name, func_body, deepseek_output) {
    const source = file_source.replace("\r\n", "\n")
    try {
        const sourceUnit = parser.parse(source, {loc: true})
        for (let child of sourceUnit["children"]) {
            if (child["type"] == "ContractDefinition" && 
                child["kind"] == "contract" &&
                child["name"] == contract_name) {
                let candidates = []
                for (let subNode of child["subNodes"]) {
                    if (subNode["type"] == "FunctionDefinition" &&
                        subNode["name"] === func_name) {
                            candidates.push(subNode)
                        }
                }
                if (candidates.length == 0) {
                    // fs.appendFileSync("check.sol", `${file_source}\t${contract_name}\t${func_name}\n-----------------------------------------------------------------------------------------------------------------\n`)
                    return null
                } else if (candidates.length == 1) {
                    let [body_start, body_end] = get_location(source, candidates[0]["body"])
                    const filled_source_body = source.slice(0, body_start + 1) + func_body + source.slice(body_end - 1)
                    const filled_source_deepseek = source.slice(0, body_start + 1) + deepseek_output + source.slice(body_end - 1)
                    // const filled_source_codellama = source.slice(0, body_start + 1) + codellama_output + source.slice(body_end - 1)
                    // return [filled_source_body, filled_source_deepseek, filled_source_codellama]
                    return [filled_source_body, filled_source_deepseek]
                } else {
                    let best_candidate = null
                    let best_similar_rate = 0
                    for (let candidate of candidates) {
                        let [body_start, body_end] = get_location(source, candidate["body"])
                        let ground_truth = source.slice(body_start + 1 , body_end - 1)
                        const similar_rate = stringSimilarity.compareTwoStrings(ground_truth.toLowerCase(), func_body.toLowerCase())
                        if (best_similar_rate < similar_rate) {
                            best_similar_rate = similar_rate
                            best_candidate = candidate
                        }
                    }
                    let [body_start, body_end] = get_location(source, best_candidate["body"])
                    const filled_source_body = source.slice(0, body_start + 1) + func_body + source.slice(body_end - 1)
                    const filled_source_deepseek = source.slice(0, body_start + 1) + deepseek_output + source.slice(body_end - 1)
                    // const filled_source_codellama = source.slice(0, body_start + 1) + codellama_output + source.slice(body_end - 1)
                    // return [filled_source_body, filled_source_deepseek, filled_source_codellama]
                    return [filled_source_body, filled_source_deepseek]
                }
            }
        }    
    } catch (e) {
        return null
    }
}

/**
 * This function aim to create a test suit for compilation test from LLM model generation output
 * @param {string} source Test input path: file contains testcase with masked a function body in soldity files and their function body candidates 
 * @param {string} dest Test suite path: files contains testcase with filled Solidity files
 */
async function make_test_suite(source, dest) {
    let test_cases = []
    let reader = await parquetjs.ParquetReader.openFile(source)
    let cursor = reader.getCursor()
    let record = null
    while (record = await cursor.next()) {
        test_cases.push(record)
    }
    var schema = new parquetjs.ParquetSchema({
        contract_name: parquetjs.ParquetFieldBuilder.createStringField(),
        func_name: parquetjs.ParquetFieldBuilder.createStringField(),
        masked_contract: parquetjs.ParquetFieldBuilder.createStringField(),
        func_body: parquetjs.ParquetFieldBuilder.createStringField(),
        func_body_removed_comment: parquetjs.ParquetFieldBuilder.createStringField(),
        deepseek_output: parquetjs.ParquetFieldBuilder.createStringField(),
        file_source_idx: parquetjs.ParquetFieldBuilder.createStringField(),
        original_source_code: parquetjs.ParquetFieldBuilder.createStringField(),
        filled_source_body: parquetjs.ParquetFieldBuilder.createStringField(),
        filled_source_deepseek: parquetjs.ParquetFieldBuilder.createStringField(),
        // filled_source_codellama: parquetjs.ParquetFieldBuilder.createStringField()
    })
    var writer = await parquetjs.ParquetWriter.openFile(schema, dest)
    for (let test_case of tqdm(test_cases)){
        const result = fill_contract(test_case["file_source"], 
                                    test_case["contract_name"], 
                                    test_case["func_name"], 
                                    test_case["func_body"],
                                    test_case["deepseek_output"]
                                    // test_case["codeellama_output"]
                                    )
        if (!result) continue

        // const [filled_source_body, 
        //     filled_source_deepseek, 
        //     filled_source_codellama] = result
        const [filled_source_body, filled_source_deepseek] = result

        await writer.appendRow({
            "contract_name": test_case["contract_name"],
            "func_name": test_case["func_name"],
            "masked_contract": test_case["masked_contract"],
            "func_body": test_case["func_body"],
            "func_body_removed_comment": test_case["func_body_removed_comment"],
            "deepseek_output": test_case["deepseek_output"],
            "file_source_idx": `${test_case["file_source_idx"]}`, 
            "original_source_code": test_case["file_source"],
            "filled_source_body": filled_source_body,
            "filled_source_deepseek": filled_source_deepseek,
            // "filled_source_codellama": filled_source_codellama,
        })
    }
    
    writer.close()
}

/**
 * Main function
 */
async function main() {
    const parser = new ArgumentParser()
    parser.add_argument('-i', '--input')
    parser.add_argument('-o', '--output')
    const args = parser.parse_args()
    await make_test_suite(args.input, args.output)
}

main()

