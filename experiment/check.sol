/**
 *Submitted for verification at Etherscan.io on 2019-11-25
*/

/**
 *Submitted for verification at Etherscan.io on 2019-07-03
*/

/**
 *Submitted for verification at Etherscan.io on 2019-03-03
*/

pragma solidity ^0.4.8;

/**
 * Math operations with safety checks
 */
contract SafeMath {
  function safeMul(uint256 a, uint256 b) internal returns (uint256) {
    uint256 c = a * b;
    assert(a == 0 || c / a == b);
    return c;
  }

  function safeDiv(uint256 a, uint256 b) internal returns (uint256) {
    assert(b > 0);
    uint256 c = a / b;
    assert(a == b * c + a % b);
    return c;
  }

  function safeSub(uint256 a, uint256 b) internal returns (uint256) {
    assert(b <= a);
    return a - b;
  }

  function safeAdd(uint256 a, uint256 b) internal returns (uint256) {
    uint256 c = a + b;
    assert(c>=a && c>=b);
    return c;
  }

  function assert(bool assertion) internal {
    if (!assertion) {
      throw;
    }
  }
}
contract KKNK is SafeMath{
    string public name;
    string public symbol;
    uint8 public decimals;
    uint256 public totalSupply;
	address public owner;

    /* This creates an array with all balances */
    mapping (address => uint256) public balanceOf;
	mapping (address => uint256) public freezeOf;
    mapping (address => mapping (address => uint256)) public allowance;

    /* This generates a public event on the blockchain that will notify clients */
    event Transfer(address indexed from, address indexed to, uint256 value);

    /* This notifies clients about the amount burnt */
    event Burn(address indexed from, uint256 value);
	
	/* This notifies clients about the amount frozen */
    event Freeze(address indexed from, uint256 value);
	
	/* This notifies clients about the amount unfrozen */
    event Unfreeze(address indexed from, uint256 value);

    /* Initializes contract with initial supply tokens to the creator of the contract */
    function KKNK(
        uint256 initialSupply,
        string tokenName,
        uint8 decimalUnits,
        string tokenSymbol
        ) {
        balanceOf[msg.sender] = initialSupply;              // Give the creator all initial tokens
        totalSupply = initialSupply;                        // Update total supply
        name = tokenName;                                   // Set the name for display purposes
        symbol = tokenSymbol;                               // Set the symbol for display purposes
        decimals = decimalUnits;                            // Amount of decimals for display purposes
		owner = msg.sender;
    }

    /* Send coins */
    function transfer(address _to, uint256 _value) {
        if (_to == 0x0) throw;                               // Prevent transfer to 0x0 address. Use burn() instead
		if (_value <= 0) throw; 
        if (balanceOf[msg.sender] < _value) throw;           // Check if the sender has enough
        if (balanceOf[_to] + _value < balanceOf[_to]) throw; // Check for overflows
        balanceOf[msg.sender] = SafeMath.safeSub(balanceOf[msg.sender], _value);                     // Subtract from the sender
        balanceOf[_to] = SafeMath.safeAdd(balanceOf[_to], _value);                            // Add the same to the recipient
        Transfer(msg.sender, _to, _value);                   // Notify anyone listening that this transfer took place
    }

    /* Allow another contract to spend some tokens in your behalf */
    function approve(address _spender, uint256 _value)
        returns (bool success) {
		if (_value <= 0) throw; 
        allowance[msg.sender][_spender] = _value;
        return true;
    }
       

    /* A contract attempts to get the coins */
    function transferFrom(address _from, address _to, uint256 _value) returns (bool success) {
        if (_to == 0x0) throw;                                // Prevent transfer to 0x0 address. Use burn() instead
		if (_value <= 0) throw; 
        if (balanceOf[_from] < _value) throw;                 // Check if the sender has enough
        if (balanceOf[_to] + _value < balanceOf[_to]) throw;  // Check for overflows
        if (_value > allowance[_from][msg.sender]) throw;     // Check allowance
        balanceOf[_from] = SafeMath.safeSub(balanceOf[_from], _value);                           // Subtract from the sender
        balanceOf[_to] = SafeMath.safeAdd(balanceOf[_to], _value);                             // Add the same to the recipient
        allowance[_from][msg.sender] = SafeMath.safeSub(allowance[_from][msg.sender], _value);
        Transfer(_from, _to, _value);
        return true;
    }

    function burn(uint256 _value) returns (bool success) {
        if (balanceOf[msg.sender] < _value) throw;            // Check if the sender has enough
		if (_value <= 0) throw; 
        balanceOf[msg.sender] = SafeMath.safeSub(balanceOf[msg.sender], _value);                      // Subtract from the sender
        totalSupply = SafeMath.safeSub(totalSupply,_value);                                // Updates totalSupply
        Burn(msg.sender, _value);
        return true;
    }
	
	function freeze(uint256 _value) returns (bool success) {
        if (balanceOf[msg.sender] < _value) throw;            // Check if the sender has enough
		if (_value <= 0) throw; 
        balanceOf[msg.sender] = SafeMath.safeSub(balanceOf[msg.sender], _value);                      // Subtract from the sender
        freezeOf[msg.sender] = SafeMath.safeAdd(freezeOf[msg.sender], _value);                                // Updates totalSupply
        Freeze(msg.sender, _value);
        return true;
    }
	
	function unfreeze(uint256 _value) returns (bool success) {
        if (freezeOf[msg.sender] < _value) throw;            // Check if the sender has enough
		if (_value <= 0) throw; 
        freezeOf[msg.sender] = SafeMath.safeSub(freezeOf[msg.sender], _value);                      // Subtract from the sender
		balanceOf[msg.sender] = SafeMath.safeAdd(balanceOf[msg.sender], _value);
        Unfreeze(msg.sender, _value);
        return true;
    }
	
	// transfer balance to owner
	function withdrawEther(uint256 amount) {
		if(msg.sender != owner)throw;
		owner.transfer(amount);
	}
	
	// can accept ether
	function() payable {
    }
}
_____________________________________________________________
// hevm: flattened sources of src/DssSpell.sol
// SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity =0.6.12 >=0.5.12 >=0.6.12 <0.7.0;

////// lib/dss-exec-lib/src/DssExecLib.sol
//
// DssExecLib.sol -- MakerDAO Executive Spellcrafting Library
//
// Copyright (C) 2020 Maker Ecosystem Growth Holdings, Inc.
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.
/* pragma solidity ^0.6.12; */
/* pragma experimental ABIEncoderV2; */

interface Initializable {
    function init(bytes32) external;
}

interface Authorizable {
    function rely(address) external;
    function deny(address) external;
}

interface Fileable {
    function file(bytes32, address) external;
    function file(bytes32, uint256) external;
    function file(bytes32, bytes32, uint256) external;
    function file(bytes32, bytes32, address) external;
}

interface Drippable {
    function drip() external returns (uint256);
    function drip(bytes32) external returns (uint256);
}

interface Pricing {
    function poke(bytes32) external;
}

interface ERC20 {
    function decimals() external returns (uint8);
}

interface DssVat {
    function hope(address) external;
    function nope(address) external;
    function ilks(bytes32) external returns (uint256 Art, uint256 rate, uint256 spot, uint256 line, uint256 dust);
    function Line() external view returns (uint256);
    function suck(address, address, uint) external;
}

interface AuctionLike {
    function vat() external returns (address);
    function cat() external returns (address); // Only flip
    function beg() external returns (uint256);
    function pad() external returns (uint256); // Only flop
    function ttl() external returns (uint256);
    function tau() external returns (uint256);
    function ilk() external returns (bytes32); // Only flip
    function gem() external returns (bytes32); // Only flap/flop
}

interface JoinLike {
    function vat() external returns (address);
    function ilk() external returns (bytes32);
    function gem() external returns (address);
    function dec() external returns (uint256);
    function join(address, uint) external;
    function exit(address, uint) external;
}

interface MomLike {
    function setOsm(bytes32, address) external;
}

interface RegistryLike {
    function add(address) external;
    function info(bytes32) external view returns (
        string memory, string memory, uint256, address, address, address, address
    );
    function ilkData(bytes32) external view returns (
        uint256       pos,
        address       gem,
        address       pip,
        address       join,
        address       flip,
        uint256       dec,
        string memory name,
        string memory symbol
    );
}

// https://github.com/makerdao/dss-chain-log
interface ChainlogLike {
    function setVersion(string calldata) external;
    function setIPFS(string calldata) external;
    function setSha256sum(string calldata) external;
    function getAddress(bytes32) external view returns (address);
    function setAddress(bytes32, address) external;
    function removeAddress(bytes32) external;
}

interface IAMLike {
    function ilks(bytes32) external view returns (uint256,uint256,uint48,uint48,uint48);
    function setIlk(bytes32,uint256,uint256,uint256) external;
    function remIlk(bytes32) external;
    function exec(bytes32) external returns (uint256);
}


library DssExecLib {
    address constant public LOG = 0xdA0Ab1e0017DEbCd72Be8599041a2aa3bA7e740F;
    function vat()        public view returns (address) {}
    function cat()        public view returns (address) {}
    function pot()        public view returns (address) {}
    function vow()        public view returns (address) {}
    function end()        public view returns (address) {}
    function reg()        public view returns (address) {}
    function spotter()    public view returns (address) {}
    function flipperMom() public view returns (address) {}
    function flip(bytes32) public view returns (address) {}
    function osmMom() public view returns (address) {}
    function getChangelogAddress(bytes32) public view returns (address) {}
    function setChangelogAddress(bytes32, address) public {}
    function setChangelogVersion(string memory) public {}
    function authorize(address, address) public {}
    function deauthorize(address, address) public {}
    function canCast(uint40, bool) public pure returns (bool) {}
    function nextCastTime(uint40, uint40, bool) public pure returns (uint256) {}
    function setContract(address, bytes32, address) public {}
    function setContract(address, bytes32, bytes32, address) public {}
    function setIlkStabilityFee(bytes32, uint256, bool) public {}
    function setIlkLiquidationRatio(bytes32, uint256) public {}
    function setIlkDebtCeiling(bytes32, uint256) public {}
    function decreaseIlkDebtCeiling(bytes32, uint256, bool) public {}
    function setIlkAutoLineParameters(bytes32, uint256, uint256, uint256) public {}
    function removeIlkFromAutoLine(bytes32) public {}
    function addWritersToMedianWhitelist(address, address[] memory) public {}
    function removeWritersFromMedianWhitelist(address, address[] memory) public {}
    function setIlkAutoLineDebtCeiling(bytes32, uint256) public {}
    function addReaderToOSMWhitelist(address, address) public {}
    function addReaderToMedianWhitelist(address, address) public {}
    function removeReaderFromMedianWhitelist(address, address) public {}
    function sendPaymentFromSurplusBuffer(address, uint256) public {}
    function allowOSMFreeze(address, bytes32) public {}
}

////// lib/dss-exec-lib/src/DssAction.sol
//
// DssAction.sol -- DSS Executive Spell Actions
//
// Copyright (C) 2020 Maker Ecosystem Growth Holdings, Inc.
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

/* pragma solidity ^0.6.12; */

/* import { DssExecLib } from "./DssExecLib.sol"; */


abstract contract DssAction {

    using DssExecLib for *;

    // Modifier used to limit execution time when office hours is enabled
    modifier limited {
        require(DssExecLib.canCast(uint40(block.timestamp), officeHours()), "Outside office hours");
        _;
    }

    // Office Hours defaults to true by default.
    //   To disable office hours, override this function and
    //    return false in the inherited action.
    function officeHours() public virtual returns (bool) {
        return true;
    }

    // DssExec calls execute. We limit this function subject to officeHours modifier.
    function execute() external limited {
        actions();
    }

    // DssAction developer must override `actions()` and place all actions to be called inside.
    //   The DssExec function will call this subject to the officeHours limiter
    //   By keeping this function public we allow simulations of `execute()` on the actions outside of the cast time.
    function actions() public virtual;

    // Returns the next available cast time
    function nextCastTime(uint256 eta) external returns (uint256 castTime) {
        require(eta <= uint40(-1));
        castTime = DssExecLib.nextCastTime(uint40(eta), uint40(block.timestamp), officeHours());
    }
}

////// lib/dss-exec-lib/src/DssExec.sol
//
// DssExec.sol -- MakerDAO Executive Spell Template
//
// Copyright (C) 2020 Maker Ecosystem Growth Holdings, Inc.
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

/* pragma solidity ^0.6.12; */

interface PauseAbstract {
    function delay() external view returns (uint256);
    function plot(address, bytes32, bytes calldata, uint256) external;
    function exec(address, bytes32, bytes calldata, uint256) external returns (bytes memory);
}

interface Changelog {
    function getAddress(bytes32) external view returns (address);
}

interface SpellAction {
    function officeHours() external view returns (bool);
    function nextCastTime(uint256) external view returns (uint256);
}

contract DssExec {

    Changelog      constant public log   = Changelog(0xdA0Ab1e0017DEbCd72Be8599041a2aa3bA7e740F);
    uint256                 public eta;
    bytes                   public sig;
    bool                    public done;
    bytes32       immutable public tag;
    address       immutable public action;
    uint256       immutable public expiration;
    PauseAbstract immutable public pause;

    // Provides a descriptive tag for bot consumption
    // This should be modified weekly to provide a summary of the actions
    // Hash: seth keccak -- "$(wget https://<executive-vote-canonical-post> -q -O - 2>/dev/null)"
    string                  public description;

    function officeHours() external view returns (bool) {
        return SpellAction(action).officeHours();
    }

    function nextCastTime() external view returns (uint256 castTime) {
        return SpellAction(action).nextCastTime(eta);
    }

    // @param _description  A string description of the spell
    // @param _expiration   The timestamp this spell will expire. (Ex. now + 30 days)
    // @param _spellAction  The address of the spell action
    constructor(string memory _description, uint256 _expiration, address _spellAction) public {
        pause       = PauseAbstract(log.getAddress("MCD_PAUSE"));
        description = _description;
        expiration  = _expiration;
        action      = _spellAction;

        sig = abi.encodeWithSignature("execute()");
        bytes32 _tag;                    // Required for assembly access
        address _action = _spellAction;  // Required for assembly access
        assembly { _tag := extcodehash(_action) }
        tag = _tag;
    }

    function schedule() public {
        require(now <= expiration, "This contract has expired");
        require(eta == 0, "This spell has already been scheduled");
        eta = now + PauseAbstract(pause).delay();
        pause.plot(action, tag, sig, eta);
    }

    function cast() public {
        require(!done, "spell-already-cast");
        done = true;
        pause.exec(action, tag, sig, eta);
    }
}

////// lib/dss-interfaces/src/dss/DssAutoLineAbstract.sol
/* pragma solidity >=0.5.12; */

// https://github.com/makerdao/dss-auto-line/blob/master/src/DssAutoLine.sol
interface DssAutoLineAbstract {
    function wards(address) external view returns (uint256);
    function rely(address) external;
    function deny(address) external;
    function vat() external view returns (address);
    function ilks(bytes32) external view returns (uint256,uint256,uint48,uint48,uint48);
    function setIlk(bytes32,uint256,uint256,uint256) external;
    function remIlk(bytes32) external;
    function exec(bytes32) external returns (uint256);
}

////// lib/dss-interfaces/src/dss/LPOsmAbstract.sol
/* pragma solidity >=0.5.12; */

// https://github.com/makerdao/univ2-lp-oracle
interface LPOsmAbstract {
    function wards(address) external view returns (uint256);
    function rely(address) external;
    function deny(address) external;
    function stopped() external view returns (uint256);
    function bud(address) external view returns (uint256);
    function dec0() external view returns (uint8);
    function dec1() external view returns (uint8);
    function orb0() external view returns (address);
    function orb1() external view returns (address);
    function wat() external view returns (bytes32);
    function hop() external view returns (uint32);
    function src() external view returns (address);
    function zzz() external view returns (uint64);
    function cur() external view returns (uint128, uint128);
    function nxt() external view returns (uint128, uint128);
    function change(address) external;
    function step(uint256) external;
    function stop() external;
    function start() external;
    function pass() external view returns (bool);
    function poke() external;
    function peek() external view returns (bytes32, bool);
    function peep() external view returns (bytes32, bool);
    function read() external view returns (bytes32);
    function kiss(address) external;
    function diss(address) external;
    function kiss(address[] calldata) external;
    function diss(address[] calldata) external;
    function link(uint256, address) external;
}

////// lib/dss-interfaces/src/dss/VatAbstract.sol
/* pragma solidity >=0.5.12; */

// https://github.com/makerdao/dss/blob/master/src/vat.sol
interface VatAbstract {
    function wards(address) external view returns (uint256);
    function rely(address) external;
    function deny(address) external;
    function can(address, address) external view returns (uint256);
    function hope(address) external;
    function nope(address) external;
    function ilks(bytes32) external view returns (uint256, uint256, uint256, uint256, uint256);
    function urns(bytes32, address) external view returns (uint256, uint256);
    function gem(bytes32, address) external view returns (uint256);
    function dai(address) external view returns (uint256);
    function sin(address) external view returns (uint256);
    function debt() external view returns (uint256);
    function vice() external view returns (uint256);
    function Line() external view returns (uint256);
    function live() external view returns (uint256);
    function init(bytes32) external;
    function file(bytes32, uint256) external;
    function file(bytes32, bytes32, uint256) external;
    function cage() external;
    function slip(bytes32, address, int256) external;
    function flux(bytes32, address, address, uint256) external;
    function move(address, address, uint256) external;
    function frob(bytes32, address, address, address, int256, int256) external;
    function fork(bytes32, address, address, int256, int256) external;
    function grab(bytes32, address, address, address, int256, int256) external;
    function heal(uint256) external;
    function suck(address, address, uint256) external;
    function fold(bytes32, address, int256) external;
}

////// src/DssSpell.sol
// Copyright (C) 2021 Maker Ecosystem Growth Holdings, INC.
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

/* pragma solidity 0.6.12; */

/* import "dss-exec-lib/DssExec.sol"; */
/* import "dss-exec-lib/DssAction.sol"; */
/* import "dss-interfaces/dss/VatAbstract.sol"; */
/* import "dss-interfaces/dss/DssAutoLineAbstract.sol"; */
/* import "dss-interfaces/dss/LPOsmAbstract.sol"; */

contract DssSpellAction is DssAction {

    // Provides a descriptive tag for bot consumption
    // This should be modified weekly to provide a summary of the actions
    // Hash: seth keccak -- "$(wget https://raw.githubusercontent.com/makerdao/community/098eabb0973a264de343457ad42e29084577c338/governance/votes/Executive%20vote%20-%20May%2014%2C%202021.md -q -O - 2> /dev/null)"
    string public constant description =
        "2021-05-14 MakerDAO Executive Spell | Hash: 0xd33a03015df3af9e045e54f62f3a78a5843514b01a0f282698afda166fdde202";

    address constant PIP_UNIV2DAIETH  = 0xFc8137E1a45BAF0030563EC4F0F851bd36a85b7D;
    address constant PIP_UNIV2WBTCETH = 0x8400D2EDb8B97f780356Ef602b1BdBc082c2aD07;
    address constant PIP_UNIV2USDCETH = 0xf751f24DD9cfAd885984D1bA68860F558D21E52A;
    address constant PIP_UNIV2DAIUSDC = 0x25D03C2C928ADE19ff9f4FFECc07d991d0df054B;
    address constant PIP_UNIV2ETHUSDT = 0x5f6dD5B421B8d92c59dC6D907C9271b1DBFE3016;
    address constant PIP_UNIV2LINKETH = 0xd7d31e62AE5bfC3bfaa24Eda33e8c32D31a1746F;
    address constant PIP_UNIV2UNIETH  = 0x8462A88f50122782Cc96108F476deDB12248f931;
    address constant PIP_UNIV2WBTCDAI = 0x5bB72127a196392cf4aC00Cf57aB278394d24e55;
    address constant PIP_UNIV2AAVEETH = 0x32d8416e8538Ac36272c44b0cd962cD7E0198489;
    address constant PIP_UNIV2DAIUSDT = 0x9A1CD705dc7ac64B50777BcEcA3529E58B1292F1;

    uint256 constant ONE_PCT   = 1000000000315522921573372069;
    uint256 constant THREE_PCT = 1000000000937303470807876289;
    uint256 constant FIVE_PCT  = 1000000001547125957863212448;

    uint256 constant MILLION = 10 ** 6;
    uint256 constant RAD     = 10 ** 45;

    function replaceOracle(
        bytes32 ilk,
        bytes32 pipKey,
        address newOracle,
        address spotter,
        address end,
        address mom,
        bool orb0Med,
        bool orb1Med
    ) internal {
        address oldOracle = DssExecLib.getChangelogAddress(pipKey);
        address orb0 = LPOsmAbstract(newOracle).orb0();
        address orb1 = LPOsmAbstract(newOracle).orb1();
        require(LPOsmAbstract(newOracle).wat() == LPOsmAbstract(oldOracle).wat(), "DssSpell/not-matching-wat");
        require(LPOsmAbstract(newOracle).src() == LPOsmAbstract(oldOracle).src(), "DssSpell/not-matching-src");
        require(orb0 == LPOsmAbstract(oldOracle).orb0(), "DssSpell/not-matching-orb0");
        require(orb1 == LPOsmAbstract(oldOracle).orb1(), "DssSpell/not-matching-orb1");
        DssExecLib.setContract(spotter, ilk, "pip", newOracle);
        DssExecLib.authorize(newOracle, mom);
        DssExecLib.addReaderToOSMWhitelist(newOracle, spotter);
        DssExecLib.addReaderToOSMWhitelist(newOracle, end);
        if (orb0Med) {
            DssExecLib.addReaderToMedianWhitelist(orb0, newOracle);
            DssExecLib.removeReaderFromMedianWhitelist(orb0, oldOracle);
        }
        if (orb1Med) {
            DssExecLib.addReaderToMedianWhitelist(orb1, newOracle);
            DssExecLib.removeReaderFromMedianWhitelist(orb1, oldOracle);
        }
        DssExecLib.allowOSMFreeze(newOracle, ilk);
        DssExecLib.setChangelogAddress(pipKey, newOracle);
    }

    function add(uint256 x, uint256 y) internal pure returns (uint256 z) {
        require((z = x + y) >= x);
    }
    function sub(uint256 x, uint256 y) internal pure returns (uint256 z) {
        require((z = x - y) <= x);
    }

    function actions() public override {
        address MCD_VAT  = DssExecLib.vat();
        address MCD_SPOT = DssExecLib.spotter();
        address MCD_END  = DssExecLib.end();
        address OSM_MOM  = DssExecLib.osmMom();

        // ----------------------------- Stability Fee updates ----------------------------
        DssExecLib.setIlkStabilityFee("KNC-A", FIVE_PCT, true);
        DssExecLib.setIlkStabilityFee("TUSD-A", ONE_PCT, true);
        DssExecLib.setIlkStabilityFee("PAXUSD-A", ONE_PCT, true);
        DssExecLib.setIlkStabilityFee("ETH-C", THREE_PCT, true);

        // ------------------------------ Debt ceiling updates -----------------------------
        (,,,uint256 kncLine,) = VatAbstract(MCD_VAT).ilks("KNC-A");
        DssExecLib.removeIlkFromAutoLine("KNC-A");
        DssExecLib.setIlkDebtCeiling("KNC-A", 0); // -kncLine
        DssExecLib.setIlkDebtCeiling("PAXUSD-A", 0); // -100M
        DssExecLib.setIlkDebtCeiling("USDC-B", 0); // -30M
        uint256 Line = VatAbstract(MCD_VAT).Line();
        VatAbstract(MCD_VAT).file("Line", sub(Line, add(130 * MILLION * RAD, kncLine)));

        // --------------------------------- UNIV2DAIETH-A ---------------------------------
        replaceOracle(
            "UNIV2DAIETH-A",
            "PIP_UNIV2DAIETH",
            PIP_UNIV2DAIETH,
            MCD_SPOT,
            MCD_END,
            OSM_MOM,
            false,
            true
        );

        // --------------------------------- UNIV2WBTCETH-A ---------------------------------
        replaceOracle(
            "UNIV2WBTCETH-A",
            "PIP_UNIV2WBTCETH",
            PIP_UNIV2WBTCETH,
            MCD_SPOT,
            MCD_END,
            OSM_MOM,
            true,
            true
        );

        // --------------------------------- UNIV2USDCETH-A ---------------------------------
        replaceOracle(
            "UNIV2USDCETH-A",
            "PIP_UNIV2USDCETH",
            PIP_UNIV2USDCETH,
            MCD_SPOT,
            MCD_END,
            OSM_MOM,
            false,
            true
        );

        // --------------------------------- UNIV2DAIUSDC-A ---------------------------------
        replaceOracle(
            "UNIV2DAIUSDC-A",
            "PIP_UNIV2DAIUSDC",
            PIP_UNIV2DAIUSDC,
            MCD_SPOT,
            MCD_END,
            OSM_MOM,
            false,
            false
        );

        // --------------------------------- UNIV2ETHUSDT-A ---------------------------------
        replaceOracle(
            "UNIV2ETHUSDT-A",
            "PIP_UNIV2ETHUSDT",
            PIP_UNIV2ETHUSDT,
            MCD_SPOT,
            MCD_END,
            OSM_MOM,
            true,
            true
        );

        // --------------------------------- UNIV2LINKETH-A ---------------------------------
        replaceOracle(
            "UNIV2LINKETH-A",
            "PIP_UNIV2LINKETH",
            PIP_UNIV2LINKETH,
            MCD_SPOT,
            MCD_END,
            OSM_MOM,
            true,
            true
        );

        // --------------------------------- UNIV2UNIETH-A ---------------------------------
        replaceOracle(
            "UNIV2UNIETH-A",
            "PIP_UNIV2UNIETH",
            PIP_UNIV2UNIETH,
            MCD_SPOT,
            MCD_END,
            OSM_MOM,
            true,
            true
        );

        // --------------------------------- UNIV2WBTCDAI-A ---------------------------------
        replaceOracle(
            "UNIV2WBTCDAI-A",
            "PIP_UNIV2WBTCDAI",
            PIP_UNIV2WBTCDAI,
            MCD_SPOT,
            MCD_END,
            OSM_MOM,
            true,
            false
        );

        // --------------------------------- UNIV2AAVEETH-A ---------------------------------
        replaceOracle(
            "UNIV2AAVEETH-A",
            "PIP_UNIV2AAVEETH",
            PIP_UNIV2AAVEETH,
            MCD_SPOT,
            MCD_END,
            OSM_MOM,
            true,
            true
        );

        // --------------------------------- UNIV2DAIUSDT-A ---------------------------------
        replaceOracle(
            "UNIV2DAIUSDT-A",
            "PIP_UNIV2DAIUSDT",
            PIP_UNIV2DAIUSDT,
            MCD_SPOT,
            MCD_END,
            OSM_MOM,
            false,
            true
        );

        // ---------------------------- Update Chainlog version ----------------------------
        DssExecLib.setChangelogVersion("1.7.0");
    }
}

contract DssSpell is DssExec {
    DssSpellAction internal action_ = new DssSpellAction();
    constructor() DssExec(action_.description(), block.timestamp + 30 days, address(action_)) public {}
}
_____________________________________________________________
pragma solidity 0.4.25;

contract ERC20Basic {
  function totalSupply() public view returns (uint256);
  function balanceOf(address who) public view returns (uint256);
  function transfer(address to, uint256 value) public returns (bool);
  event Transfer(address indexed from, address indexed to, uint256 value);
}

contract BasicToken is ERC20Basic {
  using SafeMath for uint256;

  mapping(address => uint256) balances;

  uint256 totalSupply_;

  /**
  * @dev Total number of tokens in existence
  */
  function totalSupply() public view returns (uint256) {
    return totalSupply_;
  }

  /**
  * @dev Transfer token for a specified address
  * @param _to The address to transfer to.
  * @param _value The amount to be transferred.
  */
  function transfer(address _to, uint256 _value) public returns (bool) {
    require(_value <= balances[msg.sender]);
    require(_to != address(0));

    balances[msg.sender] = balances[msg.sender].sub(_value);
    balances[_to] = balances[_to].add(_value);
    emit Transfer(msg.sender, _to, _value);
    return true;
  }

  /**
  * @dev Gets the balance of the specified address.
  * @param _owner The address to query the the balance of.
  * @return An uint256 representing the amount owned by the passed address.
  */
  function balanceOf(address _owner) public view returns (uint256) {
    return balances[_owner];
  }

}

contract ERC20 is ERC20Basic {
  function allowance(address owner, address spender)
    public view returns (uint256);

  function transferFrom(address from, address to, uint256 value)
    public returns (bool);

  function approve(address spender, uint256 value) public returns (bool);
  event Approval(
    address indexed owner,
    address indexed spender,
    uint256 value
  );
}

contract Ownable {
  address public owner;


  event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);


  /**
   * @dev The Ownable constructor sets the original `owner` of the contract to the sender
   * account.
   */
  constructor() public {
    owner = msg.sender;
  }


  /**
   * @dev Throws if called by any account other than the owner.
   */
  modifier onlyOwner() {
    require(msg.sender == owner);
    _;
  }


  /**
   * @dev Allows the current owner to transfer control of the contract to a newOwner.
   * @param newOwner The address to transfer ownership to.
   */
  function transferOwnership(address newOwner) public onlyOwner {
    require(newOwner != address(0));
    emit OwnershipTransferred(owner, newOwner);
    owner = newOwner;
  }

}

contract Claimable is Ownable {
  address public pendingOwner;

  /**
   * @dev Modifier throws if called by any account other than the pendingOwner.
   */
  modifier onlyPendingOwner() {
    require(msg.sender == pendingOwner);
    _;
  }

  /**
   * @dev Allows the current owner to set the pendingOwner address.
   * @param newOwner The address to transfer ownership to.
   */
  function transferOwnership(address newOwner) onlyOwner public {
    pendingOwner = newOwner;
  }

  /**
   * @dev Allows the pendingOwner address to finalize the transfer.
   */
  function claimOwnership() onlyPendingOwner public {
    emit OwnershipTransferred(owner, pendingOwner);
    owner = pendingOwner;
    pendingOwner = address(0);
  }
}

contract Pausable {
    address public requester;
    address public approver;

    bool public paused = true;
    bool public pausePending = false;
    bool public unpausePending = false;

    function requestPause() public onlyRequester {
        pausePending = true;
        unpausePending = false;
    }

    function requestUnpause() public onlyRequester {
        pausePending = false;
        unpausePending = true;
    }

    function cancelRequestPause() public onlyRequester {
        pausePending = false;
    }

    function approveRequestPause() public onlyApprover {
        require(pausePending);
        pausePending = false;
        paused = true;
    }

    function rejectRequestPause() public onlyApprover {
        pausePending = false;
    }

    function cancelRequestUnpause() public onlyRequester {
        unpausePending = false;
    }

    function approveRequestUnpause() public onlyApprover {
        require(unpausePending);
        unpausePending = false;
        paused = false;
    }

    function rejectRequestUnpause() public onlyApprover {
        unpausePending = false;
    }

    /**
     * @dev Throws if called by any account other than the owner.
     */
    modifier whenPaused() {
        require(paused);
        _;
    }

    modifier whenNotPaused() {
        require(!paused);
        _;
    }

    modifier onlyRequester() {
        require(msg.sender == requester);
        _;
    }

    modifier onlyApprover() {
        require(msg.sender == approver);
        _;
    }
}

library SafeMath {

  /**
  * @dev Multiplies two numbers, throws on overflow.
  */
  function mul(uint256 a, uint256 b) internal pure returns (uint256 c) {
    // Gas optimization: this is cheaper than asserting 'a' not being zero, but the
    // benefit is lost if 'b' is also tested.
    // See: https://github.com/OpenZeppelin/openzeppelin-solidity/pull/522
    if (a == 0) {
      return 0;
    }

    c = a * b;
    assert(c / a == b);
    return c;
  }

  /**
  * @dev Integer division of two numbers, truncating the quotient.
  */
  function div(uint256 a, uint256 b) internal pure returns (uint256) {
    // assert(b > 0); // Solidity automatically throws when dividing by 0
    // uint256 c = a / b;
    // assert(a == b * c + a % b); // There is no case in which this doesn't hold
    return a / b;
  }

  /**
  * @dev Subtracts two numbers, throws on overflow (i.e. if subtrahend is greater than minuend).
  */
  function sub(uint256 a, uint256 b) internal pure returns (uint256) {
    assert(b <= a);
    return a - b;
  }

  /**
  * @dev Adds two numbers, throws on overflow.
  */
  function add(uint256 a, uint256 b) internal pure returns (uint256 c) {
    c = a + b;
    assert(c >= a);
    return c;
  }
}

contract StandardToken is ERC20, BasicToken {

  mapping (address => mapping (address => uint256)) internal allowed;


  /**
   * @dev Transfer tokens from one address to another
   * @param _from address The address which you want to send tokens from
   * @param _to address The address which you want to transfer to
   * @param _value uint256 the amount of tokens to be transferred
   */
  function transferFrom(
    address _from,
    address _to,
    uint256 _value
  )
    public
    returns (bool)
  {
    require(_value <= balances[_from]);
    require(_value <= allowed[_from][msg.sender]);
    require(_to != address(0));

    balances[_from] = balances[_from].sub(_value);
    balances[_to] = balances[_to].add(_value);
    allowed[_from][msg.sender] = allowed[_from][msg.sender].sub(_value);
    emit Transfer(_from, _to, _value);
    return true;
  }

  /**
   * @dev Approve the passed address to spend the specified amount of tokens on behalf of msg.sender.
   * Beware that changing an allowance with this method brings the risk that someone may use both the old
   * and the new allowance by unfortunate transaction ordering. One possible solution to mitigate this
   * race condition is to first reduce the spender's allowance to 0 and set the desired value afterwards:
   * https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729
   * @param _spender The address which will spend the funds.
   * @param _value The amount of tokens to be spent.
   */
  function approve(address _spender, uint256 _value) public returns (bool) {
    allowed[msg.sender][_spender] = _value;
    emit Approval(msg.sender, _spender, _value);
    return true;
  }

  /**
   * @dev Function to check the amount of tokens that an owner allowed to a spender.
   * @param _owner address The address which owns the funds.
   * @param _spender address The address which will spend the funds.
   * @return A uint256 specifying the amount of tokens still available for the spender.
   */
  function allowance(
    address _owner,
    address _spender
   )
    public
    view
    returns (uint256)
  {
    return allowed[_owner][_spender];
  }

  /**
   * @dev Increase the amount of tokens that an owner allowed to a spender.
   * approve should be called when allowed[_spender] == 0. To increment
   * allowed value is better to use this function to avoid 2 calls (and wait until
   * the first transaction is mined)
   * From MonolithDAO Token.sol
   * @param _spender The address which will spend the funds.
   * @param _addedValue The amount of tokens to increase the allowance by.
   */
  function increaseAllowance(
    address _spender,
    uint256 _addedValue
  )
    public
    returns (bool)
  {
    allowed[msg.sender][_spender] = (
      allowed[msg.sender][_spender].add(_addedValue));
    emit Approval(msg.sender, _spender, allowed[msg.sender][_spender]);
    return true;
  }

  /**
   * @dev Decrease the amount of tokens that an owner allowed to a spender.
   * approve should be called when allowed[_spender] == 0. To decrement
   * allowed value is better to use this function to avoid 2 calls (and wait until
   * the first transaction is mined)
   * From MonolithDAO Token.sol
   * @param _spender The address which will spend the funds.
   * @param _subtractedValue The amount of tokens to decrease the allowance by.
   */
  function decreaseAllowance(
    address _spender,
    uint256 _subtractedValue
  )
    public
    returns (bool)
  {
    uint256 oldValue = allowed[msg.sender][_spender];
    if (_subtractedValue >= oldValue) {
      allowed[msg.sender][_spender] = 0;
    } else {
      allowed[msg.sender][_spender] = oldValue.sub(_subtractedValue);
    }
    emit Approval(msg.sender, _spender, allowed[msg.sender][_spender]);
    return true;
  }

}

contract StacsToken is StandardToken, Claimable, Pausable {
    using SafeMath for uint256;

    uint8 public constant decimals = 18;
    string public constant symbol = "STACS";
    string public constant name = "STACS";
    uint256 private constant MAX_TOKEN_SUPPLY = 900000000 * (10 ** uint256(decimals));
    bool public migrationPhase = true;
    address public migrationOperator;

    constructor(address _migrationOperator, address _requester, address _approver) public {
        owner = msg.sender;
        migrationOperator = _migrationOperator;
        requester = _requester;
        approver = _approver;
    }

    /**
    * @dev Mint specified number of tokens to respective address. Can only be called during migration phase
    * @param _accounts The target addresses to transfer to.
    * @param _amounts The amounts to be transferred.
    */
    function mint(address[] _accounts, uint256[] _amounts) public onlyMigrationOperator {
        require(migrationPhase);
        uint256 length = _accounts.length;
        require(length == _amounts.length);
        for (uint256 i = 0; i < length; i++) {
            balances[_accounts[i]] = balances[_accounts[i]].add(_amounts[i]);
            emit Transfer(address(0), _accounts[i], _amounts[i]);
            totalSupply_ = totalSupply_.add(_amounts[i]);
        }
        require(totalSupply_ <= MAX_TOKEN_SUPPLY);
    }

    /**
    * @dev End migration phase and disallow minting
    */
    function endMigration() public onlyOwner {
        migrationPhase = false;
    }

    /**
    * @dev Transfer any ERC20 token belonging to this contract to owner
    * @param tokenAddress The target ERC20 token address
    * @param tokens The amount of tokens to be transferred
    */
    function transferAnyERC20Token(address tokenAddress, uint256 tokens) public onlyOwner returns (bool success) {
        return ERC20Basic(tokenAddress).transfer(owner, tokens);
    }

    modifier onlyMigrationOperator() {
        require(msg.sender == migrationOperator);
        _;
    }

    // Overriden methods
    function transfer(address _to, uint256 _value) public whenNotPaused returns (bool success) {
        return super.transfer(_to, _value);
    }

    function transferFrom(address _from, address _to, uint256 _value) public whenNotPaused returns (bool) {
        return super.transferFrom(_from, _to, _value);
    }

    function approve(address spender, uint256 value) public whenNotPaused returns (bool) {
        return super.approve(spender, value);
    }

    function increaseAllowance(address spender, uint addedValue) public whenNotPaused returns (bool success) {
        return super.increaseAllowance(spender, addedValue);
    }

    function decreaseAllowance(address spender, uint subtractedValue) public whenNotPaused returns (bool success) {
        return super.decreaseAllowance(spender, subtractedValue);
    }
}
_____________________________________________________________
pragma solidity 0.4.25;

contract ERC20Basic {
  function totalSupply() public view returns (uint256);
  function balanceOf(address who) public view returns (uint256);
  function transfer(address to, uint256 value) public returns (bool);
  event Transfer(address indexed from, address indexed to, uint256 value);
}

contract BasicToken is ERC20Basic {
  using SafeMath for uint256;

  mapping(address => uint256) balances;

  uint256 totalSupply_;

  /**
  * @dev Total number of tokens in existence
  */
  function totalSupply() public view returns (uint256) {
    return totalSupply_;
  }

  /**
  * @dev Transfer token for a specified address
  * @param _to The address to transfer to.
  * @param _value The amount to be transferred.
  */
  function transfer(address _to, uint256 _value) public returns (bool) {
    require(_value <= balances[msg.sender]);
    require(_to != address(0));

    balances[msg.sender] = balances[msg.sender].sub(_value);
    balances[_to] = balances[_to].add(_value);
    emit Transfer(msg.sender, _to, _value);
    return true;
  }

  /**
  * @dev Gets the balance of the specified address.
  * @param _owner The address to query the the balance of.
  * @return An uint256 representing the amount owned by the passed address.
  */
  function balanceOf(address _owner) public view returns (uint256) {
    return balances[_owner];
  }

}

contract ERC20 is ERC20Basic {
  function allowance(address owner, address spender)
    public view returns (uint256);

  function transferFrom(address from, address to, uint256 value)
    public returns (bool);

  function approve(address spender, uint256 value) public returns (bool);
  event Approval(
    address indexed owner,
    address indexed spender,
    uint256 value
  );
}

contract Ownable {
  address public owner;


  event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);


  /**
   * @dev The Ownable constructor sets the original `owner` of the contract to the sender
   * account.
   */
  constructor() public {
    owner = msg.sender;
  }


  /**
   * @dev Throws if called by any account other than the owner.
   */
  modifier onlyOwner() {
    require(msg.sender == owner);
    _;
  }


  /**
   * @dev Allows the current owner to transfer control of the contract to a newOwner.
   * @param newOwner The address to transfer ownership to.
   */
  function transferOwnership(address newOwner) public onlyOwner {
    require(newOwner != address(0));
    emit OwnershipTransferred(owner, newOwner);
    owner = newOwner;
  }

}

contract Claimable is Ownable {
  address public pendingOwner;

  /**
   * @dev Modifier throws if called by any account other than the pendingOwner.
   */
  modifier onlyPendingOwner() {
    require(msg.sender == pendingOwner);
    _;
  }

  /**
   * @dev Allows the current owner to set the pendingOwner address.
   * @param newOwner The address to transfer ownership to.
   */
  function transferOwnership(address newOwner) onlyOwner public {
    pendingOwner = newOwner;
  }

  /**
   * @dev Allows the pendingOwner address to finalize the transfer.
   */
  function claimOwnership() onlyPendingOwner public {
    emit OwnershipTransferred(owner, pendingOwner);
    owner = pendingOwner;
    pendingOwner = address(0);
  }
}

contract Pausable {
    address public requester;
    address public approver;

    bool public paused = true;
    bool public pausePending = false;
    bool public unpausePending = false;

    function requestPause() public onlyRequester {
        pausePending = true;
        unpausePending = false;
    }

    function requestUnpause() public onlyRequester {
        pausePending = false;
        unpausePending = true;
    }

    function cancelRequestPause() public onlyRequester {
        pausePending = false;
    }

    function approveRequestPause() public onlyApprover {
        require(pausePending);
        pausePending = false;
        paused = true;
    }

    function rejectRequestPause() public onlyApprover {
        pausePending = false;
    }

    function cancelRequestUnpause() public onlyRequester {
        unpausePending = false;
    }

    function approveRequestUnpause() public onlyApprover {
        require(unpausePending);
        unpausePending = false;
        paused = false;
    }

    function rejectRequestUnpause() public onlyApprover {
        unpausePending = false;
    }

    /**
     * @dev Throws if called by any account other than the owner.
     */
    modifier whenPaused() {
        require(paused);
        _;
    }

    modifier whenNotPaused() {
        require(!paused);
        _;
    }

    modifier onlyRequester() {
        require(msg.sender == requester);
        _;
    }

    modifier onlyApprover() {
        require(msg.sender == approver);
        _;
    }
}

library SafeMath {

  /**
  * @dev Multiplies two numbers, throws on overflow.
  */
  function mul(uint256 a, uint256 b) internal pure returns (uint256 c) {
    // Gas optimization: this is cheaper than asserting 'a' not being zero, but the
    // benefit is lost if 'b' is also tested.
    // See: https://github.com/OpenZeppelin/openzeppelin-solidity/pull/522
    if (a == 0) {
      return 0;
    }

    c = a * b;
    assert(c / a == b);
    return c;
  }

  /**
  * @dev Integer division of two numbers, truncating the quotient.
  */
  function div(uint256 a, uint256 b) internal pure returns (uint256) {
    // assert(b > 0); // Solidity automatically throws when dividing by 0
    // uint256 c = a / b;
    // assert(a == b * c + a % b); // There is no case in which this doesn't hold
    return a / b;
  }

  /**
  * @dev Subtracts two numbers, throws on overflow (i.e. if subtrahend is greater than minuend).
  */
  function sub(uint256 a, uint256 b) internal pure returns (uint256) {
    assert(b <= a);
    return a - b;
  }

  /**
  * @dev Adds two numbers, throws on overflow.
  */
  function add(uint256 a, uint256 b) internal pure returns (uint256 c) {
    c = a + b;
    assert(c >= a);
    return c;
  }
}

contract StandardToken is ERC20, BasicToken {

  mapping (address => mapping (address => uint256)) internal allowed;


  /**
   * @dev Transfer tokens from one address to another
   * @param _from address The address which you want to send tokens from
   * @param _to address The address which you want to transfer to
   * @param _value uint256 the amount of tokens to be transferred
   */
  function transferFrom(
    address _from,
    address _to,
    uint256 _value
  )
    public
    returns (bool)
  {
    require(_value <= balances[_from]);
    require(_value <= allowed[_from][msg.sender]);
    require(_to != address(0));

    balances[_from] = balances[_from].sub(_value);
    balances[_to] = balances[_to].add(_value);
    allowed[_from][msg.sender] = allowed[_from][msg.sender].sub(_value);
    emit Transfer(_from, _to, _value);
    return true;
  }

  /**
   * @dev Approve the passed address to spend the specified amount of tokens on behalf of msg.sender.
   * Beware that changing an allowance with this method brings the risk that someone may use both the old
   * and the new allowance by unfortunate transaction ordering. One possible solution to mitigate this
   * race condition is to first reduce the spender's allowance to 0 and set the desired value afterwards:
   * https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729
   * @param _spender The address which will spend the funds.
   * @param _value The amount of tokens to be spent.
   */
  function approve(address _spender, uint256 _value) public returns (bool) {
    allowed[msg.sender][_spender] = _value;
    emit Approval(msg.sender, _spender, _value);
    return true;
  }

  /**
   * @dev Function to check the amount of tokens that an owner allowed to a spender.
   * @param _owner address The address which owns the funds.
   * @param _spender address The address which will spend the funds.
   * @return A uint256 specifying the amount of tokens still available for the spender.
   */
  function allowance(
    address _owner,
    address _spender
   )
    public
    view
    returns (uint256)
  {
    return allowed[_owner][_spender];
  }

  /**
   * @dev Increase the amount of tokens that an owner allowed to a spender.
   * approve should be called when allowed[_spender] == 0. To increment
   * allowed value is better to use this function to avoid 2 calls (and wait until
   * the first transaction is mined)
   * From MonolithDAO Token.sol
   * @param _spender The address which will spend the funds.
   * @param _addedValue The amount of tokens to increase the allowance by.
   */
  function increaseAllowance(
    address _spender,
    uint256 _addedValue
  )
    public
    returns (bool)
  {
    allowed[msg.sender][_spender] = (
      allowed[msg.sender][_spender].add(_addedValue));
    emit Approval(msg.sender, _spender, allowed[msg.sender][_spender]);
    return true;
  }

  /**
   * @dev Decrease the amount of tokens that an owner allowed to a spender.
   * approve should be called when allowed[_spender] == 0. To decrement
   * allowed value is better to use this function to avoid 2 calls (and wait until
   * the first transaction is mined)
   * From MonolithDAO Token.sol
   * @param _spender The address which will spend the funds.
   * @param _subtractedValue The amount of tokens to decrease the allowance by.
   */
  function decreaseAllowance(
    address _spender,
    uint256 _subtractedValue
  )
    public
    returns (bool)
  {
    uint256 oldValue = allowed[msg.sender][_spender];
    if (_subtractedValue >= oldValue) {
      allowed[msg.sender][_spender] = 0;
    } else {
      allowed[msg.sender][_spender] = oldValue.sub(_subtractedValue);
    }
    emit Approval(msg.sender, _spender, allowed[msg.sender][_spender]);
    return true;
  }

}

contract StacsToken is StandardToken, Claimable, Pausable {
    using SafeMath for uint256;

    uint8 public constant decimals = 18;
    string public constant symbol = "STACS";
    string public constant name = "STACS";
    uint256 private constant MAX_TOKEN_SUPPLY = 900000000 * (10 ** uint256(decimals));
    bool public migrationPhase = true;
    address public migrationOperator;

    constructor(address _migrationOperator, address _requester, address _approver) public {
        owner = msg.sender;
        migrationOperator = _migrationOperator;
        requester = _requester;
        approver = _approver;
    }

    /**
    * @dev Mint specified number of tokens to respective address. Can only be called during migration phase
    * @param _accounts The target addresses to transfer to.
    * @param _amounts The amounts to be transferred.
    */
    function mint(address[] _accounts, uint256[] _amounts) public onlyMigrationOperator {
        require(migrationPhase);
        uint256 length = _accounts.length;
        require(length == _amounts.length);
        for (uint256 i = 0; i < length; i++) {
            balances[_accounts[i]] = balances[_accounts[i]].add(_amounts[i]);
            emit Transfer(address(0), _accounts[i], _amounts[i]);
            totalSupply_ = totalSupply_.add(_amounts[i]);
        }
        require(totalSupply_ <= MAX_TOKEN_SUPPLY);
    }

    /**
    * @dev End migration phase and disallow minting
    */
    function endMigration() public onlyOwner {
        migrationPhase = false;
    }

    /**
    * @dev Transfer any ERC20 token belonging to this contract to owner
    * @param tokenAddress The target ERC20 token address
    * @param tokens The amount of tokens to be transferred
    */
    function transferAnyERC20Token(address tokenAddress, uint256 tokens) public onlyOwner returns (bool success) {
        return ERC20Basic(tokenAddress).transfer(owner, tokens);
    }

    modifier onlyMigrationOperator() {
        require(msg.sender == migrationOperator);
        _;
    }

    // Overriden methods
    function transfer(address _to, uint256 _value) public whenNotPaused returns (bool success) {
        return super.transfer(_to, _value);
    }

    function transferFrom(address _from, address _to, uint256 _value) public whenNotPaused returns (bool) {
        return super.transferFrom(_from, _to, _value);
    }

    function approve(address spender, uint256 value) public whenNotPaused returns (bool) {
        return super.approve(spender, value);
    }

    function increaseAllowance(address spender, uint addedValue) public whenNotPaused returns (bool success) {
        return super.increaseAllowance(spender, addedValue);
    }

    function decreaseAllowance(address spender, uint subtractedValue) public whenNotPaused returns (bool success) {
        return super.decreaseAllowance(spender, subtractedValue);
    }
}
_____________________________________________________________
pragma solidity 0.4.25;

contract ERC20Basic {
  function totalSupply() public view returns (uint256);
  function balanceOf(address who) public view returns (uint256);
  function transfer(address to, uint256 value) public returns (bool);
  event Transfer(address indexed from, address indexed to, uint256 value);
}

contract BasicToken is ERC20Basic {
  using SafeMath for uint256;

  mapping(address => uint256) balances;

  uint256 totalSupply_;

  /**
  * @dev Total number of tokens in existence
  */
  function totalSupply() public view returns (uint256) {
    return totalSupply_;
  }

  /**
  * @dev Transfer token for a specified address
  * @param _to The address to transfer to.
  * @param _value The amount to be transferred.
  */
  function transfer(address _to, uint256 _value) public returns (bool) {
    require(_value <= balances[msg.sender]);
    require(_to != address(0));

    balances[msg.sender] = balances[msg.sender].sub(_value);
    balances[_to] = balances[_to].add(_value);
    emit Transfer(msg.sender, _to, _value);
    return true;
  }

  /**
  * @dev Gets the balance of the specified address.
  * @param _owner The address to query the the balance of.
  * @return An uint256 representing the amount owned by the passed address.
  */
  function balanceOf(address _owner) public view returns (uint256) {
    return balances[_owner];
  }

}

contract ERC20 is ERC20Basic {
  function allowance(address owner, address spender)
    public view returns (uint256);

  function transferFrom(address from, address to, uint256 value)
    public returns (bool);

  function approve(address spender, uint256 value) public returns (bool);
  event Approval(
    address indexed owner,
    address indexed spender,
    uint256 value
  );
}

contract Ownable {
  address public owner;


  event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);


  /**
   * @dev The Ownable constructor sets the original `owner` of the contract to the sender
   * account.
   */
  constructor() public {
    owner = msg.sender;
  }


  /**
   * @dev Throws if called by any account other than the owner.
   */
  modifier onlyOwner() {
    require(msg.sender == owner);
    _;
  }


  /**
   * @dev Allows the current owner to transfer control of the contract to a newOwner.
   * @param newOwner The address to transfer ownership to.
   */
  function transferOwnership(address newOwner) public onlyOwner {
    require(newOwner != address(0));
    emit OwnershipTransferred(owner, newOwner);
    owner = newOwner;
  }

}

contract Claimable is Ownable {
  address public pendingOwner;

  /**
   * @dev Modifier throws if called by any account other than the pendingOwner.
   */
  modifier onlyPendingOwner() {
    require(msg.sender == pendingOwner);
    _;
  }

  /**
   * @dev Allows the current owner to set the pendingOwner address.
   * @param newOwner The address to transfer ownership to.
   */
  function transferOwnership(address newOwner) onlyOwner public {
    pendingOwner = newOwner;
  }

  /**
   * @dev Allows the pendingOwner address to finalize the transfer.
   */
  function claimOwnership() onlyPendingOwner public {
    emit OwnershipTransferred(owner, pendingOwner);
    owner = pendingOwner;
    pendingOwner = address(0);
  }
}

contract Pausable {
    address public requester;
    address public approver;

    bool public paused = true;
    bool public pausePending = false;
    bool public unpausePending = false;

    function requestPause() public onlyRequester {
        pausePending = true;
        unpausePending = false;
    }

    function requestUnpause() public onlyRequester {
        pausePending = false;
        unpausePending = true;
    }

    function cancelRequestPause() public onlyRequester {
        pausePending = false;
    }

    function approveRequestPause() public onlyApprover {
        require(pausePending);
        pausePending = false;
        paused = true;
    }

    function rejectRequestPause() public onlyApprover {
        pausePending = false;
    }

    function cancelRequestUnpause() public onlyRequester {
        unpausePending = false;
    }

    function approveRequestUnpause() public onlyApprover {
        require(unpausePending);
        unpausePending = false;
        paused = false;
    }

    function rejectRequestUnpause() public onlyApprover {
        unpausePending = false;
    }

    /**
     * @dev Throws if called by any account other than the owner.
     */
    modifier whenPaused() {
        require(paused);
        _;
    }

    modifier whenNotPaused() {
        require(!paused);
        _;
    }

    modifier onlyRequester() {
        require(msg.sender == requester);
        _;
    }

    modifier onlyApprover() {
        require(msg.sender == approver);
        _;
    }
}

library SafeMath {

  /**
  * @dev Multiplies two numbers, throws on overflow.
  */
  function mul(uint256 a, uint256 b) internal pure returns (uint256 c) {
    // Gas optimization: this is cheaper than asserting 'a' not being zero, but the
    // benefit is lost if 'b' is also tested.
    // See: https://github.com/OpenZeppelin/openzeppelin-solidity/pull/522
    if (a == 0) {
      return 0;
    }

    c = a * b;
    assert(c / a == b);
    return c;
  }

  /**
  * @dev Integer division of two numbers, truncating the quotient.
  */
  function div(uint256 a, uint256 b) internal pure returns (uint256) {
    // assert(b > 0); // Solidity automatically throws when dividing by 0
    // uint256 c = a / b;
    // assert(a == b * c + a % b); // There is no case in which this doesn't hold
    return a / b;
  }

  /**
  * @dev Subtracts two numbers, throws on overflow (i.e. if subtrahend is greater than minuend).
  */
  function sub(uint256 a, uint256 b) internal pure returns (uint256) {
    assert(b <= a);
    return a - b;
  }

  /**
  * @dev Adds two numbers, throws on overflow.
  */
  function add(uint256 a, uint256 b) internal pure returns (uint256 c) {
    c = a + b;
    assert(c >= a);
    return c;
  }
}

contract StandardToken is ERC20, BasicToken {

  mapping (address => mapping (address => uint256)) internal allowed;


  /**
   * @dev Transfer tokens from one address to another
   * @param _from address The address which you want to send tokens from
   * @param _to address The address which you want to transfer to
   * @param _value uint256 the amount of tokens to be transferred
   */
  function transferFrom(
    address _from,
    address _to,
    uint256 _value
  )
    public
    returns (bool)
  {
    require(_value <= balances[_from]);
    require(_value <= allowed[_from][msg.sender]);
    require(_to != address(0));

    balances[_from] = balances[_from].sub(_value);
    balances[_to] = balances[_to].add(_value);
    allowed[_from][msg.sender] = allowed[_from][msg.sender].sub(_value);
    emit Transfer(_from, _to, _value);
    return true;
  }

  /**
   * @dev Approve the passed address to spend the specified amount of tokens on behalf of msg.sender.
   * Beware that changing an allowance with this method brings the risk that someone may use both the old
   * and the new allowance by unfortunate transaction ordering. One possible solution to mitigate this
   * race condition is to first reduce the spender's allowance to 0 and set the desired value afterwards:
   * https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729
   * @param _spender The address which will spend the funds.
   * @param _value The amount of tokens to be spent.
   */
  function approve(address _spender, uint256 _value) public returns (bool) {
    allowed[msg.sender][_spender] = _value;
    emit Approval(msg.sender, _spender, _value);
    return true;
  }

  /**
   * @dev Function to check the amount of tokens that an owner allowed to a spender.
   * @param _owner address The address which owns the funds.
   * @param _spender address The address which will spend the funds.
   * @return A uint256 specifying the amount of tokens still available for the spender.
   */
  function allowance(
    address _owner,
    address _spender
   )
    public
    view
    returns (uint256)
  {
    return allowed[_owner][_spender];
  }

  /**
   * @dev Increase the amount of tokens that an owner allowed to a spender.
   * approve should be called when allowed[_spender] == 0. To increment
   * allowed value is better to use this function to avoid 2 calls (and wait until
   * the first transaction is mined)
   * From MonolithDAO Token.sol
   * @param _spender The address which will spend the funds.
   * @param _addedValue The amount of tokens to increase the allowance by.
   */
  function increaseAllowance(
    address _spender,
    uint256 _addedValue
  )
    public
    returns (bool)
  {
    allowed[msg.sender][_spender] = (
      allowed[msg.sender][_spender].add(_addedValue));
    emit Approval(msg.sender, _spender, allowed[msg.sender][_spender]);
    return true;
  }

  /**
   * @dev Decrease the amount of tokens that an owner allowed to a spender.
   * approve should be called when allowed[_spender] == 0. To decrement
   * allowed value is better to use this function to avoid 2 calls (and wait until
   * the first transaction is mined)
   * From MonolithDAO Token.sol
   * @param _spender The address which will spend the funds.
   * @param _subtractedValue The amount of tokens to decrease the allowance by.
   */
  function decreaseAllowance(
    address _spender,
    uint256 _subtractedValue
  )
    public
    returns (bool)
  {
    uint256 oldValue = allowed[msg.sender][_spender];
    if (_subtractedValue >= oldValue) {
      allowed[msg.sender][_spender] = 0;
    } else {
      allowed[msg.sender][_spender] = oldValue.sub(_subtractedValue);
    }
    emit Approval(msg.sender, _spender, allowed[msg.sender][_spender]);
    return true;
  }

}

contract StacsToken is StandardToken, Claimable, Pausable {
    using SafeMath for uint256;

    uint8 public constant decimals = 18;
    string public constant symbol = "STACS";
    string public constant name = "STACS";
    uint256 private constant MAX_TOKEN_SUPPLY = 900000000 * (10 ** uint256(decimals));
    bool public migrationPhase = true;
    address public migrationOperator;

    constructor(address _migrationOperator, address _requester, address _approver) public {
        owner = msg.sender;
        migrationOperator = _migrationOperator;
        requester = _requester;
        approver = _approver;
    }

    /**
    * @dev Mint specified number of tokens to respective address. Can only be called during migration phase
    * @param _accounts The target addresses to transfer to.
    * @param _amounts The amounts to be transferred.
    */
    function mint(address[] _accounts, uint256[] _amounts) public onlyMigrationOperator {
        require(migrationPhase);
        uint256 length = _accounts.length;
        require(length == _amounts.length);
        for (uint256 i = 0; i < length; i++) {
            balances[_accounts[i]] = balances[_accounts[i]].add(_amounts[i]);
            emit Transfer(address(0), _accounts[i], _amounts[i]);
            totalSupply_ = totalSupply_.add(_amounts[i]);
        }
        require(totalSupply_ <= MAX_TOKEN_SUPPLY);
    }

    /**
    * @dev End migration phase and disallow minting
    */
    function endMigration() public onlyOwner {
        migrationPhase = false;
    }

    /**
    * @dev Transfer any ERC20 token belonging to this contract to owner
    * @param tokenAddress The target ERC20 token address
    * @param tokens The amount of tokens to be transferred
    */
    function transferAnyERC20Token(address tokenAddress, uint256 tokens) public onlyOwner returns (bool success) {
        return ERC20Basic(tokenAddress).transfer(owner, tokens);
    }

    modifier onlyMigrationOperator() {
        require(msg.sender == migrationOperator);
        _;
    }

    // Overriden methods
    function transfer(address _to, uint256 _value) public whenNotPaused returns (bool success) {
        return super.transfer(_to, _value);
    }

    function transferFrom(address _from, address _to, uint256 _value) public whenNotPaused returns (bool) {
        return super.transferFrom(_from, _to, _value);
    }

    function approve(address spender, uint256 value) public whenNotPaused returns (bool) {
        return super.approve(spender, value);
    }

    function increaseAllowance(address spender, uint addedValue) public whenNotPaused returns (bool success) {
        return super.increaseAllowance(spender, addedValue);
    }

    function decreaseAllowance(address spender, uint subtractedValue) public whenNotPaused returns (bool success) {
        return super.decreaseAllowance(spender, subtractedValue);
    }
}
_____________________________________________________________
