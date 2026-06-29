from __future__ import annotations

from decimal import Decimal
import unittest

from app.quotes.models import QuoteRequest
from app.quotes.uniswap_v3_quote_provider import (
    UNISWAP_V3_BASE_FACTORY,
    UNISWAP_V3_BASE_QUOTER_V2,
    UNISWAP_V3_BASE_SWAP_ROUTER_02,
    UNISWAP_V3_FEE_TIERS,
    UniswapV3QuoteProvider,
)
from app.registry.dexes import get_dexes_for_chain


class UniswapV3QuoteProviderTests(unittest.TestCase):
    def test_base_contract_addresses_are_official_deployments(self) -> None:
        self.assertEqual(UNISWAP_V3_BASE_FACTORY.lower(), "0x33128a8fc17869897dce68ed026d694621f6fdfd")
        self.assertEqual(UNISWAP_V3_BASE_SWAP_ROUTER_02.lower(), "0x2626664c2603336e57b271c5c0b26f421741e481")
        self.assertEqual(UNISWAP_V3_BASE_QUOTER_V2.lower(), "0x3d4e44eb1374240ce5f1b871ab261cd16335b76a")

    def test_registry_uses_verified_uniswap_v3_swap_router(self) -> None:
        uniswap_v3 = next(row for row in get_dexes_for_chain("base") if row.name == "Uniswap V3")

        self.assertEqual(str(uniswap_v3.router_address).lower(), UNISWAP_V3_BASE_SWAP_ROUTER_02.lower())
        self.assertIn("QuoterV2", uniswap_v3.notes)

    def test_provider_supports_base_uniswap_v3_requests(self) -> None:
        provider = UniswapV3QuoteProvider()

        self.assertTrue(
            provider.supports(
                QuoteRequest(
                    chain="base",
                    dex="Uniswap V3",
                    token_in="WETH",
                    token_out="USDC",
                    amount_in=Decimal("1"),
                )
            )
        )
        self.assertFalse(
            provider.supports(
                QuoteRequest(
                    chain="base",
                    dex="Aerodrome",
                    token_in="WETH",
                    token_out="USDC",
                    amount_in=Decimal("1"),
                )
            )
        )

    def test_fee_tiers_cover_common_base_eth_usdc_pools(self) -> None:
        self.assertEqual(UNISWAP_V3_FEE_TIERS, (500, 3000, 10000))


if __name__ == "__main__":
    unittest.main()
