// SPDX-License-Identifier: MIT
pragma solidity ^0.8.22;

import "hardhat/console.sol"; // <--- ADD THIS LINE

abstract contract Context {
    function _msgSender() internal view virtual returns (address) {
        return msg.sender;
    }

    function _msgData() internal view virtual returns (bytes calldata) {
        return msg.data;
    }

    function _contextSuffixLength() internal view virtual returns (uint256) {
        return 0;
    }
}

abstract contract Ownable is Context {
    address private _owner;
    error OwnableUnauthorizedAccount(address account);
    error OwnableInvalidOwner(address owner);

    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    constructor(address initialOwner) {
        if (initialOwner == address(0)) {
            revert OwnableInvalidOwner(address(0));
        }
        _transferOwnership(initialOwner);
    }

    modifier onlyOwner() {
        _checkOwner();
        _;
    }

    function owner() public view virtual returns (address) {
        return _owner;
    }

    function _checkOwner() internal view virtual {
        if (owner() != _msgSender()) {
            revert OwnableUnauthorizedAccount(_msgSender());
        }
    }

    function renounceOwnership() public virtual onlyOwner {
        _transferOwnership(address(0));
    }

    function transferOwnership(address newOwner) public virtual onlyOwner {
        if (newOwner == address(0)) {
            revert OwnableInvalidOwner(address(0));
        }
        _transferOwnership(newOwner);
    }

    function _transferOwnership(address newOwner) internal virtual {
        address oldOwner = _owner;
        _owner = newOwner;
        emit OwnershipTransferred(oldOwner, newOwner);
    }
}

contract Grader5 is Ownable{

    mapping (address => uint256) public counter;
    mapping(string => uint256) public students;
    mapping(address => bool) public isGraded;
    uint256 public studentCounter;
    uint256 public divisor = 8;
    uint256 public deadline = 10000000000000000000000;
    uint256 public startTime = 0;

    constructor() Ownable(msg.sender) payable {}

    function retrieve() external payable {
        console.log("--------------------");
        console.log("retrieve() called");
        console.log("msg.sender:", msg.sender);
        console.log("msg.value:", msg.value);
        console.log("counter before increment:", counter[msg.sender]);
        require(msg.value > 3, "not enough money");
        counter[msg.sender]++;
        console.log("counter after increment:", counter[msg.sender]);
        require(counter[msg.sender] < 4, "counter >= 4, revert");

        (bool sent, ) = payable(msg.sender).call{value: 1, gas: gasleft()}("");
        console.log("sent after call:", sent);

        require(sent, "Failed to send Ether");

        if(counter[msg.sender] < 2) {
            console.log("Counter < 2, resetting counter[msg.sender] to 0");
            counter[msg.sender] = 0;
        } else {
            console.log("Counter >= 2, not resetting");
        }
        console.log("counter at end of function:", counter[msg.sender]);
        console.log("--------------------");
    }  

    function gradeMe(string calldata name) public {
        require(block.timestamp < deadline, "The end");
        require(block.timestamp > startTime, "The end");
        require(counter[msg.sender] > 1, "Not yet");
        uint256 _grade = studentCounter / divisor;
        ++studentCounter;

        if (_grade <= 6) {
            _grade = 100 - _grade * 5;
        } else {
            _grade = 70;
        }
  
        require(students[name] == 0, "student already exists");
        require(isGraded[msg.sender] == false, "already graded");
        isGraded[msg.sender] = true;
        students[name] = _grade;
    }

    function setDivisor(uint256 _divisor) public onlyOwner {
        divisor = _divisor;
    }

    function setDeadline(uint256 _deadline) public onlyOwner {
        deadline = _deadline;
    }

    function setStudentCounter(uint256 _studentCounter) public onlyOwner {
        studentCounter = _studentCounter;
    }

    function setStartTime(uint256 _startTime) public onlyOwner {
        startTime = _startTime;
    }

    function withdraw() public onlyOwner {
        payable(msg.sender).transfer(address(this).balance);
    }
}
