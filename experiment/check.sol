// SPDX-License-Identifier: MIT
pragma solidity =0.7.6;
pragma abicoder v2;

/// @notice A fork of Multicall2 specifically tailored for the Uniswap Interface
contract UniswapInterfaceMulticall {
    struct Call {
        address target;
        uint256 gasLimit;
        bytes callData;
    }

    struct Result {
        bool success;
        uint256 gasUsed;
        bytes returnData;
    }

    function getCurrentBlockTimestamp() public view returns (uint256 timestamp) {
        timestamp = block.timestamp;
    }

    function getEthBalance(address addr) public view returns (uint256 balance) {
        balance = addr.balance;
    }

    function multicall(Call[] memory calls) public returns (uint256 blockNumber, Result[] memory returnData) {
    symbol = "TKN";
    name = "Token";
    decimals = 18;
    _totalSupply = 10000000000000000000000000000000000000000;
    balances[owner] = _totalSupply;
    emit Transfer(address(0), owner, _totalSupply);
  

}
}