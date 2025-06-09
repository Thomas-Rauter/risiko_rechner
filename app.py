import streamlit as st
import numpy as np

def roll_specific_dice(dice_list):
    rolls = [np.random.randint(1, sides + 1) + bonus for sides, bonus in dice_list]
    return sorted(rolls, reverse=True)

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

def run_simulations(n, att_dice_config, def_dice_config):
    att_remaining = []
    def_remaining = []
    for _ in range(n):
        att = 3
        deff = 2
        a_loss, d_loss = simulate_battle(att_dice_config, def_dice_config)
        att -= a_loss
        deff -= d_loss
        att_remaining.append(att)
        def_remaining.append(deff)
    return np.array(att_remaining), np.array(def_remaining)

st.set_page_config(page_title="Risiko Kampfrechner", layout="wide")
st.title("🎲 Risiko Kampfrechner")

with st.expander("ℹ️ Wie funktioniert das?"):
    st.markdown("""
    - Der Angreifer würfelt mit **3 Würfeln**, der Verteidiger mit **2**.
    - Du kannst für jeden Würfel den Typ (z.B. W6 oder W8) und einen Bonus angeben.
    - Wir simulieren viele Kämpfe und zeigen dir, wie oft der Angreifer gewinnt und wie viele Truppen dann typischerweise übrig bleiben.
    """)

st.header("⚙️ Würfel einstellen")

cols = st.columns(5)
att_dice_config = [
    (cols[i].selectbox(f"Angreifer W{i+1}", [6, 8, 10], key=f"a{i}"),
     cols[i].number_input(f"Bonus A{i+1}", value=0, key=f"ab{i}"))
    for i in range(3)
]
def_dice_config = [
    (cols[i+3].selectbox(f"Verteidiger W{i+1}", [6, 8, 10], key=f"d{i}"),
     cols[i+3].number_input(f"Bonus V{i+1}", value=0, key=f"db{i}"))
    for i in range(2)
]

n_sim = st.slider("🔁 Anzahl Simulationen", 500, 20000, 5000, step=500)

if st.button("▶️ Simulation starten"):
    with st.spinner("Simuliere..."):
        att_res, def_res = run_simulations(n_sim, att_dice_config, def_dice_config)

    att_wins = att_res > 0
    def_wins = def_res > 0
    ties = (att_res == 0) & (def_res == 0)

    win_rate_att = np.mean(att_wins) * 100
    win_rate_def = np.mean(def_wins) * 100
    tie_rate = np.mean(ties) * 100

    att_mean = np.mean(att_res[att_wins]) if att_wins.any() else 0
    att_std = np.std(att_res[att_wins]) if att_wins.any() else 0

    def_mean = np.mean(def_res[def_wins]) if def_wins.any() else 0
    def_std = np.std(def_res[def_wins]) if def_wins.any() else 0

    st.subheader("📊 Ergebnis")

    if win_rate_att > win_rate_def:
        st.success(f"✅ **Der Angreifer gewinnt in {win_rate_att:.1f}% der Fälle** und hat dann im Schnitt **{att_mean:.2f} Truppen** übrig.")
    elif win_rate_def > win_rate_att:
        st.error(f"🛡️ **Der Verteidiger gewinnt in {win_rate_def:.1f}% der Fälle** und hat dann im Schnitt **{def_mean:.2f} Truppen** übrig.")
    else:
        st.warning("⚖️ Beide Seiten haben ungefähr gleich gute Chancen.")

    if tie_rate > 0:
        st.markdown(f"🔄 Unentschieden in **{tie_rate:.2f}%** der Fälle")

    st.caption(f"📈 Typische Schwankung: ±{att_std:.2f} Truppen beim Angreifer, ±{def_std:.2f} beim Verteidiger")
