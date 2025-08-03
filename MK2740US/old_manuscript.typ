#import "@preview/unequivocal-ams:0.1.2": ams-article, theorem, proof
#show par: set par(spacing: 2em)
#show: ams-article.with(
  title: [Optimizing Pricing Strategy with Royalty Constraints],
  authors: (
    (
      name: "Mustafif Khan",
      department: [],
      organization: [MoKa Reads Collective],
      location: [],
      email: "mustafif.khan@mokareads.org",
      url: "mokareads.org",
    ),
  ),
  abstract: include "abstract.typ",
  bibliography: bibliography("refs.bib", full: true),
)

#set math.equation(numbering: "(1)")

In this paper we will be exploring a nonlinear optimization problem to determine the best prices for a publication given
various distribution formats and producers. The method we use to determine the best price is by using a royalty constraint with
the main premise being able to "spend the least to support the most", this slogan is directly tied to the collective's interest as
a not-for-profit organization to sell publications not for pure profit, but in a affordable, accessible way that enables readers and
our interest to being able to support ourselves aligned.

We will firstly discuss about the market, having a look at different books, their prices, page counts and trying to build a relationship with it,
thereafter, we can start looking at our problem formulation, ways to approach it, and lastly we will look at results for determining the optimal prices
for publications in the MoKa Reads Collective or a minimum set price.

= Market Analysis and Price-per-Page Relationship

// We firstly take a look into the market
// and determine a relationship with book's prices. While prices of books per organization can depend on their contract with the writer, demand in the technology,
// organization's margins;  for simplicity purposes with the data we have gathered, we are going to look at the data mainly with a price and page count point-of-view.

To begin, we analyze the current programming book market to explore the relationship between book price and page count. Although pricing can be influenced by factors
such as author contracts, content demand, and publisher margin strategies, we restrict our focus to two primary variables: price and page count.

In this paper, all prices are assumed to be under the Canadian Dollar (CAD) unless explicitly stated not to be.
Data was collected using the Google Books API, which provides convenient access to structured information such
as book price and page count. This approach eliminates the need for web scraping and allows for efficient data retrieval under usage rate limits.

// To gather our data of different books in the programming
// category which our publications focus on,
// we make use of the Google Books API, this API is convenient to use as it provides easy ways to query, get price and page count information,
// free with rate-limit usage, and doesn't involve us needing to scrape websites.

// iffy on this, may need to change later
// From our data, we do require to clean it to remove any entry which does not include their price or page count, and we do have a flag to check whether the book's format is an ebook
// or not, in our data all books are ebooks. #text(fill: color.red, [This isn't an issue, as when we come to getting results, many of the distributions are ebooks, so their price bounds are the most critical
//   to determine, while determining paperback can be 1.5 times the price, and hardcover 1.5 times the paperback's]).

Given that the majority of our publications will be released in digital format, our pricing analysis focuses on ebooks. This is consistent with the format of our dataset, which exclusively contains ebooks.
Print formats such as paperback and hardcover are considered secondary and are typically estimated by applying standard multipliers—1.5× for paperback over ebook, and an additional 1.5× for hardcover over paperback. For our purposes
we will keep the price within the price bound we develop.

// From our dataset, we have the following statistical description for the page count and price of the books.
After cleaning the dataset to remove entries missing either price or page count, we obtained summary statistics shown in #ref(<stats_description>).
#figure(
  [
    #table(
      columns: 3,
      rows: auto,
      ..csv("figures/stats.csv").flatten(),
    )
  ],
  caption: "Descriptive statistics of page count and price for programming books retrieved from Google Books API",
)<stats_description>

// While we don't immediately interpret the data just from its statistic description, we can follow better from the distribution
// when these are plotted.
While the table provides a statistical overview, further insight is gained through visualization.
#ref(<price_vs_pagecount>) shows a scatter plot of price versus page count distribution. A notable concentration of titles lies within the 200–400 page range, which
we expect our publications in the collective to target.
// where prices tend to cluster around \$50. This observation motivates setting $50 as a practical upper bound for print formats, with ebook prices targeting the more accessible midpoint of $25–30.

#figure(
  image("figures/price_vs_pages.png", width: 82%),
  caption: "Scatter Plot of Price vs. Page Count",
)<price_vs_pagecount>

// If we focus on the the section for page count between 200-400 pages, as this is the range our books will most likely follow,
// we can see the price concentrates at \$50. This price would be a good maximum price to set for our print formats, and for our ebooks
// we would want to have it closer to the halfway mark, $\$25^+$.

As illustrated in #ref(<price_vs_pagecount>), books within the 200–400 page range cluster around a price point of approximately $\$50$.
This suggests that \$50 may serve as an upper bound for our formats, while pricing could reasonably target a midpoint range of \$25–30 to improve affordability.

The range chosen can additionally be supported by the 2024 Canadian Book Consumer Study #ref(<booknet2024cbc>) which found $53%$ of Canadians purchasing new books in the price range
of \$1-49.


= The Optimization Problem

// Suppose there are $n$ platforms or sale formats each with a unit price $p_i$ for format $i$, and a royalty rate $r_i in [0, 1)$ such that
// you receive $r_i * p_i$ as royalty earnings per unit.

// We seek to determine the optimal prices $p_i in [p_"min", p_"max"]$ with $x_i in [0, 1]$ representing
// the normalized position within that range:

In the context of multi-platform publishing, determining optimal pricing across these various platforms and the
formats they support (eg. Ebook, Paperback, Hardcover) requires a balance between the royalties earned per unit,
format differentiation such as how ebooks won't have a print cost compared to paperback or hardcover which effects the author's earnings,
and the affordability of the publication to the consumer or reader.

Let there be $n$ publishing formats/platforms where each associated with a unit price $p in [p_"min", p_"max"]$,
a corresponding royalty rate $r_i in (0, 1)$ that determines the revenue earned per unit sold: $r_i p$, and lastly the platform's market share $m_i$. To ensure
consistency and flexibility, we express each price as a normalized variable $x_i in (0, 1)$, such that:

$
p(x_i) = p_min + x_i (p_"max" - p_"min")
$

This formulation allows the optimization to occur over the unit interval, while still mapping to actual price values within a global price bound.



// The optimization problem becomes trying to maximizes the total royalty revenue per unit minus a penalty on total price:

// The primary objective of our problem is to maximize the total expected royalty across all formats/platforms, while
// simultaneously penalizing excessive pricing to maintain affordability and market competitiveness, thus allowing consumers
// to be rewarded by choosing to buy the publication from platforms which offer higher royalty rates.The proposed objective function
// is a convex combination of maximizing total royalty and penalizing the total squared price:

The primary objective of our problem is to maximize the total expected royalty across all platforms, while maintaining a balance in
the price to maintain a focus on affordability, accessability and variability in price between each platform. The objective function is defined in a reward and penalty
form, where the _reward_ is the expected total royalty earned from all platforms while also considering the market share, and the
_penalty_ term is the negative entropy of the price in all platforms.

$
  max_(upright(x in [0, 1]^n)) quad [sum_(i=1)^n p(x_i) dot tau(r_i, m_i) - lambda_p sum_(i=1)^n p(x_i) ln(p(x_i))]
$<max_objective>

Where $tau(r_i, m_i)$ is a logit function defined as:

$
  tau(r_i, m_i) &= e^(U(r_i, m_i))/(sum_j e^(U(r_j, m_j)))\
  U(r_i, m_i) &= beta_1 r_i + beta_2 m_i
$

The logit function $tau$ uses a utility variable $U$ which is used to describe the price sensitivity based on
its royalty rate and the market share that are balanced with $beta_1, beta_2$.

// $
// max_(upright(x in [0, 1]^n)) quad [sum_(i=1)^n r_i p_i - lambda_p (sum_(i=1)^n p_i)^2]
// $


Equivalently, this can be posed as a minimization problem that we can use in numerical optimization techniques:

$
min_(upright(x in [0, 1]^n)) quad [-sum_(i=1)^n p(x_i) dot tau(r_i, m_i) + lambda_p sum_(i=1)^n p(x_i) ln(p(x_i))]
$

Here, the parameter $lambda_p >= 0$ governs the trade-off between maximizing royalties and discouraging price inflation.
A higher $lambda_p$ places greater emphasis on reducing the overall price, thereby improving affordability.

#align(center)[
  *Constraints*
]

To ensure logical structure and consistency in pricing and royalty assignment, we impose two key sets of contraints onto our problem:

// The first contraint that we apply on our model is to ensure price ordering by enforcing
// strictly increasing normalized price levels:

1. *Monotocity in Price Levels:* To prevent illogical pricing where a format perceived to be of lower value is priced above a higher-tier format, we require strictly increasing normalized price levels:

$
x_(i+1) - x_i >= delta quad forall i=1, ..., n-1
$

2. *Monotocity in Royalty-per-Unit:* To incentivize distribution through high-royalty platforms and maintain economic alignment, we require that the effective royalty earned per unit decreases across formats of decreasing royalty rate:

// While we ensure price ordering which is what affects the consumers or readers who wish to purchase the publication,
// on the other end, the "profit" or royalty-per-unit. The royalty-per-unit ordering ensures that platforms with higher
// royalty rates yield grater or equal royalty-per-unit than those with lower rates:

$
r_i p(x_i) >= r_(i+1) p(x_(i+1)) + epsilon quad forall i=1, ..., n-1
$

#v(5pt)
#align(center)[
  *Initialization Strategy*
]

To help acheive convergence faster and add bias to the optimization towards realistic solutions, we propose a smart initialization based on the ordinal rank of the royalty rate. Let $R(r_i)$
denote the rank of format $i$'s royalty rate among all formats, with rank $0$ being the highest. Let $U$ denote the number of unique royalty tiers, then
the initial guess for each normalized price is given by:

$
x_i^((0)) = R(r_i)/(U-1)
$

This initialization method places formats with higher royalty rates closer to the lower bound of the price range, thus having our model bias
towards our affordability goal.

= Applying the Model to Determine Minimum Set Prices

// To apply our model, we will be solving it using Sequential Least Squares Programming (SLSQP) algorithm, which supports
// both inequality constraints and variable bounds, and is a well suited method for our structured pricing optimization problem.

// rewrite this in our words:
// #text(fill: color.red, [To solve the royalty-constrained pricing optimization problem, we employ gradient-based constrained optimization methods such as Sequential Least Squares Programming (_SLSQP_) and the Trust-Region Constrained (_trust-constr_) algorithm. These methods are well-suited for problems that feature nonlinear objective functions and nonlinear inequality constraints, as is the case here where we balance royalty maximization against pricing regularization while enforcing inter-format royalty and price orderings. SLSQP is particularly attractive due to its efficient handling of both equality and inequality constraints, along with variable bounds, in a relatively low-dimensional space. Alternatively, the trust-constr method provides a more robust framework by incorporating trust-region steps and allowing for Jacobian and Hessian approximations, which improves stability in the presence of tightly coupled constraints. Both methods leverage the smoothness and structure of the problem to converge efficiently to locally optimal solutions that satisfy all pricing and royalty conditions. This makes them strong candidates for reliably determining minimum viable prices across publishing formats while maintaining economic consistency.])

// Let us consider the following platforms that are used for self-publishing by the MoKa Reads Collective: MoKa Reads Shop, Kindle Direct Publishing (KDP), Leanpub, Kobo, Google Books and Barnes \& Noble (B\&N).
// These plaforms have the following royalty rates, it is assumed the format is Ebook, unless explicitly stated otherwise:

To solve the royalty-constrained pricing optimization problem, we employ two gradient-based nonlinear optimization methods: Sequential Least Squares Programming (SLSQP) and the Trust Region Constrained (trust-constr) algorithm.
These methods are well-suited for problems that involve smooth objective functions and nonlinear inequality constraints—characteristics inherent to our pricing model, which simultaneously seeks to maximize royalties,
enforce monotonicity, and preserve pricing fairness.

The SLSQP algorithm, originally proposed by Kraft (1988) #ref(<kraft1988sqp>), is a quasi-Newton method that handles both equality and inequality constraints efficiently.
It updates the solution iteratively using sequential quadratic programming steps, making it particularly suitable for small- to medium-scale problems with smooth constraint structure.

By contrast, the trust-region constrained method (Byrd, Schnabel, and Shultz, 1987) #ref(<byrdTrustRegionAlgorithm1987>) provides a more robust approach by solving a local approximation of the problem within a dynamically updated region where
the model is trusted to be accurate. It incorporates both first- and second-order derivative information (Jacobian and Hessian) and uses barrier or merit functions to handle inequality constraints. This makes it
more stable for tightly coupled constraint systems or cases where convergence is sensitive to initial guesses or step sizes.

We now apply the model to determine optimal pricing across self-publishing platforms used by the MoKa Reads Collective. The selected platforms, with corresponding formats and royalty rates, are shown below:

// #figure(table(
//   columns: 2,
//   rows: auto,
//   [Platform],
//   [Royalty],
//   [MoKa Reads Shop],
//   $92.5%$,
//   [Leanpub],
//   [$80%$ #ref(<leanpub>)],
//   [Kobo, Google Books, B\&N],
//   $70%$,
//   [KDP Paperback],
//   [$60%$ #ref(<noauthor_paperback_nodate>)],
//   [B\&N Print],
//   [$55%$ #ref(<barnesnoble_make_nodate>)],
//   [KDP Ebook],
//   [$35%$ #ref(<noauthor_ebook_nodate>)],
// ), caption: [Platform Format Royalty Rates])

#figure(table(
  columns: 3,
  rows: auto,
  ..csv("figures/platforms.csv").flatten(),
))

// #text(fill: color.red, [
//   It is important to note that the reason our royalty rate for KDP is $35%$ is due to our ebook prices being over the
//   maximum of $9.99$ that KDP requires to be eligible for its $70%$ royalty option. Another thing to remember is the royalty-per-unit
//   for print formats (paperback, hardcover) is the earnings from the royalty, and does not include printing costs, so while for ebook,
//   we can synonymously say the royalty is the profit margin, the same cannot be said for print formats, and is the reason we say the prices
//   are the minimum set, while the optimal prices for ebooks will not change if the book is between 200-400 pages, the same guarantee cannot be made
// for print formats, and may be be adjusted due to print costs.])
*Note*: The 35% rate for KDP eBooks arises because our prices exceed the $\$9.99$ cap for eligibility under their $70%$ royalty program #ref(<PaperbackRoyalty>). For print formats, royalties reflect author revenue before printing costs,
reinforcing our interpretation of these as minimum set prices. Ebook prices, in contrast, are profit-aligned.

The following parameters are used in our optimization procedure:

#figure(
  table(
    columns: 2,
    rows: auto,
    [Parameter],
    [Value],
    $(p_"min", p_"max")$,
    $(8.99, 50)$,
    $delta$,
    $0.05$,
    $epsilon$,
    $0.25$,
    $lambda_p$,
    $0.05$,
    $r$,
    $[0.925, 0.8, 0.7, 0.6, 0.55]$,
  ),
  caption: [Parameters for SLSQP and TRCP solvers],
)

#align(center)[*Optimization Results*]

We ran both SLSQP and Trust-Region solvers using the same problem formulation and constraints.
Remarkably, both methods converge to identical price vectors,
showing high consistency and validating the model's numerical stability.

#figure(
  table(columns: 5, rows: auto, ..csv("figures/pricing_comparison.csv").flatten()),
  caption: [Comparison of optimal prices and royalties obtained using SLSQP and Trust-Region Constrained methods for multi-format royalty-constrained pricing.],
)

The results validate that our optimization framework yields price structures that are logically consistent, economically justified, and equitably aligned across publishing platforms.
By assigning more affordable prices to higher-royalty platforms, the model simultaneously promotes reader accessibility and ensures author sustainability. This approach offers a transparent, data-driven methodology for principled price determination under practical royalty constraints. Ultimately, the computed values establish the minimum set prices to be adopted for MoKa Reads Collective’s forthcoming publications.

= Conclusion

// In this paper, we developed and applied a pricing optimization framework tailored to the needs of mission-driven, independent publishing initiatives such as the MoKa Reads Collective.
// Grounded in the principle of “spend the least to support the most,” our model balances the dual objectives of affordability for readers and fair compensation for authors by integrating
// platform-specific royalty constraints into a nonlinear optimization problem.

// Through empirical market analysis, we established realistic pricing boundaries based on ebook page counts and demonstrated how price-per-page insights can inform initial price bounds.
// The optimization model itself—formulated over normalized price variables and incorporating monotonicity constraints—was solved using robust, gradient-based methods (SLSQP and trust-region
// constrained algorithms), which consistently converged to economically meaningful and structurally coherent solutions.

// Our results validate the effectiveness of this model in producing pricing strategies that are logically ordered, reward high-royalty platforms with greater affordability, and remain flexible
// across various publishing formats. The computed minimum set prices provide a principled foundation for future publication pricing by the MoKa Reads Collective, ensuring accessibility without
// compromising financial sustainability.

// By uniting data analysis, optimization theory, and publishing economics, this framework contributes a replicable and transparent method for socially-conscious pricing strategy in digital and print publishing.
This paper presented a principled pricing optimization framework designed to balance reader affordability with author compensation under platform-specific royalty constraints. Grounded in the mission of the MoKa Reads Collective, our model uses nonlinear optimization with monotonicity and royalty-based constraints to generate fair, data-driven prices across multiple formats.

Using SLSQP and trust-region methods, we demonstrated that the model consistently produces logically ordered and economically aligned prices, rewarding high-royalty platforms with greater affordability. The resulting minimum set prices offer a transparent and sustainable foundation for future MoKa Reads publications.
#pagebreak()

#heading(depth: 1, [Appendix], numbering: none)

#heading(depth: 2, [A. Pseudo-Code], numbering: none)

#rect(
  stroke: 1pt + black,
  outset: 10pt,
  ```
  Inputs:
      n          ← number of publishing formats
      r[1..n]    ← royalty rates per format
      p_min      ← global minimum price
      p_max      ← global maximum price
      λ_p        ← price penalty weight
      δ          ← minimum price spacing (normalized)
      ε          ← minimum royalty-per-unit spacing

  Initialize:
      For each format i = 1 to n:
          Assign normalized price variable x_i ∈ [0, 1]
          Set initial guess x_i^(0) ← rank(r_i) / (R - 1)

  Define:
      p_i(x_i)     ← p_min + x_i * (p_max - p_min)
      objective(x_i) ← ( -∑ r_i * p_i(x_i) + λ_p * (∑ p_i(x_i))^2 ) / n

  Subject to constraints:
    For i = 1 to n - 1:
      x_{i+1} - x_i ≥ δ                                [Price ordering]
      r_i * p_i(x_i) ≥ r_{i+1} * p_{i+1}(x_{i+1}) + ε  [Royalty ordering]
      For all i:
          0 ≤ x_i ≤ 1                                  [Normalized bounds]

  Solve:
    Use a constrained optimization algorithm (e.g., SLSQP or Trust-Region Constrained) to find x* = argmin objective(x) subject to constraints

  Output:
      For each i:
          Price:   p_i = p_min + x_i * (p_max - p_min)
          Royalty: r_i * p_i
      Report:
          Total Price   = ∑ p_i
          Total Royalty = ∑ r_i * p_i
  ```,
)

#pagebreak()
