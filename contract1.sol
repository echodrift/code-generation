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
    // Hash: seth keccak -- ""$(wget https://<executive-vote-canonical-post> -q -O - 2>/dev/null)""
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
        pause       = PauseAbstract(log.getAddress(""MCD_PAUSE""));
        description = _description;
        expiration  = _expiration;
        action      = _spellAction;

        sig = abi.encodeWithSignature(""execute()"");
        bytes32 _tag;                    // Required for assembly access
        address _action = _spellAction;  // Required for assembly access
        assembly { _tag := extcodehash(_action) }
        tag = _tag;
    }

    function schedule() public {
        require(now <= expiration, ""This contract has expired"");
        require(eta == 0, ""This spell has already been scheduled"");
        eta = now + PauseAbstract(pause).delay();
        pause.plot(action, tag, sig, eta);
    }

    function cast() public {
        require(!done, ""spell-already-cast"");
        done = true;
        pause.exec(action, tag, sig, eta);
    }
}