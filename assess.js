import parquetjs from "@dsnp/parquetjs"
import parser from "@solidity-parser/parser"

async function parsable(test_file) {
    let test_cases = []
    let reader = await parquetjs.ParquetReader.openFile(test_file)
    let cursor = reader.getCursor()
    let record = null
    while (record = await cursor.next()) {
        test_cases.push(record)
    }
    for (let i = 0; i < test_cases.length; i++) {
        const source = test_cases[i]["source_code"].replace("\r\n", "\n")
        const sourceUnit = parser.parse(source, {loc: true})
        

    }
}

async function compilable(test_file) {
    let test_cases = []
    let reader = await parquetjs.ParquetReader.openFile(test_file)
    let cursor = reader.getCursor()
    let record = null
    while (record = await cursor.next()) {
        test_cases.push(record)
    }
}