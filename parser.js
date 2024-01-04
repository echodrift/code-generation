const parser = require("@solidity-parser/parser");
const fs = require("fs");
const csv = require("csv-parser");

function parse(sol_files) {
    csv_file = "contract_address,contract_code\n";
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
                        csv_file += `${sol_files[i]["contract_address"]},${source.slice(start_idx, end_idx)}\n`
                        fs.writeFileSync("./out/contracts.csv", csv_file)
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
    input = `// SPDX-License-Identifier: MIT
    pragma solidity >0.5.0 <0.8.0;
    
    /* Library Imports */
    import { Lib_Bytes32Utils } from "../../libraries/utils/Lib_Bytes32Utils.sol";
    import { Lib_OVMCodec } from "../../libraries/codec/Lib_OVMCodec.sol";
    import { Lib_ECDSAUtils } from "../../libraries/utils/Lib_ECDSAUtils.sol";
    import { Lib_SafeExecutionManagerWrapper } from "../../libraries/wrappers/Lib_SafeExecutionManagerWrapper.sol";
    
    /**
     * @title OVM_ProxyEOA
     * @dev The Proxy EOA contract uses a delegate call to execute the logic in an implementation contract.
     * In combination with the logic implemented in the ECDSA Contract Account, this enables a form of upgradable 
     * 'account abstraction' on layer 2. 
     * 
     * Compiler used: solc
     * Runtime target: OVM
     */
    contract OVM_ProxyEOA {
    
        /*************
         * Constants *
         *************/
    
        bytes32 constant IMPLEMENTATION_KEY = 0xdeaddeaddeaddeaddeaddeaddeaddeaddeaddeaddeaddeaddeaddeaddeaddead;
    
    
        /***************
         * Constructor *
         ***************/
    
        /**
         * @param _implementation Address of the initial implementation contract.
         */
        constructor(
            address _implementation
        )
        {
            _setImplementation(_implementation);
        }
    
    
        /*********************
         * Fallback Function *
         *********************/
    
        fallback()
            external
        {
            (bool success, bytes memory returndata) = Lib_SafeExecutionManagerWrapper.safeDELEGATECALL(
                gasleft(),
                getImplementation(),
                msg.data
            );
    
            if (success) {
                assembly {
                    return(add(returndata, 0x20), mload(returndata))
                }
            } else {
                Lib_SafeExecutionManagerWrapper.safeREVERT(
                    string(returndata)
                );
            }
        }
    
    
        /********************
         * Public Functions *
         ********************/
    
        /**
         * Changes the implementation address.
         * @param _implementation New implementation address.
         */
        function upgrade(
            address _implementation
        )
            external
        {
            Lib_SafeExecutionManagerWrapper.safeREQUIRE(
                Lib_SafeExecutionManagerWrapper.safeADDRESS() == Lib_SafeExecutionManagerWrapper.safeCALLER(),
                "EOAs can only upgrade their own EOA implementation"
            );
    
            _setImplementation(_implementation);
        }
    
        /**
         * Gets the address of the current implementation.
         * @return Current implementation address.
         */
        function getImplementation()
            public
            returns (
                address
            )
        {
            return Lib_Bytes32Utils.toAddress(
                Lib_SafeExecutionManagerWrapper.safeSLOAD(
                    IMPLEMENTATION_KEY
                )
            );
        }
    
    
        /**********************
         * Internal Functions *
         **********************/
    
        function _setImplementation(
            address _implementation
        )
            internal
        {
            Lib_SafeExecutionManagerWrapper.safeSSTORE(
                IMPLEMENTATION_KEY,
                Lib_Bytes32Utils.fromAddress(_implementation)
            );
        }
    }`

    try {
        const ast = parser.parse(input);
        console.log(ast)
    } catch (e) {
        if (e instanceof parser.ParserError) {
            console.log(e.errors)
        }
    }
}

main()