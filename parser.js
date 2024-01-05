const parser = require("@solidity-parser/parser");
const fs = require("fs");
const csv = require("csv-parser");
const { stringify } = require("csv-stringify")

function parse(sol_files) {
    contracts = []
    for (let i = 0; i < sol_files.length; i++) {
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
    const columns = ["contract_address", "contract_code"]
    stringify(contracts, {header: true, columns: columns}, (err, output) => {
        if (err) throw err;
        fs.writeFileSync("./out/contracts.csv", output, (error) => {
            if (err) throw err;
            console.log("Saved");
        })
    });
    
}

function main() {
    const test_sol_file = []
    fs.createReadStream("./data/solfile/test_sol_file.csv")
    .pipe(csv())
    .on('data', (data) => test_sol_file.push(data))
    .on('end', () => {
        parse(test_sol_file)
    })
}

function test() {
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

// main()

test()