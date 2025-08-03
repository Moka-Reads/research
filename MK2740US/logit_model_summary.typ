#set page(margin: 2cm)
#set text(font: "Linux Libertine", size: 11pt)
#set heading(numbering: "1.")

#align(center)[
  #text(size: 16pt, weight: "bold")[
    Research Note: Why Beta Coefficients "Don't Work" in Logit Pricing Models
  ]

  #v(0.5em)
  #text(size: 12pt)[
    Identifying and Fixing Implementation Flaws in Economic Optimization
  ]
  #v(1.5em)
]

= Problem Discovery

A logit model for digital platform pricing optimization showed puzzling behavior: beta coefficients appeared to have minimal impact on optimal pricing strategies, with different preference parameters ($beta_1, beta_2, beta_3$) producing nearly identical results.

*Symptom*: All scenarios yielded identical prices regardless of consumer price sensitivity:
- Price variation across beta scenarios: $0.38
- Strategic differentiation: None observed

= Root Cause Analysis

Three critical implementation flaws were identified:

== 1. Over-Restrictive Constraints
```python
# Forced identical price sequences
x[i+1] - x[i] >= 0.05  # Delta constraint
r[i] * p[i] - r[i+1] * p[i+1] >= epsilon  # Royalty ordering
```
These constraints completely determined the solution, making beta coefficients irrelevant.

== 2. Missing Economic Trade-offs
The objective function $max sum p_i r_i s_i(bold(p), bold(beta))$ always favored maximum prices since market size was fixed. No price-volume trade-off existed.

== 3. Dominated Penalty Terms
Large penalty coefficient ($lambda = 0.05$) for price inflation overwhelmed demand effects, forcing solutions toward penalty minimization rather than economic optimization.

= Solution Implementation

== Market Size Elasticity (Key Innovation)
Introduced total market size as function of average price:
$ M = 1000 times (15 / overline(p))^{1.5} $

This creates the essential economic trade-off: higher prices → smaller markets.

== Proper Economic Objective
$ "Revenue" = sum_i M(overline(p)) times s_i(bold(p), bold(beta)) times p_i times r_i $

Now optimization must balance:
- Price per unit (higher = better)
- Market size (lower with higher prices)
- Market share allocation (driven by beta coefficients)

== Minimal Constraints
Removed rigid constraints, allowing economic forces to determine optimal pricing.

= Results

The fixed model achieved meaningful strategic differentiation:

#table(
  columns: (2fr, 1fr, 1fr, 1fr),
  [*Strategy*], [*Avg Price*], [*Market Size*], [*Revenue*],
  [Price Insensitive ($beta_3 = 0$)], [$7.86], [2,635], [$22,142],
  [Price Sensitive ($beta_3 = -1.5$)], [$5.14], [4,986], [$18,955],
  [Balanced ($beta_3 = -0.5$)], [$5.00], [5,196], [$19,240]
)

*Key Metrics*:
- Price variation: $1.11 (vs. $0.38 originally)
- Revenue range: 15% difference between strategies
- Economic logic: Premium pricing captures smaller but profitable markets

= Strategic Insights

== Two Distinct Equilibria Emerged

*Premium Strategy* (Price Insensitive Market):
- High prices ($7.86 average) attract smaller market (2,635 customers)
- Highest total revenue through margin optimization
- Optimal when $beta_3 ≈ 0$ (consumers ignore price differences)

*Volume Strategy* (Price Sensitive Market):
- Low prices (~$5.00) attract larger market (5,000+ customers)
- Lower revenue per customer but higher volume
- Optimal when $beta_3 < -1.0$ (strong price sensitivity)

= Validation

The fixed model demonstrates proper economic behavior:

1. *Demand Curves*: Higher prices reduce quantity demanded ✓
2. *Beta Impact*: Different coefficients drive different strategies ✓
3. *Trade-offs*: Price-volume optimization working correctly ✓
4. *Market Segmentation*: Strategies target different consumer types ✓

= Key Lessons

== Implementation Details Matter Enormously
The original question "why don't beta coefficients have much effect" revealed implementation flaws, not theoretical limitations. Seemingly minor constraint choices can completely determine optimization outcomes.

== Economic Structure Must Be Preserved
Models need proper trade-offs to generate realistic behavior. Missing the price-volume relationship made the model economically meaningless despite mathematical correctness.

== Constraint Design Is Critical
Over-restrictive constraints can predetermine solutions regardless of objective function parameters. Optimization space must allow meaningful choices.

= Conclusion

Beta coefficients in logit models *should* and *do* have significant impact when properly implemented. The perception that they "don't work" resulted from:

1. Constraints forcing identical solutions
2. Missing economic trade-offs
3. Penalty terms dominating optimization

After fixing these issues, beta coefficients now drive strategically differentiated pricing decisions that reflect genuine economic principles. The theoretical foundation of logit demand modeling is sound—the implementation was flawed.

*Practical Recommendation*: When beta coefficients appear ineffective in economic models, investigate constraint structures and economic completeness before questioning the underlying theory.

#align(center)[
  #text(size: 10pt, style: "italic")[
    This analysis demonstrates the critical importance of proper model implementation in revealing theoretical relationships that economic theory predicts should exist.
  ]
]
