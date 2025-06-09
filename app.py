import streamlit as st
import numpy as np

# Richtige Bonus-Zuweisung: erst Würfeln, dann sortieren, dann Bonus anwenden
def roll_specific_dice(dice_list):
    base_rolls = [np.random.randint(1, sides + 1) for sides, _ in dice_list]
    bonuses = sorted([bonus for _, bonus in dice_list], reverse=True)
    sorted_rolls = sorted(base_rolls, reverse=True)
    final_rolls = [r + b for r, b in zip(sorted_rolls, bonuses)]
    return final_rolls

# Simuliert einen einzelnen Kampf
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

# Mehrfach-Simulation ganzer Kämpfe
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
    - Du kannst für jeden Würfel den Typ (W6 oder W8) und einen Bonus angeben.
    - Die Boni gelten **immer auf die höchsten Würfe** – der stärkste Bonus auf das höchste Ergebnis, usw.
    - Wir simulieren viele Kämpfe zwischen gleichbleibenden Truppenstärken.
    """)

st.header("⚙️ Kampf-Einstellungen")

col1, col2 = st.columns(2)
att_total = col1.number_input("💂 Truppenanzahl Angreifer", min_value=4, value=10)
def_total = col2.number_input("🏰 Truppenanzahl Verteidiger", min_value=1, value=6)

st.subheader("🎯 Würfel konfigurieren")

cols = st.columns(5)

# Angreifer: 3 Würfel
att_dice_config = [
    (cols[i].selectbox(f"Angreifer W{i+1}", [6, 8], key=f"a{i}"),
     cols[i].number_input(f"Bonus A{i+1}", value=0, key=f"ab{i}"))
    for i in range(3)
]

# Verteidiger: 2 Würfel
def_dice_config = [
    (cols[i+3].selectbox(f"Verteidiger W{i-2}", [6, 8], key=f"d{i}"),
     cols[i+3].number_input(f"Bonus V{i-2}", value=0, key=f"db{i}"))
    for i in range(3, 5)
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
