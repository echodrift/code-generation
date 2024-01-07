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

async function test_extract_contract() {
    const contracts = await read_csv("./data/solfile/test_sol_file.csv").then((sol_files) => {
        return extract_contract(sol_files);
    });
    write_csv(contracts, "./out/test.csv", ["address", "contract_name", "contract_code"]);
}

function test_find_comment(file) {
    const sol_file = fs.readFileSync(file, "utf-8");
    const comments = find_comment(sol_file);
    for (let i = 0; i < comments.length; i++) {
        console.log(`${comments[i]["content"]}\n---------------------------------------------------------`);
    }
}

async function test_find_function() {
    const sol_files = await read_csv("./data/solfile/test_sol_file.csv").then((sol_files) => {
        return sol_files;
    }); 
    const contracts = await read_csv("./out/test.csv").then((contracts) => {
        return contracts;
    });
    const contract = contracts[0];
    const sol_file = sol_files.find(element => {
        return element["contract_address"] == contract["address"];
    })["source_code"];
    
    const functions = find_function(sol_file, contract["contract_name"]);
    for (let i = 0; i < functions.length; i++) {
        console.log(functions[i]["content"]);
        console.log("-----------------------------------");
    }
}

async function test_find_function_has_comment() {
    const sol_files = await read_csv("./data/solfile/test_sol_file.csv").then((sol_files) => {
        return sol_files;
    }); 
    const contracts = await read_csv("./out/test.csv").then((contracts) => {
        return contracts;
    });
    const contract = contracts[21];
    const sol_file = sol_files.find(element => {
        return element["contract_address"] == contract["address"];
    })["source_code"];
    find_function_has_comment(sol_file, contract["contract_name"]);
}

test_find_function_has_comment();




