class TestScriptGenerator:
    """TestScriptGenerator class"""

    def __init__(self, contract: str):
        """The constructor of the class

        Args:
            contract (str): Code in a solidity file
        """

        self.contract = contract

    def test_script_generator():
        import_lines = """const {
                        time,
                        loadFixture,
                        } = require("@nomicfoundation/hardhat-toolbox/network-helpers");
                        const { anyValue } = require("@nomicfoundation/hardhat-chai-matchers/withArgs");
                        const { expect } = require("chai");"""
        
        
