# risiko_simulator_app.py
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt


def roll_dice(n_dice, sides, bonus):
    return sorted(
        [np.random.randint(1, sides + 1) + bonus for _ in range(n_dice)],
        reverse=True)


def simulate_battle(att_troops, def_troops, att_die, def_die, att_bonus,
                    def_bonus):
    a = att_troops
    d = def_troops
    while a > 1 and d > 0:
        att_rolls = roll_dice(min(3, a - 1), att_die, att_bonus)
        def_rolls = roll_dice(min(2, d), def_die, def_bonus)
        for att, df in zip(att_rolls, def_rolls):
            if att > df:
                d -= 1
            else:
                a -= 1
    return a, d


def run_simulations(n, att_troops, def_troops, att_die, def_die, att_bonus,
                    def_bonus):
    results = [
        simulate_battle(att_troops, def_troops, att_die, def_die, att_bonus,
                        def_bonus)
        for _ in range(n)]
    att_remaining = [res[0] for res in results]
    def_remaining = [res[1] for res in results]
    return att_remaining, def_remaining


st.title("🎲 Risiko Kampfrechner")

st.sidebar.header("Einstellungen")

att_troops = st.sidebar.number_input("Angreifer-Truppen", min_value=1, value=10)
def_troops = st.sidebar.number_input("Verteidiger-Truppen", min_value=1,
                                     value=5)
att_die = st.sidebar.selectbox("Angreifer-Würfel", [6, 8, 10, 12, 20], index=0)
def_die = st.sidebar.selectbox("Verteidiger-Würfel", [6, 8, 10, 12, 20],
                               index=0)
att_bonus = st.sidebar.number_input("Angreifer-Bonus", value=0)
def_bonus = st.sidebar.number_input("Verteidiger-Bonus", value=0)
n_sim = st.sidebar.number_input("Anzahl Simulationen", min_value=100,
                                max_value=50000, step=1000, value=10000)

if st.button("🔁 Kampf simulieren"):
    with st.spinner("Simuliere..."):
        att_res, def_res = run_simulations(n_sim, att_troops, def_troops,
                                           att_die, def_die, att_bonus,
                                           def_bonus)

    att_mean = np.mean(att_res)
    def_mean = np.mean(def_res)
    att_std = np.std(att_res)
    def_std = np.std(def_res)
    win_prob = np.mean([d == 0 for d in def_res]) * 100

    st.subheader("📊 Ergebnisse")
    st.markdown(f"- 🛡️ Verteidiger besiegt in **{win_prob:.2f}%** der Fälle")
    st.markdown(
        f"- 💂 Erwartete verbleibende Angreifer: **{att_mean:.2f} ± {att_std:.2f}**")
    st.markdown(
        f"- 🏰 Erwartete verbleibende Verteidiger: **{def_mean:.2f} ± {def_std:.2f}**")

    fig, ax = plt.subplots()
    ax.hist(att_res, bins=range(0, max(att_res) + 2), alpha=0.7,
            label='Angreifer')
    ax.hist(def_res, bins=range(0, max(def_res) + 2), alpha=0.7,
            label='Verteidiger')
    ax.set_xlabel("Verbleibende Truppen")
    ax.set_ylabel("Anzahl Simulationen")
    ax.legend()
    st.pyplot(fig)
