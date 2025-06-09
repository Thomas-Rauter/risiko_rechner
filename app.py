import streamlit as st
import numpy as np

# Würfeln: zuerst alle Basiswürfe, dann Bonusvergabe auf höchste Ergebnisse
def roll_specific_dice(dice_list):
    base_rolls = [np.random.randint(1, sides + 1) for sides, _ in dice_list]
    bonuses = sorted([bonus for _, bonus in dice_list], reverse=True)
    sorted_rolls = sorted(base_rolls, reverse=True)
    final_rolls = [r + b for r, b in zip(sorted_rolls, bonuses)]
    return final_rolls

# Eine einzelne Kampfrunde (3 vs 2 Würfel)
def simulate_battle(att_dice_config, def_dice_config):
    att_rolls = roll_specific_dice(att_dice_config)
    def_rolls = roll_specific_dice(def_dice_config)
    att_loss, def_loss = 0, 0
    for a, d in zip(att_rolls[:2], def_rolls[:2]):
        if a > d:
            def_loss += 1
        else:
            att_loss += 1
    return att_loss, def_loss

# Wiederholte Simulation mit vollständigem Kampfverlauf
def run_simulations(n, att_dice_config, def_dice_config, att_total, def_total):
    att_remaining = []
    def_remaining = []
    for _ in range(n):
        a = att_total
        d = def_total
        while a > 3 and d > 0:
            a_loss, d_loss = simulate_battle(att_dice_config, def_dice_config)
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
    - Der Angreifer würfelt mit **3 Würfeln**, der Verteidiger mit **2**.
    - Du kannst den **Würfeltyp (W6 oder W8)** für jeden Würfel einstellen.
    - Zusätzlich kannst du jedem Rangplatz (höchster, zweithöchster, usw.) einen Bonus geben.
    - Es wird sehr oft simuliert, wie der Kampf ausgeht, um typische Ergebnisse zu berechnen.
    """)

st.header("⚙️ Kampf-Einstellungen")

col1, col2 = st.columns(2)
att_total = col1.number_input("💂 Truppenanzahl Angreifer", min_value=4, value=10)
def_total = col2.number_input("🏰 Truppenanzahl Verteidiger", min_value=1, value=6)

st.subheader("🎯 Würfel konfigurieren")

cols = st.columns(5)

# Angreifer: 3 Würfel
att_dice_config = [
    (cols[0].selectbox("Angreifer Würfeltyp 1", [6, 8], key="a_die_1"),
     cols[0].number_input("Bonus höchster Würfel", value=0, key="a_bonus_1")),
    (cols[1].selectbox("Angreifer Würfeltyp 2", [6, 8], key="a_die_2"),
     cols[1].number_input("Bonus zweithöchster Würfel", value=0, key="a_bonus_2")),
    (cols[2].selectbox("Angreifer Würfeltyp 3", [6, 8], key="a_die_3"),
     cols[2].number_input("Bonus dritthöchster Würfel", value=0, key="a_bonus_3")),
]

# Verteidiger: 2 Würfel
def_dice_config = [
    (cols[3].selectbox("Verteidiger Würfeltyp 1", [6, 8], key="d_die_1"),
     cols[3].number_input("Bonus höchster Würfel", value=0, key="d_bonus_1")),
    (cols[4].selectbox("Verteidiger Würfeltyp 2", [6, 8], key="d_die_2"),
     cols[4].number_input("Bonus zweithöchster Würfel", value=0, key="d_bonus_2")),
]

n_sim = st.slider("🔁 Anzahl Simulationen", 500, 20000, 5000, step=500)

if st.button("▶️ Simulation starten"):
    with st.spinner("Simuliere..."):
        att_res, def_res = run_simulations(n_sim, att_dice_config, def_dice_config, att_total, def_total)

    att_wins = att_res > def_res
    def_wins = def_res > att_res
    ties = (att_res == def_res)

    win_rate_att = np.mean(att_wins) * 100
    win_rate_def = np.mean(def_wins) * 100
    tie_rate = np.mean(ties) * 100

    att_mean = np.mean(att_res[att_wins]) if att_wins.any() else 0
    att_std = np.std(att_res[att_wins]) if att_wins.any() else 0

    def_mean = np.mean(def_res[def_wins]) if def_wins.any() else 0
    def_std = np.std(def_res[def_wins]) if def_wins.any() else 0

    st.subheader("📊 Ergebnis")

    if win_rate_att > win_rate_def:
        st.success(f"✅ Der Angreifer gewinnt in **{win_rate_att:.1f}%** der Fälle und hat dann im Schnitt **{att_mean:.2f}** Truppen übrig.")
    elif win_rate_def > win_rate_att:
        st.error(f"🛡️ Der Verteidiger gewinnt in **{win_rate_def:.1f}%** der Fälle und hat dann im Schnitt **{def_mean:.2f}** Truppen übrig.")
    else:
        st.info("⚖️ Beide Seiten haben ungefähr gleich gute Chancen.")

    if tie_rate > 0:
        st.markdown(f"🔄 Unentschieden in **{tie_rate:.2f}%** der Fälle")

    st.caption(f"📈 Typische Schwankung: ±{att_std:.2f} Truppen beim Angreifer, ±{def_std:.2f} beim Verteidiger")
