import { get_location } from "./parse_funcs.js"
import parser from "@solidity-parser/parser"
import parquetjs from "@dsnp/parquetjs"
import tqdm from "tqdm"
import { ArgumentParser } from "argparse"

async function parse_contract(file_source, output_file) {
    let sol_files = []
    let reader = await parquetjs.ParquetReader.openFile(file_source)
    let cursor = reader.getCursor()
    let record = null
    while (record = await cursor.next()) {
        sol_files.push(record)
    }

    var schema = new parquetjs.ParquetSchema({
        source_idx: parquetjs.ParquetFieldBuilder.createStringField(),
        contract_name: parquetjs.ParquetFieldBuilder.createStringField(),
        contract_source: parquetjs.ParquetFieldBuilder.createStringField()
    })
    var writer = await parquetjs.ParquetWriter.openFile(schema, output_file)
    for (const sol_file of tqdm(sol_files)) {
        try {
            const source = sol_file["source_code"].replace('\r\n', '\n')
            const sourceUnit = parser.parse(source, {loc: true})
            for (const child of sourceUnit["children"]) {
                if (child["type"] == "ContractDefinition" &&
                    child["kind"] == "contract") {
                        const contract_name = child["name"]
                        const [contract_start, contract_end] = get_location(source, child)
                        const contract_source = source.slice(contract_start, contract_end)
                        await writer.appendRow({
                            "source_idx": `${sol_file["source_idx"]}`,
                            "contract_name": contract_name, 
                            "contract_source": contract_source
                        })
                }
            }
        } catch (e) {
        }
    }
    writer.close()
}


async function main() {
    const parser = new ArgumentParser()
    parser.add_argument('-i', '--input')
    parser.add_argument('-o', '--output')
    const args = parser.parse_args()
    await parse_contract(args.input, args.output)
}

main()