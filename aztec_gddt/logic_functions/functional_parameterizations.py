from typing import Tuple
from ..types import AztecModelParams, Tokens
from ..helper import rewards_to_sequencer, total_phase_duration


def determine_profitability(
    phase: str, params: AztecModelParams, fee
) -> Tuple[Tokens, Tokens, bool]:
    """Function to determine profitability for an agent

    Args:
        phase (str): The phase this function is being called in
        params (AztecModelParams): The system parameters

    Returns:
        Tuple[Tokens, Tokens, bool]: Returns the expected rewards, expected costs and whether there is a payoff
    """
    if params["fp_determine_profitability"] == "Always Pass":
        return determine_profitability_always_pass(phase, params, fee)
    elif params["fp_determine_profitability"] == "Op Cost":
        return determine_profitability_op_cost(phase, params, fee)
    else:
        assert (
            False
        ), "The param of {} for fp_determine_profitability is not valid".format(
            params["fp_determine_profitability"]
        )


def determine_profitability_always_pass(
    phase: str, params: dict, fee
) -> Tuple[float, float, bool]:
    if phase == "Reveal Content":
        expected_rewards = 1
        assert (
            expected_rewards >= 0
        ), "REVEAL_CONTENT: Expected rewards should be positive."

        expected_costs = 0
        assert expected_costs == 0, "REVEAL_CONTENT: Expected costs should be zero."

        payoff_reveal = expected_rewards - expected_costs
        return expected_rewards, expected_costs, payoff_reveal
    elif phase == "Submit Proof":
        expected_rewards = 1
        assert (
            expected_rewards >= 0
        ), "SUBMIT PROOF: Expected rewards should be positive."

        expected_costs = 0
        assert expected_costs == 0, "SUBMIT PROOF: Expected costs should be zero."

        payoff_reveal = expected_rewards - expected_costs
        return expected_rewards, expected_costs, payoff_reveal
    elif phase == "Commit Bond":
        expected_rewards = 1
        assert expected_rewards > 0, "COMMIT_BOND: Expected rewards should be positive."

        expected_costs = 0
        assert expected_costs == 0, "COMMIT_BOND: Expected costs should be 0."

        payoff_reveal = expected_rewards - expected_costs
        return expected_rewards, expected_costs, payoff_reveal

    else:
        assert False, "Not implemented for phase {}".format(phase)


def determine_profitability_op_cost(
    phase: str, params: AztecModelParams, fee
) -> Tuple[Tokens, Tokens, bool]:
    if phase == "Reveal Content":

        # Assumption: Agents have extra costs / profit considerations and need a safety buffer
        SAFETY_BUFFER = params["safety_factor_reveal_content"] * fee
        expected_l2_blocks_per_day = params["l1_blocks_per_day"] / total_phase_duration(
            params
        )
        expected_rewards = params["daily_block_reward"]
        expected_rewards *= rewards_to_sequencer(params)
        expected_rewards /= expected_l2_blocks_per_day
        assert (
            expected_rewards >= 0
        ), "REVEAL_CONTENT: Expected rewards should be positive."

        expected_costs: float = params["op_cost_sequencer"]
        expected_costs += fee
        expected_costs += SAFETY_BUFFER
        expected_costs *= params["gwei_to_tokens"]

        payoff_reveal = expected_rewards - expected_costs
        return expected_rewards, expected_costs, payoff_reveal
    elif phase == "Submit Proof":
        SAFETY_BUFFER = params["safety_factor_rollup_proof"] * fee
        expected_l2_blocks_per_day = params["l1_blocks_per_day"] / total_phase_duration(
            params
        )
        expected_rewards = params["daily_block_reward"]
        expected_rewards *= params["rewards_to_provers"]
        expected_rewards /= expected_l2_blocks_per_day
        assert (
            expected_rewards >= 0
        ), "SUBMIT PROOF: Expected rewards should be positive."

        expected_costs: float = params["op_cost_prover"]
        expected_costs += fee
        expected_costs += SAFETY_BUFFER
        expected_costs *= params["gwei_to_tokens"]

        payoff_reveal = expected_rewards - expected_costs
        return expected_rewards, expected_costs, payoff_reveal
    elif phase == "Commit Bond":
        SAFETY_BUFFER = params["safety_factor_commit_bond"] * fee

        expected_l2_blocks_per_day = params["l1_blocks_per_day"] / total_phase_duration(
            params
        )
        expected_rewards = params["daily_block_reward"]
        expected_rewards *= rewards_to_sequencer(params)
        expected_rewards /= expected_l2_blocks_per_day
        assert expected_rewards > 0, "COMMIT_BOND: Expected rewards should be positive."

        expected_costs: float = params["op_cost_sequencer"]
        expected_costs += fee
        expected_costs += SAFETY_BUFFER
        expected_costs *= params["gwei_to_tokens"]

        payoff_reveal = expected_rewards - expected_costs
        return expected_rewards, expected_costs, payoff_reveal

    else:
        assert False, "Not implemented for phase {}".format(phase)
