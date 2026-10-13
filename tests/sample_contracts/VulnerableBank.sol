// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VulnerableBank {
    mapping(address => uint256) public balances;
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    // VULN-001: Classic Reentrancy vulnerability (External call before state change)
    function withdraw() public {
        uint256 balance = balances[msg.sender];
        require(balance > 0, "No balance");
        
        (bool success, ) = msg.sender.call{value: balance}("");
        require(success, "Transfer failed");

        balances[msg.sender] = 0; // State update after external call!
    }

    // VULN-002: Dangerous use of tx.origin
    function emergencyDrain(address recipient) public {
        require(tx.origin == owner, "Only owner authorized");
        payable(recipient).transfer(address(this).balance);
    }

    // VULN-005: Missing zero-address validation
    function setOwner(address newOwner) public {
        require(msg.sender == owner, "Not owner");
        owner = newOwner;
    }
}
