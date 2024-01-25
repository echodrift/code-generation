import parser from "@solidity-parser/parser";

/**
 * Get plain location of a element in source code (from ith to jth in source code)
 * @param {string} source Solditity source code 
 * @param {string} element An element that parsed from source code 
 * @returns 
 */
export function get_location(source, element) {
    const start_line = element["loc"]["start"]["line"];
    const start_col = element["loc"]["start"]["column"];
    const end_line = element["loc"]["end"]["line"];
    const end_col = element["loc"]["end"]["column"];
    const lines = source.split('\n');
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

/**
 * This function is a recusive function aim to get all comment before a start point
 * @param {string} source Solidity source code
 * @param {List[string]} comment_list List comments in that source code
 * @param {int} start_point Start point for recursive search 
 * @param {List[string]} result Update variable through recursion
 */
function back_search(source, comment_list, start_point, result) {
    let tmp = start_point;
    while (source[tmp] == ' ' || source[tmp] == '\n' || source[tmp] == '\t' || source[tmp] == '\r') {
        tmp -= 1;
    }
    for (let i = 0; i < comment_list.length; i++) {
        if (tmp >= comment_list[i]["range"]["start"] && tmp <= comment_list[i]["range"]["end"]) {
            result.push(comment_list[i]["content"]);
            back_search(source, comment_list, comment_list[i]["range"]["start"] - 1, result);
            break;
        }
    }
}

/**
 * This function aims to extract all comments in Solidity source code
 * @param {string} source Solidity source code 
 * @returns List of comments in source code
 */
export function find_comment(source) {
    source = source.replace('\r\n', '\n');
    let state = "ETC";
    let i = 0;
    let comments = [];
    let currentComment = null;

    while (i + 1 < source.length) {
        if (state == "ETC" && source[i] == '/' && source[i + 1] == '/') {
            state = "LINE_COMMENT";
            currentComment = {
                "type": "LineComment",
                "range": { "start": i }
            };
            i += 2;
            continue;
        }

        if (state == "LINE_COMMENT" && source[i] == '\n') {
            state = "ETC";
            currentComment["range"]["end"] = i;
            comments.push(currentComment);
            currentComment = null;
            i += 1;
            continue;
        }

        if (state == "ETC" && source[i] == '/' && source[i + 1] == '*') {
            state = "BLOCK_COMMENT";
            currentComment = {
                "type": "BlockComment",
                "range": { "start": i }
            };
            i += 2;
            continue;
        }

        if (state == "BLOCK_COMMENT" && source[i] == '*' && source[i + 1] == '/') {
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
        if (source[i - 1] == '\n') {
            currentComment["range"]["end"] = source.length - 1;
        } else {
            currentComment["range"]["end"] = source.length;
        }
        comments.push(currentComment)
    }


    function extract_content(source, comments) {
        for (let i = 0; i < comments.length; i++) {
            let start = comments[i]["range"]["start"] + 2;
            let end = comments[i]["type"] == "LineComment" ? comments[i]["range"]["end"] : comments[i]["range"]["end"] - 2;
            let raw = source.slice(start, end);
            comments[i]["content"] = raw.trim();
        }
        comments = comments.filter((comment) => comment["content"]);
        return comments;
    }

    return extract_content(source, comments);
}

/**
 * This function aims to extract all functions in Solidity source code
 * @param {string} source Solidity source code 
 * @returns List of function in source code
 */
export function find_function(source) {
    source = source.replace('\r\n', '\n');
    let functions = [];
    const sourceUnit = parser.parse(source, { loc: true });
    for (let i = 0; i < sourceUnit["children"].length; i++) {
        if (sourceUnit["children"][i]["type"] == "ContractDefinition" &&
            sourceUnit["children"][i]["kind"] == "contract") { 
            let child = sourceUnit["children"][i]
            for (let j = 0; j < child["subNodes"].length; j++) {
                if (child["subNodes"][j]["type"] == "FunctionDefinition") {
                    if (child["subNodes"][j]["body"] && child["subNodes"][j]) {
                        let [contract_start, contract_end] = get_location(source, child);
                        let [func_start, func_end] = get_location(source, child["subNodes"][j]);
                        let [body_start, body_end] = get_location(source, child["subNodes"][j]["body"]);
                        const body = source.slice(body_start + 1, body_end - 1);
                        const contract_masked = source.slice(contract_start, body_start + 1) + "<FILL_FUNCTION_BODY>" + source.slice(body_end - 1, contract_end);
                        // const func = source.slice(func_start, func_end)
                        // const contract_masked = source.slice(contract_start, func_start) + "<FILL_FUNCTION>" + source.slice(func_end, contract_end)
                        functions.push({
                            "contract_name": child["name"],
                            "function_name": child["subNodes"][j]["name"],
                            "range": { "start": func_start, "end": func_end },
                            "body": body,
                            // "func": func,
                            "contract_masked": contract_masked
                        });
                    }
                }
            }
        }
    }
    return functions
}

/**
 * This function aims to get all function that has comment(requirement) in Soldity source code
 * @param {string} source Solidity source code 
 * @returns List of functions that has requirement in source code
 */
export function find_function_has_comment(source) {
    let result = []
    source = source.replace('\r\n', '\n');
    const functions = find_function(source);
    const comments = find_comment(source);
    if (functions.length > 0 && comments.length > 0) {
        for (let i = 0; i < functions.length; i++) {
            let tmp = functions[i]["range"]["start"] - 1;
            let function_comments = [];
            back_search(source, comments, tmp, function_comments);
            if (function_comments.length > 0) {
                const function_requirement = function_comments.reverse().join('\n');
                result.push([functions[i]["contract_name"], functions[i]["function_name"],
                functions[i]["contract_masked"], functions[i]["body"], function_requirement]);
                // result.push([functions[i]["contract_name"], functions[i]["function_name"],
                // functions[i]["contract_masked"], functions[i]["func"], function_requirement]);
            }
        }
    }
    return result;
}

/**
 * This function aims to get all functions in Solidity source code with formated structure
 * @param {string} source Solidity source code
 * @returns List of functions in source code
 */
export function find_function_only(source) {
    source = source.replace('\r\n', '\n');
    let functions = [];
    const sourceUnit = parser.parse(source, { loc: true });
    for (let child of sourceUnit["children"]) {
        if (child["type"] == "ContractDefinition" &&
            child["kind"] == "contract") { 
            for (let subNode of child["subNodes"]) {
                if (subNode["type"] == "FunctionDefinition" && subNode["body"]) {
                    let [contract_start, contract_end] = get_location(source, child);
                    // let [body_start, body_end] = get_location(source, subNode["body"]);
                    // const body = source.slice(body_start + 1, body_end - 1);
                    // const contract_masked = source.slice(contract_start, body_start + 1) + "<FILL_FUNCTION_BODY>" + source.slice(body_end - 1, contract_end);
                    let [func_start, func_end] = get_location(source, subNode);
                    const func = source.slice(func_start, func_end)
                    const contract_masked = source.slice(contract_start, func_start) + "<FILL_FUNCTION>" + source.slice(func_end, contract_end)
                    functions.push({
                        "contract_name": child["name"],
                        "function_name": subNode["name"],
                        "contract_masked": contract_masked,
                        // "body": body
                        "func": func
                    });
                
                }
            }
        }
    }
    return functions
}