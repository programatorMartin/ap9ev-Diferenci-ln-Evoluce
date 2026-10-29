# Protokol: Diferenciálna Evolúcia (DE)

Tento protokol dokumentuje implementáciu a experimentálne porovnanie troch variantov algoritmu Diferenciálnej Evolúcie (DE): **DE/rand/1/bin**, **DE/best/1/bin** a adaptívneho variantu **jDE**.

---

## 1. Teoretický popis algoritmov

Diferenciálna evolúcia je stochastický populačný optimalizačný algoritmus pracujúci v spojitom stavovom priestore. Každá generácia pozostáva z troch základných krokov: **mutácia**, **kríženie** (rekombinácia) a **selekcia**.

### Mutačné stratégie
Pre každého jedinca $x_i$ (target vector) sa vytvára mutačný vektor $v_i$:

1. **DE/rand/1:**
   $$v_i = x_{r1} + F \cdot (x_{r2} - x_{r3})$$
   Kde $r_1, r_2, r_3$ sú náhodne zvolené vzájomne rôzne indexy odlišné od indexu aktívneho jedinca $i$. Poskytuje vysokú diverzitu populácie a zabraňuje predčasnej konvergencii.

2. **DE/best/1:**
   $$v_i = x_{\text{best}} + F \cdot (x_{r1} - x_{r2})$$
   Bázovým vektorom je aktuálne najlepší jedinec generácie $x_{\text{best}}$. Využíva informáciu o najsľubnejšom smere, vďaka čomu konverguje rýchlejšie v ranných fázach, no nesie riziko uviaznutia v lokálnom extréme alebo predčasnej straty diverzity.

3. **jDE (Self-adaptive DE):**
   Využíva mutáciu typu **Rand/1**, avšak riadiace parametre $F$ a $CR$ nie sú statické, ale sú viazané priamo na každého jedinca populácie ($F_i$, $CR_i$). Pred mutáciou sa parametre s pravdepodobnosťou $\tau_1$ a $\tau_2$ re-inicializujú:
   $$F_i = \begin{cases} 0.1 + 0.8 \cdot \text{rand}_1() & \text{ak } \text{rand}_2() < \tau_1 \\ F_i & \text{inak} \end{cases}$$
   $$CR_i = \begin{cases} \text{rand}_3() & \text{ak } \text{rand}_4() < \tau_2 \\ CR_i & \text{inak} \end{cases}$$
   Ak potomek prežije do ďalšej generácie, jeho hodnoty $F_i$ a $CR_i$ prežívajú s ním.

### Kríženie (Binomiálne)
Skúšobný vektor $u_i$ sa skladá z prvkov rodiča $x_i$ a mutanta $v_i$:
$$u_{i, j} = \begin{cases} v_{i, j} & \text{ak } \text{rand}(0, 1) \le CR \text{ alebo } j = j_{\text{rand}} \\ x_{i, j} & \text{inak} \end{cases}$$
kde $j_{\text{rand}} \in \{1, \dots, D\}$ zaručuje prenos aspoň jednej zložky z mutovaného vektora.

### Selekcia (Elitárska)
Do novej generácie postupuje jedinec s lepšou alebo rovnou hodnotou účelovej funkcie:
$$x_{i, G+1} = \begin{cases} u_{i, G} & \text{ak } f(u_{i, G}) \le f(x_{i, G}) \\ x_{i, G} & \text{inak} \end{cases}$$

---

## 2. Nastavenie experimentu

* **Testovacia funkcia:** Sphere function ($f(x) = \sum_{j=1}^{D} x_j^2$)
  * **Dimenzia ($D$):** 10
  * **Hranice priestoru:** $[-5.12, 5.12]^D$
  * **Globálne minimum:** $f(x^*) = 0.0$ v bode $x^* = (0, 0, \dots, 0)$
* **Veľkosť populácie ($NP$):** 40
* **Maximálny počet generácií ($G_{\text{max}}$):** 200
* **Parametre stratégií:**
  * **Rand/1:** $CR = 0.8$, $F = 0.5$
  * **Best/1:** $CR = 0.8$, $F = 0.5$
  * **jDE:** $\tau_1 = 0.1$, $\tau_2 = 0.1$, počiatočné $CR = 0.9$ (rozsah $[0.0, 1.0]$), počiatočné $F = 0.5$ (rozsah $[0.1, 0.9]$)

---

## 3. Namerané výsledky a konvergencia

### Dosiahnutá hodnota účelovej funkcie (generácia 200)

| Algoritmus | Najlepšia nájdená hodnota $f(x)$ |
| :--- | :--- |
| **DE/rand/1/bin** | $5.0567 \times 10^{-10}$ |
| **DE/best/1/bin** | $3.7773 \times 10^{-3}$ |
| **jDE** | **$5.8736 \times 10^{-11}$** |

### Konvergenčný graf
![Graf konvergencie](image_ae40f1.png)

---

## 4. Diskusia a vyhodnotenie

1. **Rýchlosť nástupu (Best/1):**
   * Stratégia **Best/1** vykazuje v prvých 30 generáciách najstrmší pokles hodnoty účelovej funkcie. Je to spôsobené orientáciou rozdielových vektorov priamo na najlepšieho jedinca.
   * Okolo 35. generácie však algoritmus narazil na **predčasnú stratu diverzity** (populácia sa zhlukovité zhromaždila v okolí lokálneho bodu a rozdielové vektory sa zmenšili tak, že nedokázali vygenerovať ďalšie zlepšenia), pričom konvergencia uviazla na hodnote približne $3.78 \times 10^{-3}$.

2. **Diverzita a stabilita (Rand/1):**
   * Stratégia **Rand/1** začínala pomalšie, no vďaka náhodnému výberu bázových aj diferenčných jedincov si udržala dostatočnú diverzitu počas celých 200 generácií.
   * Výsledná presnosť dosiahla rádovo $10^{-10}$, čo dokazuje schopnosť úspešne jemne dohľadávať globálne minimum.

3. **Adaptabilita (jDE):**
   * Algoritmus **jDE** dosiahol najlepšiu finálnu hodnotu ($5.87 \times 10^{-11}$).
   * Mechanizmus úspešnej propagácie parametrov $F$ a $CR$ umožnil dynamicky meniť veľkosť kroku podľa aktuálneho stavu populácie, čo viedlo k plynulej a najpresnejšej konvergencii ku koncu optimalizácie.

---

## 5. Záver
Všetky tri varianty diferenciálnej evolúcie boli úspešne implementované a otestované. Experiment potvrdil, že pre dosiahnutie vysokej presnosti a stability je vhodnejšie použiť exploratívnejšiu stratégiu **Rand/1** alebo samo-adaptívny prístup **jDE**, zatiaľ čo chamtivý prístup **Best/1** je náchylný na predčasné uviaznutie kvôli rýchlej strate rozptylu populácie.
