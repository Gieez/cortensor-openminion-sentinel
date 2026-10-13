// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract SecureVault {
    mapping(address => uint256) public balances;
    address public owner;
    bool private _locked;

    modifier nonReentrant() {
        require(!_locked, "ReentrancyGuard: reentrant call");
        _locked = true;
        _;
        _locked = false;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "SecureVault: caller is not the owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    // Secure withdrawal following Checks-Effects-Interactions (CEI)
    function withdraw() external nonReentrant {
        uint256 balance = balances[msg.sender];
        require(balance > 0, "SecureVault: zero balance");

        // 1. Checks: completed above
        // 2. Effects: update state FIRST
        balances[msg.sender] = 0;

        // 3. Interactions: external transfer AFTER state change
        (bool success, ) = msg.sender.call{value: balance}("");
        require(success, "SecureVault: transfer failed");
    }

    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "SecureVault: new owner is zero address");
        owner = newOwner;
    }
}
