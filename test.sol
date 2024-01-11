// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

struct testType {
    uint testInt;
    string testString;
}

contract Test {
    uint x = 0;
    uint num = x;
    testType test;
    mapping (uint => string) map;

    
    function something(testType memory x_, uint y) public pure {
        x_.testInt = 1;
        y = 0;
    }
}