pragma solidity >=0.6.0 <0.8.0;

/**
 * @dev Contract module which provides a basic access control mechanism, where
 * there is an account (an owner) that can be granted exclusive access to
 * specific functions.
 *
 * By default, the owner account will be the one that deploys the contract. This
 * can later be changed with {transferOwnership}.
 *
 * This module is used through inheritance. It will make available the modifier
 * `onlyOwner`, which can be applied to your functions to restrict their use to
 * the owner.
 */
abstract contract Ownable is Context {
    address private _owner;

    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    /**
     * @dev Initializes the contract setting the deployer as the initial owner.
     */
    constructor () internal {
        address msgSender = _msgSender();
        _owner = msgSender;
        emit OwnershipTransferred(address(0), msgSender);
    }

    /**
     * @dev Returns the address of the current owner.
     */
    function owner() public view virtual returns (address) {
        return _owner;
    }

    /**
     * @dev Throws if called by any account other than the owner.
     */
    modifier onlyOwner() {
        require(owner() == _msgSender(), "Ownable: caller is not the owner");
        _;
    }

    /**
     * @dev Leaves the contract without owner. It will not be possible to call
     * `onlyOwner` functions anymore. Can only be called by the current owner.
     *
     * NOTE: Renouncing ownership will leave the contract without an owner,
     * thereby removing any functionality that is only available to the owner.
     */
    function renounceOwnership() public virtual onlyOwner {
        emit OwnershipTransferred(_owner, address(0));
        _owner = address(0);
    }

    /**
     * @dev Transfers ownership of the contract to a new account (`newOwner`).
     * Can only be called by the current owner.
     */
    function transferOwnership(address newOwner) public virtual onlyOwner {
        require(newOwner != address(0), "Ownable: new owner is the zero address");
        emit OwnershipTransferred(_owner, newOwner);
        _owner = newOwner;
    }
}



// MUSHY BARAS CONTRACT

pragma solidity ^0.7.0;
pragma abicoder v2;

contract MushyBaras is ERC721, Ownable {

    using SafeMath for uint256;

    string public MUSHYBARA_PROVENANCE = ""; // IPFS URL WILL BE ADDED WHEN MUSHYBARAS ARE ALL SOLD OUT

    string public LICENSE_TEXT = ""; // IT IS WHAT IT SAYS

    bool licenseLocked = false; // TEAM CAN'T EDIT THE LICENSE AFTER THIS GETS TRUE

    uint256 public constant mushybaraPrice = 40000000000000000; // 0.04 ETH

    uint public constant maxMushybaraPurchase = 20;

    uint256 public constant MAX_MUSHYBARAS = 9999;

    bool public saleIsActive = false;

    mapping(uint => string) public mushybaraNames;

    // Reserve for giveaways and marketing
    uint public mushybaraReserve = 9900;

    event mushybaraNameChange(address _by, uint _tokenId, string _name);

    event licenseisLocked(string _licenseText);

    constructor() ERC721("MushyBaras", "BARA") { }

    function withdraw() public onlyOwner {
        uint balance = address(this).balance;
        msg.sender.transfer(balance);
    }

    function reserveMushybaras(address _to, uint256 _reserveAmount) public onlyOwner {
        uint supply = totalSupply();
        require(_reserveAmount > 0 && _reserveAmount <= mushybaraReserve, "Not enough reserve left for team");
        for (uint i = 0; i < _reserveAmount; i++) {
            _safeMint(_to, supply + i);
        }
        mushybaraReserve = mushybaraReserve.sub(_reserveAmount);
    }


    function setProvenanceHash(string memory provenanceHash) public onlyOwner {
        MUSHYBARA_PROVENANCE = provenanceHash;
    }

    function setBaseURI(string memory baseURI) public onlyOwner {
        _setBaseURI(baseURI);
    }


    function flipSaleState() public onlyOwner {
        saleIsActive = !saleIsActive;
    }


    function tokensOfOwner(address _owner) external view returns(uint256[] memory ) {
        uint256 tokenCount = balanceOf(_owner);
        if (tokenCount == 0) {
            // Return an empty array
            return new uint256[](0);
        } else {
            uint256[] memory result = new uint256[](tokenCount);
            uint256 index;
            for (index = 0; index < tokenCount; index++) {
                result[index] = tokenOfOwnerByIndex(_owner, index);
            }
            return result;
        }
    }

    // Returns the license for tokens
    function tokenLicense(uint _id) public view returns(string memory) {
        require(_id < totalSupply(), "CHOOSE A MUSHYBARA WITHIN RANGE");
        return LICENSE_TEXT;
    }

    // Locks the license to prevent further changes
    function lockLicense() public onlyOwner {
        require(licenseLocked == false, "License already locked");
        licenseLocked = true;
        emit licenseisLocked(LICENSE_TEXT);
    }

    // Change the license
    function changeLicense(string memory _license) public onlyOwner {
        require(licenseLocked == false, "License already locked");
        LICENSE_TEXT = _license;
    }


    function mintMushybara(uint numberOfTokens) public payable {
        require(saleIsActive, "Sale must be active to mint a Mushybara");
        require(numberOfTokens > 0 && numberOfTokens <= maxMushybaraPurchase, "Can only mint 20 tokens at a time");
        require(totalSupply().add(numberOfTokens) <= MAX_MUSHYBARAS, "Purchase would exceed max supply of Mushybaras");
        require(msg.value >= mushybaraPrice.mul(numberOfTokens), "Ether value sent is not correct");

        for(uint i = 0; i < numberOfTokens; i++) {
            uint mintIndex = totalSupply();
            if (totalSupply() < MAX_MUSHYBARAS) {
                _safeMint(msg.sender, mintIndex);
            }
        }

    }

    function changeMushybaraName(uint _tokenId, string memory _name) public {
        require(ownerOf(_tokenId) == msg.sender, "Hey, your wallet doesn't own this mushybara!");
        require(sha256(bytes(_name)) != sha256(bytes(mushybaraNames[_tokenId])), "New name is same as the current one");
        mushybaraNames[_tokenId] = _name;

        emit mushybaraNameChange(msg.sender, _tokenId, _name);

    }

    function viewMushybaraName(uint _tokenId) public view returns( string memory ){
        require( _tokenId < totalSupply(), "Choose a mushybara within range" );
        return mushybaraNames[_tokenId];
    }


    // GET ALL MUSHYBARAS OF A WALLET AS AN ARRAY OF STRINGS. WOULD BE BETTER MAYBE IF IT RETURNED A STRUCT WITH ID-NAME MATCH
    function mushybaraNamesOfOwner(address _owner) external view returns(string[] memory ) {
        uint256 tokenCount = balanceOf(_owner);
        if (tokenCount == 0) {
            // Return an empty array
            return new string[](0);
        } else {
            string[] memory result = new string[](tokenCount);
            uint256 index;
            for (index = 0; index < tokenCount; index++) {
                result[index] = mushybaraNames[ tokenOfOwnerByIndex(_owner, index) ] ;
            }
            return result;
        }
    }

}