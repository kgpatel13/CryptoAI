// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

interface IERC20 {
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
}

contract CryptoAIAtomicArbitrageExecutor {
    struct Route {
        address tokenIn;
        address tokenMid;
        address tokenOut;
        uint256 amountIn;
        uint256 minAmountOut;
        uint256 minProfit;
        address buyRouter;
        address sellRouter;
        bytes buyCalldata;
        bytes sellCalldata;
        address recipient;
        uint256 deadline;
    }

    address public owner;
    bool private locked;
    mapping(address => bool) public allowedRouters;
    mapping(address => bool) public allowedTokens;

    event RouterAllowed(address indexed router, bool allowed);
    event TokenAllowed(address indexed token, bool allowed);
    event AtomicArbitrageExecuted(
        address indexed caller,
        address indexed tokenOut,
        uint256 amountIn,
        uint256 amountOut,
        uint256 profit
    );

    error NotOwner();
    error Reentered();
    error Expired();
    error ZeroAddress();
    error RouterNotAllowed(address router);
    error TokenNotAllowed(address token);
    error TransferFailed();
    error SwapFailed(bytes data);
    error ProfitTooLow(uint256 amountOut, uint256 minAmountOut);

    constructor(address[] memory routers, address[] memory tokens) {
        owner = msg.sender;
        for (uint256 i = 0; i < routers.length; i++) {
            allowedRouters[routers[i]] = true;
            emit RouterAllowed(routers[i], true);
        }
        for (uint256 i = 0; i < tokens.length; i++) {
            allowedTokens[tokens[i]] = true;
            emit TokenAllowed(tokens[i], true);
        }
    }

    modifier onlyOwner() {
        if (msg.sender != owner) revert NotOwner();
        _;
    }

    modifier nonReentrant() {
        if (locked) revert Reentered();
        locked = true;
        _;
        locked = false;
    }

    function setRouterAllowed(address router, bool allowed) external onlyOwner {
        if (router == address(0)) revert ZeroAddress();
        allowedRouters[router] = allowed;
        emit RouterAllowed(router, allowed);
    }

    function setTokenAllowed(address token, bool allowed) external onlyOwner {
        if (token == address(0)) revert ZeroAddress();
        allowedTokens[token] = allowed;
        emit TokenAllowed(token, allowed);
    }

    function executeTwoLegArbitrage(Route calldata route)
        external
        nonReentrant
        returns (uint256 amountOut, uint256 profit)
    {
        if (block.timestamp > route.deadline) revert Expired();
        if (route.recipient == address(0)) revert ZeroAddress();
        _checkAllowed(route);

        uint256 startingOutBalance = IERC20(route.tokenOut).balanceOf(address(this));
        if (!IERC20(route.tokenIn).transferFrom(msg.sender, address(this), route.amountIn)) {
            revert TransferFailed();
        }

        _approveExact(route.tokenIn, route.buyRouter, route.amountIn);
        _callRouter(route.buyRouter, route.buyCalldata);

        uint256 midBalance = IERC20(route.tokenMid).balanceOf(address(this));
        _approveExact(route.tokenMid, route.sellRouter, midBalance);
        _callRouter(route.sellRouter, route.sellCalldata);

        uint256 endingOutBalance = IERC20(route.tokenOut).balanceOf(address(this));
        amountOut = endingOutBalance - startingOutBalance;
        uint256 requiredOut = route.minAmountOut;
        if (requiredOut < route.amountIn + route.minProfit) {
            requiredOut = route.amountIn + route.minProfit;
        }
        if (amountOut < requiredOut) revert ProfitTooLow(amountOut, requiredOut);

        profit = amountOut - route.amountIn;
        if (!IERC20(route.tokenOut).transfer(route.recipient, amountOut)) {
            revert TransferFailed();
        }

        uint256 residualMid = IERC20(route.tokenMid).balanceOf(address(this));
        if (residualMid > 0) {
            if (!IERC20(route.tokenMid).transfer(route.recipient, residualMid)) {
                revert TransferFailed();
            }
        }

        emit AtomicArbitrageExecuted(msg.sender, route.tokenOut, route.amountIn, amountOut, profit);
    }

    function _checkAllowed(Route calldata route) private view {
        if (!allowedTokens[route.tokenIn]) revert TokenNotAllowed(route.tokenIn);
        if (!allowedTokens[route.tokenMid]) revert TokenNotAllowed(route.tokenMid);
        if (!allowedTokens[route.tokenOut]) revert TokenNotAllowed(route.tokenOut);
        if (!allowedRouters[route.buyRouter]) revert RouterNotAllowed(route.buyRouter);
        if (!allowedRouters[route.sellRouter]) revert RouterNotAllowed(route.sellRouter);
    }

    function _approveExact(address token, address spender, uint256 amount) private {
        IERC20(token).approve(spender, 0);
        if (!IERC20(token).approve(spender, amount)) revert TransferFailed();
    }

    function _callRouter(address router, bytes calldata data) private {
        (bool ok, bytes memory result) = router.call(data);
        if (!ok) revert SwapFailed(result);
    }
}
