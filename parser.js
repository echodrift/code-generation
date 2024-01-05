const parser = require("@solidity-parser/parser");
const fs = require("fs");
const csv = require("csv-parser");
const { stringify } = require("csv-stringify")


function extract_contract(sol_files) {
    contracts = []
    for (let i = 0; i < 10; i++) {
        try {
            console.log(i)
            source = sol_files[i]["source_code"].replace('\r\n', '\n');
            const lines = source.split('\n');
            const ast = parser.parse(sol_files[i]["source_code"], {loc: true});
            for (let i = 0; i < ast["children"].length; i++) {
                if (ast["children"][i]["type"] == "ContractDefinition") {
                    const child = ast["children"][i]
                    if (child["kind"] == "contract") {
                        const start_line = child["loc"]["start"]["line"];
                        const start_col = child["loc"]["start"]["column"];
                        const end_line = child["loc"]["end"]["line"];
                        const end_col = child["loc"]["end"]["column"];
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
                        contracts.push([sol_files[i]["contract_address"], source.slice(start_idx, end_idx)])
                    }    
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


function read_csv(file_path) {
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


function write_csv(data, file_path, columns) {
    stringify(data, {header: true, columns: columns}, (err, output) => {
        if (err) throw err;
        fs.writeFileSync(file_path, output, (error) => {
            if (err) throw err;
            console.log("Saved");
        });
    });
}

async function main() {
    const contracts = await read_csv("./data/solfile/test_sol_file.csv").then((sol_files) => {
        return extract_contract(sol_files);
    });
    write_csv(contracts, "./out/test.csv", columns=["address", "contract_code"]);
}


function test_parser() {
    const data = fs.readFileSync("error.sol", "utf-8");
    try {
        const ast = parser.parse(data);
        console.log(ast);
    } catch (e) {
        console.log("Error")
        if (e instanceof parser.ParserError) {
            console.log(e.errors);
        }
    }   
}


function find_func_has_require(contract) {

}


function find_comment(contract) {
    let state = "ETC";
    let i = 0;
    let comments = [];
    let currentComment = null;

    while (i + 1 < contract.length) {
        if (state == "ETC" && contract[i] == '/' && contract[i + 1] == '/') {
            state = "LINE_COMMENT";
            currentComment = {
                "type": "LineComment",
                "range": {"start": i}
            };
            i += 2;
            continue;
        }

        if (state == "LINE_COMMENT" && contract[i] == '\n') {
            state = "ETC";
            currentComment["range"]["end"] = i;
            comments.push(currentComment);
            currentComment = null;
            i += 1;
            continue;
        }

        if (state == "ETC" && contract[i] == '/' && contract[i + 1] == '*') {
            state = "BLOCK_COMMENT";
            currentComment = {
                "type": "BlockComment",
                "range": {"start": i}
            };
            i += 2;
            continue;
        }

        if (state == "BLOCK_COMMENT" && contract[i] == '*' && contract[i + 1] == '/') {
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
        if (contract[i - 1] == '\n') {
            currentComment["range"]["end"] = contract.length - 1;
        } else {
            currentComment["range"]["end"] = contract.length;
        }
        comments.push(currentComment)
    }
    

    function extract_content(contract, comments) {
        for (let i = 0; i < comments.length; i++) {
            let start = comments[i]["range"]["start"] + 2;
            let end = comments[i]["type"] == "LineComment" ? comments[i]["range"]["end"] : comments[i]["range"]["end"] - 2;
            let raw = contract.slice(start, end);
            comments[i]["content"] = raw.trim();
        }
        comments = comments.filter((comment) => comment["content"]);
        return comments;
    }

    return extract_content(contract, comments);
}


function test_find_comment() {
    contract = fs.readFileSync("error.sol", "utf-8");
    comments = find_comment(contract);
    for (let i = 0; i < comments.length; i++) {
        console.log(`${comments[i]["content"]}\n---------------------------------------------------------`);
    }
}






