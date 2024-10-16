# Dollar value to filter loan events, so low value test/spam loans are ignored.
filter_threshold = 50

market_operators_config = {
    'optimism': {
        '0xD74A1f6B44395cf8c4833df5Bc965C6C2b567476': {
            'collateral_name': 'WETH', 
            'collateral_decimals': 18,
            'collateral_address': '0x4200000000000000000000000000000000000006'
        },
        '0xC82B4C656BA6Aa4A2eF6bfe6b511d206C93b405b': {
            'collateral_name': 'WBTC', 
            'collateral_decimals': 8, 
            'collateral_address': '0x68f180fcCe6836688e9084f035309E29Bf0A2095'
        },
        '0xfC6Ec1F94f2fFCe0f0BcB79592D765abD3E1BAEf': {
            'collateral_name': 'WSTETH', 
            'collateral_decimals': 18, 
            'collateral_address': '0x1F32b1c2345538c0c6f582fCB022739c4A194Ebb'
        },
        '0x13aa7dBB49d414A321b403EabB1B4231e61C7b29': {
            'collateral_name': 'OP', 
            'collateral_decimals': 18, 
            'collateral_address': '0x4200000000000000000000000000000000000042'
        },
        '0x7e0242FCAA2d4844C6fF0769fac9c9cF5f8DE2d6': {
            'collateral_name': 'VELO', 
            'collateral_decimals': 18, 
            'collateral_address': '0x9560e827aF36c94D2Ac33a39bCE1Fe78631088Db'
        }
    },

    'arbitrum': {
        '0xe38FB572099A8Fdb51e0929cb2B439D0479fC43E': {
            'collateral_name': 'WETH', 
            'collateral_decimals': 18, 
            'collateral_address': '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1'
        },
        '0xB745f12eCF271484c79D3999cA12164Fe1c4e5f9': {
            'collateral_name': 'WBTC', 
            'collateral_decimals': 8, 
            'collateral_address': '0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f'
        },
        '0xEC70Ac48D2cc382987a176f64fe74d77d010F9D1': {
            'collateral_name': 'ARB', 
            'collateral_decimals': 18, 
            'collateral_address': '0x912CE59144191C1204E64559FE8253a0e49E6548'
        },
        '0xE927e8B43Da90f017b146Eff5f99515372630DD1': {
            'collateral_name': 'WSTETH', 
            'collateral_decimals': 18, 
            'collateral_address': '0x5979D7b546E38E414F7E9822514be443A4800529'
        },
        '0xa8ED217624218a4c65e6d577A26D7810E2f8f790': {
            'collateral_name': 'GMX', 
            'collateral_decimals': 18, 
            'collateral_address': '0xfc5A1A6EB076a2C7aD06eD22C90d7E710E35ad0a'
        },
        '0xE304eF44F4240E44d0A8E954c22e5007a93a4378': {
            'collateral_name': 'RDNT', 
            'collateral_decimals': 18, 
            'collateral_address': '0x3082CC23568eA640225c2467653dB90e9250AaA0'
        },
        '0xFF75fa72bbc5DB02FceB948901614A1155925592': {
            'collateral_name': 'PENDLE', 
            'collateral_decimals': 18, 
            'collateral_address': '0x0c880f6761F1af8d9Aa9C466984b80DAb9a8c9e8'
        }
    },

    'base': {
        '0xA929A836148E0635aB5EDf5B474d664601aDD2cE': {
            'collateral_name': 'WETH', 
            'collateral_decimals': 18, 
            'collateral_address': '0x4200000000000000000000000000000000000006'
        },
        '0xA86e8d5ed6F07DAb21C44e55e8576742760a7aFB': {
            'collateral_name': 'CBBTC', 
            'collateral_decimals': 8, 
            'collateral_address': '0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf'
        },
        '0xdf887F7a76744df87CF8111349657688E73257dc': {
            'collateral_name': 'CBETH', 
            'collateral_decimals': 18, 
            'collateral_address': '0x2Ae3F1Ec7F1F5012CFEab0185bfc7aa3cf0DEc22'
        }
    }
}