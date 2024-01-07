import parser from "@solidity-parser/parser";
import fs from "fs";
import csv from "csv-parser";
import { stringify } from "csv-stringify";


function get_location(sol_file, element) {
    const start_line = element["loc"]["start"]["line"];
    const start_col = element["loc"]["start"]["column"];
    const end_line = element["loc"]["end"]["line"];
    const end_col = element["loc"]["end"]["column"];
    const lines = sol_file.split('\n');
    let start_idx = 0;
    for (let j = 0; j < start_line - 1; j++) {
        start_idx += lines[j].length;
    }
    start_idx = start_idx + start_line - 1 + start_col;
    let end_idx = 0;
    for (let j = 0; j < end_line - 1; j++) {
        end_idx += lines[j].length;
    }
    end_idx = end_idx + end_line - 1 + end_col + 1;

    return [start_idx, end_idx];
}

function back_search(sol_file, comment_list, start_point, result) {
    let tmp = start_point;
    while (sol_file[tmp] == ' ' || sol_file[tmp] == '\n' || sol_file[tmp] == '\t' || sol_file[tmp] == '\r') {
        tmp -= 1;
    }
    for (let i = 0; i < comment_list.length; i++) {
        if (tmp >= comment_list[i]["range"]["start"] && tmp <= comment_list[i]["range"]["end"]) {
            result.push(comment_list[i]["content"]);
            back_search(sol_file, comment_list, comment_list[i]["range"]["start"] - 1, result);
            break;
        }
    }
}

export function read_csv(file_path) {
    return new Promise((resolve, reject) => {
        let result = []
        fs.createReadStream(file_path)
            .pipe(csv())
            .on('data', (data) => result.push(data))
            .on('end', () => {
                resolve(result)
            });
    });
}

export function write_csv(data, file_path, columns) {
    stringify(data, { header: true, columns: columns }, (err, output) => {
        if (err) throw err;
        fs.writeFileSync(file_path, output, (error) => {
            if (err) throw err;
            console.log("Saved");
        });
    });
}

export function extract_contract(sol_files) {
    var contracts = []
    for (let i = 0; i < sol_files.length; i++) {
        console.log(i);
        console.log(contracts.length)
        try {
            const source = sol_files[i]["source_code"].replace('\r\n', '\n');
            const ast = parser.parse(source, { loc: true });
            for (let j = 0; j < ast["children"].length; j++) {
                if (ast["children"][j]["type"] == "ContractDefinition" &&
                    ast["children"][j]["kind"] == "contract") {
                    const [start_idx, end_idx] = get_location(source, ast["children"][j]);
                    contracts.push([
                        sol_files[i]["contract_address"],
                        ast["children"][j]["name"],
                        source.slice(start_idx, end_idx)
                    ]);
                }
            }
        } catch (e) {
            fs.appendFileSync("js_error_log.txt",
                `------------------------------------------------------------------------\n${i}\t${e.errors}\n`,
                function (err) {
                    if (err) throw err;
                });
        }
    }
    return contracts
}

export function find_comment(sol_file) {
    sol_file = sol_file.replace('\r\n', '\n');
    let state = "ETC";
    let i = 0;
    let comments = [];
    let currentComment = null;

    while (i + 1 < sol_file.length) {
        if (state == "ETC" && sol_file[i] == '/' && sol_file[i + 1] == '/') {
            state = "LINE_COMMENT";
            currentComment = {
                "type": "LineComment",
                "range": { "start": i }
            };
            i += 2;
            continue;
        }

        if (state == "LINE_COMMENT" && sol_file[i] == '\n') {
            state = "ETC";
            currentComment["range"]["end"] = i;
            comments.push(currentComment);
            currentComment = null;
            i += 1;
            continue;
        }

        if (state == "ETC" && sol_file[i] == '/' && sol_file[i + 1] == '*') {
            state = "BLOCK_COMMENT";
            currentComment = {
                "type": "BlockComment",
                "range": { "start": i }
            };
            i += 2;
            continue;
        }

        if (state == "BLOCK_COMMENT" && sol_file[i] == '*' && sol_file[i + 1] == '/') {
            state = "ETC";
            currentComment["range"]["end"] = i + 2;
            comments.push(currentComment);
            currentComment = null;
            i += 2;
            continue;
        }
        i += 1;
    }

    if (currentComment && currentComment["type"] == "LineComment") {
        if (sol_file[i - 1] == '\n') {
            currentComment["range"]["end"] = sol_file.length - 1;
        } else {
            currentComment["range"]["end"] = sol_file.length;
        }
        comments.push(currentComment)
    }


    function extract_content(sol_file, comments) {
        for (let i = 0; i < comments.length; i++) {
            let start = comments[i]["range"]["start"] + 2;
            let end = comments[i]["type"] == "LineComment" ? comments[i]["range"]["end"] : comments[i]["range"]["end"] - 2;
            let raw = sol_file.slice(start, end);
            comments[i]["content"] = raw.trim();
        }
        comments = comments.filter((comment) => comment["content"]);
        return comments;
    }

    return extract_content(sol_file, comments);
}

export function find_function(sol_file, contract_name) {
    sol_file = sol_file.replace('\r\n', '\n');
    let functions = [];
    const sourceUnit = parser.parse(sol_file, { loc: true });
    for (let i = 0; i < sourceUnit["children"].length; i++) {
        if (sourceUnit["children"][i]["type"] == "ContractDefinition" &&
            sourceUnit["children"][i]["kind"] == "contract" &&
            sourceUnit["children"][i]["name"] == contract_name) {
            let child = sourceUnit["children"][i];
            for (let j = 0; j < child["subNodes"].length; j++) {
                if (child["subNodes"][j]["type"] == "FunctionDefinition") {
                    if (child["subNodes"][j]["body"]) {
                        let [contract_start, contract_end] = get_location(sol_file, child);
                        let [func_start, func_end] = get_location(sol_file, child["subNodes"][j]);
                        let [body_start, body_end] = get_location(sol_file, child["subNodes"][j]["body"]);
                        const body = sol_file.slice(body_start + 1, body_end - 1);
                        const contract_masked = sol_file.slice(contract_start, body_start + 1) + "<FILL FUNCTION BODY>" + sol_file.slice(body_end, contract_end);
                        functions.push({
                            "name": child["subNodes"][j]["name"],
                            "range": { "start": func_start, "end": func_end },
                            "body": body,
                            "contract_masked": contract_masked
                        });
                    }
                }
            }
        }
    }
    return functions
}

export function find_function_has_comment(sol_file, contract_name) {
    let result = []
    sol_file = sol_file.replace('\r\n', '\n');
    const functions = find_function(sol_file, contract_name);
    const comments = find_comment(sol_file);
    if (functions.length > 0 && comments.length > 0) {
        for (let i = 0; i < functions.length; i++) {
            let tmp = functions[i]["range"]["start"] - 1;
            let function_comments = [];
            back_search(sol_file, comments, tmp, function_comments);
            if (function_comments.length > 0) {
                const function_requirement = function_comments.reverse().join('\n');
                result.push([functions[i]["name"], functions[i]["contract_masked"], functions[i]["body"], function_requirement]);
            }
        }
    } 
    return result;
}
