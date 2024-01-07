import { read_csv, extract_contract, write_csv, find_comment, find_function, find_function_has_comment } from "./parser.js";
import fs from "fs";
import parser from "@solidity-parser/parser";

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

async function test_extract_contract(input_file, output_file) {
    const contracts = await read_csv(input_file).then((sol_files) => {
        return extract_contract(sol_files);
    });
    write_csv(contracts, output_file, ["address", "contract_name", "contract_code"]);
}

function test_find_comment(file) {
    const sol_file = fs.readFileSync(file, "utf-8");
    const comments = find_comment(sol_file);
    for (let i = 0; i < comments.length; i++) {
        console.log(`${comments[i]["content"]}\n---------------------------------------------------------`);
    }
}

async function test_find_function(sol_file, contract_file) {
    const sol_files = await read_csv(sol_file).then((sol_files) => {
        return sol_files;
    }); 
    const contracts = await read_csv(contract_file).then((contracts) => {
        return contracts;
    });
    const contract = contracts[0];
    const source = sol_files.find(element => {
        return element["contract_address"] == contract["address"];
    })["source_code"];
    const functions = find_function(source, contract["contract_name"]);
    if (functions) {
        for (let i = 0; i < functions.length; i++) {
            console.log(functions[i]["body"]["content"]);
            console.log("-----------------------------------");
        }
    }
}

async function test_find_function_has_comment(sol_file, contract_file) {
    const sol_files = await read_csv(sol_file).then((sol_files) => {
        return sol_files;
    }); 
    const contracts = await read_csv(contract_file).then((contracts) => {
        return contracts;
    });
    let data = [];
    for (let i = 0; i < contracts.length; i++) {
        try {
            console.log(i);
            let row = [contracts[i]["address"], contracts[i]["contract_name"]]
            let source = sol_files.find(element => {
                return element["contract_address"] == contracts[i]["address"];
            })["source_code"];
            const result = find_function_has_comment(source, contracts[i]["contract_name"]);
            if (result.length > 0) {
                for (let j = 0; j < result.length; j++) {
                    let row = [contracts[i]["address"], contracts[i]["contract_name"], ...result[j]];
                    data.push(row)
                }    
            } else {
                fs.appendFileSync("contract_no_function_has_requirement.txt",
                `------------------------------------------------------------------------\nContract ${i}\n`,
                function (err) {
                    if (err) throw err;
                }
                );
            }
        } catch (e) {
            fs.appendFileSync("contract_error.txt",
            `------------------------------------------------------------------------\nContract ${i}\n`,
            function (err) {
                if (err) throw err;
            }
            );
        }   
    }
    const chunks = Math.floor(data.length / 500);
    for (let i = 0; i < chunks; i++) {
        write_csv(data.slice(i * 500, (i + 1) * 500), `./out/data${i}.csv`, ["File address", "Contract name", "Function name", "Contract masked", "Function body", "Function requirement"]);
    }
    write_csv(data.slice(chunks * 500), `./out/data${chunks}.csv`, ["File address", "Contract name", "Function name", "Contract masked", "Function body", "Function requirement"]);    
}

// test_extract_contract("./data/solfile/valid_sol_file.csv", "./out/contracts.csv");
test_find_function_has_comment("./data/solfile/valid_sol_file.csv", "./out/contracts.csv");


