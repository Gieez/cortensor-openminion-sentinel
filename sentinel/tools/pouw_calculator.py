"""Cortensor Proof-of-Useful-Work (PoUW) Gas Rebate and Incentive Calculator."""

from typing import Any, Dict
from sentinel.models import PoUWRebateResult


def calculate_cortensor_rebate(
    gas_consumed: int,
    base_fee_gwei: float,
    validator_node_tier: str = "alpha-tier-1",
    cor_price_usd: float = 0.15,
    eth_price_usd: float = 2600.0
) -> Dict[str, Any]:
    """Calculate the Cortensor PoUW gas rebate in ETH and equivalent $COR reward.
    
    Formula based on Cortensor Whitepaper:
    - Base Gas Cost = Gas Consumed * Base Fee (in Gwei) * 1e-9 ETH
    - PoUW Rebate = Base Gas Cost * Tier Multiplier (5% for Tier 1, 8% for Tier 2)
    - Equivalent COR Reward = (Rebate in USD) / (COR Price in USD)
    """
    multiplier = 0.05
    if "tier-2" in validator_node_tier.lower():
        multiplier = 0.08
    elif "validator" in validator_node_tier.lower() or "dedicated" in validator_node_tier.lower():
        multiplier = 0.10

    # Total gas cost in ETH
    gas_cost_eth = (gas_consumed * base_fee_gwei) / 1e9
    rebate_eth = gas_cost_eth * multiplier

    # USD values
    rebate_usd = rebate_eth * eth_price_usd
    cor_tokens = rebate_usd / cor_price_usd if cor_price_usd > 0 else 0.0

    result = PoUWRebateResult(
        gas_consumed=gas_consumed,
        base_fee_gwei=base_fee_gwei,
        rebate_percentage=multiplier * 100.0,
        total_rebate_eth=round(rebate_eth, 8),
        cor_exchange_rate_usd=cor_price_usd,
        cor_reward_estimate=round(cor_tokens, 4),
        validator_node_tier=validator_node_tier
    )

    return result.model_dump()
