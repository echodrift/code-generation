    function SCT() {
        balanceOf[msg.sender] = initialSupply;              // Give the creator all initial tokens
        totalSupply = initialSupply;                        // Update total supply
        name = tokenName;                                   // Set the name for display purposes
        symbol = tokenSymbol;                               // Set the symbol for display purposes
        decimals = decimalUnits;                            // Amount of decimals for display purposes
        owner = msg.sender;
    }
---------------------------------------------------
function transfer(address _to, uint256 _value) {
      require (_value > 0) ;
        require (balanceOf[msg.sender] >= _value);           // Check if the sender has enough
        require (balanceOf[_to] + _value >= balanceOf[_to]) ;     // Check for overflows
        require (!restrictedAddresses[_to]);
        balanceOf[msg.sender] = SafeMath.safeSub(balanceOf[msg.sender], _value);                     // Subtract from the sender
        balanceOf[_to] = SafeMath.safeAdd(balanceOf[_to], _value);                            // Add the same to the recipient
        Transfer(msg.sender, _to, _value);                   // Notify anyone listening that this transfer took place
    }
---------------------------------------------------
function approve(address _spender, uint256 _value)
        returns (bool success) {
          allowance[msg.sender][_spender] = _value;          // Set allowance
        Approval(msg.sender, _spender, _value);             // Raise Approval event
        return true;
    }
---------------------------------------------------
function transferFrom(address _from, address _to, uint256 _value) returns (bool success) {
        require (balanceOf[_from] >= _value);                 // Check if the sender has enough
        require (balanceOf[_to] + _value >= balanceOf[_to]) ;  // Check for overflows
        require (_value <= allowance[_from][msg.sender]) ;     // Check allowance
        require (!restrictedAddresses[_to]);
        balanceOf[_from] = SafeMath.safeSub(balanceOf[_from], _value);                           // Subtract from the sender
        balanceOf[_to] = SafeMath.safeAdd(balanceOf[_to], _value);                             // Add the same to the recipient
        allowance[_from][msg.sender] = SafeMath.safeSub(allowance[_from][msg.sender], _value);
        Transfer(_from, _to, _value);
        return true;
    }
---------------------------------------------------
function execute(
    bytes calldata data,
    address executor,
    uint256 gasLimit,
    bytes32 salt,
    bytes calldata signatures
  ) external returns (bool success, bytes memory returnData) {
    require(
      executor == msg.sender || executor == address(0),
      "Must call from the executor account if one is specified."
    );

    // Derive the message hash and ensure that it has not been used before.
    (bytes32 rawHash, bool usable) = _getHash(data, executor, gasLimit, salt);
    require(usable, "Hash in question has already been used previously.");

    // wrap the derived message hash as an eth signed messsage hash.
    bytes32 hash = _toEthSignedMessageHash(rawHash);

    // Recover each signer from provided signatures and ensure threshold is met.
    address[] memory signers = _recoverGroup(hash, signatures);

    require(signers.length == _THRESHOLD, "Total signers must equal threshold.");

    // Verify that each signatory is an owner and is strictly increasing.
    address lastAddress = address(0); // cannot have address(0) as an owner
    for (uint256 i = 0; i < signers.length; i++) {
      require(
        _isOwner[signers[i]], "Signature does not correspond to an owner."
      );
      require(
        signers[i] > lastAddress, "Signer addresses must be strictly increasing."
      );
      lastAddress = signers[i];
    }

    // Add the hash to the mapping of used hashes and execute the transaction.
    _usedHashes[rawHash] = true;
    (success, returnData) = _DESTINATION.call{gas:gasLimit}(data);
  }
---------------------------------------------------
function SCT() {
        balanceOf[msg.sender] = initialSupply;              
        totalSupply = initialSupply;                        
        name = tokenName;                                   
        symbol = tokenSymbol;                               
        decimals = decimalUnits;                            
        owner = msg.sender;
    }
-------------------------------------
function transfer(address _to, uint256 _value) {
      require (_value > 0) ;
        require (balanceOf[msg.sender] >= _value);           
        require (balanceOf[_to] + _value >= balanceOf[_to]) ;     
        require (!restrictedAddresses[_to]);
        balanceOf[msg.sender] = SafeMath.safeSub(balanceOf[msg.sender], _value);                     
        balanceOf[_to] = SafeMath.safeAdd(balanceOf[_to], _value);                            
        Transfer(msg.sender, _to, _value);                   
    }
-------------------------------------
function approve(address _spender, uint256 _value)
        returns (bool success) {
          allowance[msg.sender][_spender] = _value;          
        Approval(msg.sender, _spender, _value);             
        return true;
    }
-------------------------------------
function transferFrom(address _from, address _to, uint256 _value) returns (bool success) {
        require (balanceOf[_from] >= _value);                 
        require (balanceOf[_to] + _value >= balanceOf[_to]) ;  
        require (_value <= allowance[_from][msg.sender]) ;     
        require (!restrictedAddresses[_to]);
        balanceOf[_from] = SafeMath.safeSub(balanceOf[_from], _value);                           
        balanceOf[_to] = SafeMath.safeAdd(balanceOf[_to], _value);                             
        allowance[_from][msg.sender] = SafeMath.safeSub(allowance[_from][msg.sender], _value);
        Transfer(_from, _to, _value);
        return true;
    }
-------------------------------------
function execute(
    bytes calldata data,
    address executor,
    uint256 gasLimit,
    bytes32 salt,
    bytes calldata signatures
  ) external returns (bool success, bytes memory returnData) {
    require(
      executor == msg.sender || executor == address(0),
      "Must call from the executor account if one is specified."
    );

    
    (bytes32 rawHash, bool usable) = _getHash(data, executor, gasLimit, salt);
    require(usable, "Hash in question has already been used previously.");

    
    bytes32 hash = _toEthSignedMessageHash(rawHash);

    
    address[] memory signers = _recoverGroup(hash, signatures);

    require(signers.length == _THRESHOLD, "Total signers must equal threshold.");

    
    address lastAddress = address(0); 
    for (uint256 i = 0; i < signers.length; i++) {
      require(
        _isOwner[signers[i]], "Signature does not correspond to an owner."
      );
      require(
        signers[i] > lastAddress, "Signer addresses must be strictly increasing."
      );
      lastAddress = signers[i];
    }

    
    _usedHashes[rawHash] = true;
    (success, returnData) = _DESTINATION.call{gas:gasLimit}(data);
  }
-------------------------------------
