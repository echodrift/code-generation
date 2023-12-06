const parser = require('@solidity-parser/parser')

const input = `
    contract test {
        uint256 a;
        function f() {}
    }
`
try {
  const ast = parser.parse(input)
  console.log(ast["children"][0]["subNodes"])
} catch (e) {
  if (e instanceof parser.ParserError) {
    console.error(e.errors)
  }
}