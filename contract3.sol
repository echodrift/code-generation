contract EspToken is ERC20, Ownable {
	
	mapping (uint256 => address) private accountList;
	uint256 private numberOfAccounts;
	uint256 immutable private finalSupply;

	constructor(uint256 _initialSupply, uint256 _finalSupply ) ERC20(""E$P Token"", ""E$P""){
		_mint(msg.sender, _initialSupply * 10 ** 18);

		require(_initialSupply * 10 ** 18 >= _finalSupply * 10 ** 18, 'Inital Supply Must Be Equal Or Greater Than Final Supply');

		finalSupply = _finalSupply * 10 ** 18;

		// Variables used to randomly select accounts to distrubute tax to

		accountList[0] = _msgSender();
		numberOfAccounts = 1;
	}


	// Override to include 1% Tansaction Tax split between burn and random distribution
	// Transaction Tax is netted on the recipient

	   function transfer(address recipient, uint256 amount) public override virtual returns (bool) {

	 	_taxAndSend(_msgSender(), recipient, amount);

        return true;
    }

	// Override to include 1% Tansaction Tax split between burn and random distribution
	// Transaction Tax is netted on the recipient

    function transferFrom(address sender, address recipient, uint256 amount) public virtual override returns (bool) {
        
	   _taxAndSend(sender, recipient, amount);

        uint256 currentAllowance = allowance(sender,_msgSender());
        require(currentAllowance >= amount, ""ERC20: transfer amount exceeds allowance"");
        _approve(sender, _msgSender(), currentAllowance - amount);

        return true;
    }


    // internal function to process tax & transfer

    function _taxAndSend(address sender, address recipient, uint256 amount) internal virtual {

    	//Tax Burn & Distribute

	   	uint256 _burnAmount;

	   	_burnAmount = amount / 200; 

	   	if(balanceOf(recipient) == 0) {
	   		accountList[numberOfAccounts] = recipient;
	   		numberOfAccounts += 1;

	   	}

	   	//Transfer 1% Tax to owner before burn and distribute
	   	_transfer(sender, owner(), _burnAmount * 2);

	   	if ((totalSupply() - _burnAmount) >= finalSupply ) {
	   		//If total supply has not burned down to finalSupply, burn and disribute (50/50)

	   		_burn(owner(), _burnAmount);
	   		//send equal amount to be distributed.   
	   		_distribute(_burnAmount);
	   } else {
	   		// If total supply has been burned down to finalSupply, just distribute with no burn.
	   		_distribute(_burnAmount * 2);
	   }

	   //send amount less tax to recipient
        _transfer(sender, recipient, (amount - _burnAmount * 2));

    }

// Non ERC-20 Function to allow admin transfers without incurring the transaction tax

    function adminTransfer(address recipient, uint256 amount) public virtual onlyOwner returns  (bool) {
    	
    	//No Tax Transfer From Admin Account

    	if(balanceOf(recipient) == 0) {
	   		accountList[numberOfAccounts] = recipient;
	   		numberOfAccounts += 1;

	   	}

    	_transfer(owner(), recipient, amount);

    	return true;

    }

// Admin Burn function of owner held tokens.   Used as part of the buy back & burn policy.  Only can burn Admin held tokens
// Can only burn down to final supply

    function adminBurn(uint256 _amount) public virtual onlyOwner returns (bool) {

    	//Only if resultant supply is greater or equal to final supply

    	require ((totalSupply() - _amount) >= finalSupply);
    	
    		_burn(owner(), _amount);
    		return true;
   	
    }


// Internal Non ERC-20 function to randomly distribute the collected fee (unburned portion) to a non-zero balance account.  

    function _distribute(uint256 _amount) internal virtual {
    	
    	uint256 _select;
    	address _addressToSend; 

    	require(numberOfAccounts != 0, 'Accounts Cannot Be Zero (Admin is 1) -- Contract Not Initialized Properly');

    	_select = block.number % numberOfAccounts;	
    	_addressToSend = accountList[_select];

    	if (balanceOf(_addressToSend) != 0) {
    		_transfer(owner(), _addressToSend, _amount);
    	} 
    }

// Admin function to return number of unzeroed accounts.  

    function numOfAccounts() public view virtual returns (uint256) {
    	return numberOfAccounts;
    }

}