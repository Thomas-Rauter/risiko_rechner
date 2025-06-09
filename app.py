"""
Streamlit app
"""

import streamlit as st
import numpy as np


def roll_specific_dice(
        dice_list: list[tuple[int, int]]
) -> list[int]:
    """
    Roll a given list of dice and apply bonuses to the highest rolls.

    Each die is specified as a (sides, bonus) tuple. All dice are rolled
    first without bonuses. Then, the rolls are sorted in descending order,
    and the bonuses are sorted in descending order and applied to the
    highest rolls.

    Parameters
    ----------
    dice_list : list of tuple of (int, int)
        Each tuple contains (sides, bonus) for one die.

    Returns
    -------
    list of int
        The final results after applying bonuses to the sorted rolls.
    """
    base_rolls = [np.random.randint(1, sides + 1) for sides, _ in dice_list]
    bonuses = sorted([bonus for _, bonus in dice_list], reverse=True)
    sorted_rolls = sorted(base_rolls, reverse=True)
    final_rolls = [r + b for r, b in zip(sorted_rolls, bonuses)]
    return final_rolls


def simulate_battle(
        attacker_dice_config: list[tuple[int, int]],
        defender_dice_confg: list[tuple[int, int]],
        a_truppen: int,
        d_truppen: int
) -> tuple[int, int]:
    """
    Simulate a single battle round between attacker and defender.

    The number of dice used depends on the current troop counts:
    - Attacker uses up to 3 dice, but always leaves 1 troop behind.
    - Defender uses up to 2 dice, depending on remaining troops.

    Dice are rolled according to configuration, bonuses are applied
    to the highest rolls, and then compared pairwise. Each comparison
    results in a loss for one side.

    Parameters
    ----------
    attacker_dice_config : list of tuple of (int, int)
        List of (sides, bonus) for attacker dice.
    defender_dice_confg : list of tuple of (int, int)
        List of (sides, bonus) for defender dice.
    a_truppen : int
        Current number of attacker troops.
    d_truppen : int
        Current number of defender troops.

    Returns
    -------
    tuple of int
        att_loss : int
            Number of attacker troops lost in this round.
        def_loss : int
            Number of defender troops lost in this round.
    """
    att_dice = min(3, a_truppen - 1)
    def_dice = min(2, d_truppen)

    att_rolls = roll_specific_dice(attacker_dice_config[:att_dice])
    def_rolls = roll_specific_dice(defender_dice_confg[:def_dice])

    att_loss, def_loss = 0, 0
    for a, d in zip(att_rolls, def_rolls):
        if a > d:
            def_loss += 1
        else:
            att_loss += 1
    return att_loss, def_loss


def run_simulations(
        n: int,
        att_dice_config: list[tuple[int, int]],
        def_dice_config: list[tuple[int, int]],
        att_total: int,
        def_total: int
) -> tuple[np.ndarray, np.ndarray]:
    """
    Simulate multiple full battles between attacker and defender.

    Each battle proceeds round by round until the defender is defeated
    (0 troops) or the attacker has only 1 troop left (cannot attack
    further). The attacker must always leave 1 troop behind and adjusts
    the number of dice accordingly.

    Parameters
    ----------
    n : int
        Number of simulations to run.
    att_dice_config : list of tuple of (int, int)
        Each tuple represents a die with (sides, bonus) for the attacker.
        All 3 dice are always defined; only the number used depends on
        remaining troops.
    def_dice_config : list of tuple of (int, int)
        Each tuple represents a die with (sides, bonus) for the defender.
        All 2 dice are always defined; only the number used depends on
        remaining troops.
    att_total : int
        Initial number of attacker troops (must be >= 2 to allow at least
        one attack).
    def_total : int
        Initial number of defender troops.

    Returns
    -------
    tuple of np.ndarray
        att_remaining : array of int
            Number of attacker troops remaining after each simulation.
        def_remaining : array of int
            Number of defender troops remaining after each simulation.
    """
    att_remaining = []
    def_remaining = []
    for _ in range(n):
        a = att_total
        d = def_total
        while a > 1 and d > 0:
            a_loss, d_loss = simulate_battle(
                att_dice_config,
                def_dice_config,
                a,
                d
            )
            a -= a_loss
            d -= d_loss
        att_remaining.append(max(0, a))
        def_remaining.append(max(0, d))
    return np.array(att_remaining), np.array(def_remaining)

# Streamlit UI
st.set_page_config(page_title="Risiko Kampfrechner", layout="wide")
st.title("🎲 Risiko Kampfrechner")

with st.expander("ℹ️ Wie funktioniert das?", expanded=False):
    st.markdown("""
    - Gib ALLE Angreifer-Truppen an, die auf dem Feld stehen. Der Rechner 
    berücksichtigt, dass eine Truppe immer zurückbleiben muss.
    - Der Rechner berücksichtigt, dass gegen Ende des Kampfes oft weniger 
    Würfel geworfen werden (wenn z.B. der Verteidiger nur noch 1 Truppe übrig hat).
    - Der Angreifer würfelt mit **3 Würfeln**, der Verteidiger mit **2**.
    - Du kannst den **Würfeltyp (W6 oder W8)** für jeden Würfel einstellen.
    - Zusätzlich kannst du jedem Rangplatz (höchster, zweithöchster, usw.) einen Bonus geben.
    - Es wird sehr oft simuliert, wie der Kampf ausgeht, um typische Ergebnisse zu berechnen.
    """)

st.header("⚙️ Kampf-Einstellungen")

col1, col2 = st.columns(2)
attacker_total = col1.number_input(
    "💂 Truppenanzahl Angreifer",
    min_value=4,
    value=10
)
defender_total = col2.number_input(
    "🏰 Truppenanzahl Verteidiger",
    min_value=1,
    value=6
)

st.subheader("🎯 Würfel konfigurieren")

cols = st.columns(5)

# Angreifer: 3 Würfel
dice_config_attacker = [
    (cols[0].selectbox("Angreifer Würfeltyp 1", [6, 8], key="a_die_1"),
     cols[0].number_input("Bonus höchster Würfel", value=0, key="a_bonus_1")),
    (cols[1].selectbox("Angreifer Würfeltyp 2", [6, 8], key="a_die_2"),
     cols[1].number_input("Bonus zweithöchster Würfel", value=0, key="a_bonus_2")),
    (cols[2].selectbox("Angreifer Würfeltyp 3", [6, 8], key="a_die_3"),
     cols[2].number_input("Bonus dritthöchster Würfel", value=0, key="a_bonus_3")),
]

# Verteidiger: 2 Würfel
dice_config_defender = [
    (cols[3].selectbox("Verteidiger Würfeltyp 1", [6, 8], key="d_die_1"),
     cols[3].number_input("Bonus höchster Würfel", value=0, key="d_bonus_1")),
    (cols[4].selectbox("Verteidiger Würfeltyp 2", [6, 8], key="d_die_2"),
     cols[4].number_input("Bonus zweithöchster Würfel", value=0, key="d_bonus_2")),
]

n_sim = st.slider(
    "🔁 Anzahl Simulationen",
    500,
    20000,
    5000,
    step=500
)

if st.button("▶️ Simulation starten"):
    with st.spinner("Simuliere..."):
        att_res, def_res = run_simulations(
            n_sim,
            dice_config_attacker,
            dice_config_defender,
            attacker_total,
            defender_total
        )

    # Attacker wins when defender has no more troops
    att_wins: np.ndarray = np.array(def_res == 0, dtype=bool)
    # Defender wins when attacker cannot attack anymore
    def_wins: np.ndarray = np.array(att_res == 1, dtype=bool)

    invalid = ~(att_wins | def_wins)
    if np.any(invalid):
        raise RuntimeError(
            f"{np.sum(invalid)} simulation(s) ended in an invalid state "
            f"(attacker > 1 and defender > 0). This indicates a code logic "
            f"error."
        )

    win_rate_att = float(np.mean(att_wins)) * 100
    win_rate_def = float(np.mean(def_wins)) * 100

    # Avg nr. attacker troops left when attacker won
    att_mean = np.mean(att_res[att_wins]) if att_wins.any() else 0
    att_std = np.std(att_res[att_wins]) if att_wins.any() else 0

    # Avg nr. defender troops left when defender won
    def_mean = np.mean(def_res[def_wins]) if def_wins.any() else 0
    def_std = np.std(def_res[def_wins]) if def_wins.any() else 0

    st.subheader("📊 Ergebnis")

    if win_rate_att > win_rate_def:
        st.success(f"✅ Der Angreifer gewinnt in **{win_rate_att:.1f}%** der Fälle und hat dann im Schnitt **{att_mean:.2f}** Truppen übrig.")
    elif win_rate_def > win_rate_att:
        st.error(f"🛡️ Der Verteidiger gewinnt in **{win_rate_def:.1f}%** der Fälle und hat dann im Schnitt **{def_mean:.2f}** Truppen übrig.")
    else:
        st.info("⚖️ Beide Seiten haben ungefähr gleich gute Chancen.")

    st.caption(f"📈 Typische Schwankung: ±{att_std:.2f} Truppen beim Angreifer, ±{def_std:.2f} beim Verteidiger")
