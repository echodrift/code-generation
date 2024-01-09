import { read_csv, write_csv, find_comment, find_function, find_function_has_comment } from "./parser.js";
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

// async function test_extract_contract(input_file, output_file) {
//     const contracts = await read_csv(input_file).then((sol_files) => {
//         return extract_contract(sol_files);
//     });
//     write_csv(contracts, output_file, ["address", "contract_name"]);
// }

function test_find_comment(file) {
    const sol_file = fs.readFileSync(file, "utf-8");
    const comments = find_comment(sol_file);
    for (let i = 0; i < comments.length; i++) {
        console.log(`${comments[i]["content"]}\n---------------------------------------------------------`);
    }
}

async function test_find_function(sol_file) {
    const sol_files = await read_csv(sol_file).then((sol_files) => {
        return sol_files;
    });
    const source = sol_files[0]["source_code"];
    const functions = find_function(source);
    if (functions.length > 0) {
        for (let i = 0; i < functions.length; i++) {
            console.log(functions[i]["contract_name"]);
            console.log("-----------------------------------");
        }
    }
}

async function test_find_function_has_comment(sol_file) {
    let sol_files = await read_csv(sol_file).then((sol_files) => {
        return sol_files;
    });
    let chunks = Math.floor(sol_files.length / 1000);
    for (let i = 0; i < chunks; i++) {
        let data = [];
        for (let j = i * 1000; j < (i + 1) * 1000; j++) {
            try {
                console.log(j);
                const result = find_function_has_comment(sol_files[j]["source_code"]);
                if (result.length > 0) {
                    for (let k = 0; k < result.length; k++) {
                        let row = [sol_files[j]["contract_address"], ...result[k]];
                        data.push(row)
                    }
                } else {
                    fs.appendFileSync("contract_no_function_has_requirement.txt",
                        `------------------------------------------------------------------------\nContract ${j}\n`,
                        function (err) {
                            if (err) throw err;
                        }
                    );
                }
            } catch (e) {
                fs.appendFileSync("contract_error.txt",
                    `------------------------------------------------------------------------\nContract ${j}\n`,
                    function (err) {
                        if (err) throw err;
                    }
                );
            }
        }
        await write_csv(data, `./out/data${i}.csv`, ["file_address", "contract_name", "function_name", "contract_masked", "function_body", "function_requirement"]);
    }
   
    let data = []
    for (let j = chunks * 1000; j < sol_files.length; j++) {
        try {
            console.log(j);
            const result = find_function_has_comment(sol_files[j]["source_code"]);
            if (result.length > 0) {
                for (let k = 0; k < result.length; k++) {
                    let row = [sol_files[j]["contract_address"], ...result[k]];
                    data.push(row)
                }
            } else {
                fs.appendFileSync("contract_no_function_has_requirement.txt",
                    `------------------------------------------------------------------------\nContract ${j}\n`,
                    function (err) {
                        if (err) throw err;
                    }
                );
            }
        } catch (e) {
            fs.appendFileSync("contract_error.txt",
                `------------------------------------------------------------------------\nContract ${j}\n`,
                function (err) {
                    if (err) throw err;
                }
            );
        }
    }
    write_csv(data, `./out/data${chunks}.csv`, ["file_address", "contract_name", "function_name", "contract_masked", "function_body", "function_requirement"]);
}


test_find_function_has_comment("./data/solfile/test_sol_file.csv");

