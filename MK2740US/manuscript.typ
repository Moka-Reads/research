#import "@preview/unequivocal-ams:0.1.2": ams-article, theorem, proof
#show par: set par(spacing: 2em)

#let title = [Strategic Pricing for Multi-Platform Digital Publishing: A Penalty-Reward Optimization Approach]
#show: ams-article.with(
  title: title,
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
  abstract: "",
  bibliography: bibliography("refs.bib", full: true),
)

#set math.equation(numbering: "(1)")

// In this paper we will be exploring a nonlinear optimization problem to determine the best prices for a publication given
// various distribution formats and producers. The method we use to determine the best price is by using a royalty constraint with
// the main premise being able to "spend the least to support the most", this slogan is directly tied to the collective's interest as
// a not-for-profit organization to sell publications not for pure profit, but in a affordable, accessible way that enables readers and
// our interest to being able to support ourselves aligned.

// We will firstly discuss about the market, having a look at different books, their prices, page counts and trying to build a relationship with it,
// thereafter, we can start looking at our problem formulation, ways to approach it, and lastly we will look at results for determining the optimal prices
// for publications in the MoKa Reads Collective or a minimum set price.

In this paper we develop an optimization model for determining optimal pricing strategies across heterogeneous digital publishing platforms. The methadology
we bring into our model is to maximize revenue across all platforms, however we also explicitly incorporate affordability constraints as well. This balance is
particularly relevent for not-for-profit organizations who operate under the principle of maximizing readers support while minimizing financial barriers.

Our approach to this involves employing a penalty-reward model 

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

As illustrated in #ref(<price_vs_pagecount>), books within the 100–400 page range clusters at the price point of approximately $\$50$.
This suggests that \$50 may serve as an upper bound for our formats.

The range chosen can additionally be supported by the 2024 Canadian Book Consumer Study #ref(<booknet2024cbc>) which found $53%$ of Canadians purchasing new books in the price range
of \$1-49.
#pagebreak()
= Optimization Problem

In the context of multi-platform publishing, determining the optimal price across these various platforms require a balance between the royalty earned per unit to the author
and the affordability of the publication to the reader, keeping in mind the convenience some platforms provide which are accounted in their market share.

Let there be $n$ publishing platforms where each are associated with a price $p_i in [p_"min", p_"max"]$,
a corresponding royalty rate $r_i in (0, 1)$, and lastly the platform's normalized market share $m_i in (0, 1)$ and $sum_(i=1)^n m_i = 1$.

To ensure consistency in our results of our model, we express each price as a normalized variable $x_i in (0, 1)$ such that:

$
p_i (x_i) = p_min + x_i (p_"max" - p_"min")
$

This formulation allows the optimization to occur over the unit interval, while still mapping to actual price values within a global price bound.

The primary objective of our problem is to maximize the total expected revenue across all platforms while maintaining a balance in affordability to the reader. The model structure
that was chosen for this situation is a Penalty-Reward model, the reward to us is the expected revenue across all platforms, but we need to penalize this term
to avoid it choosing the upper price bound.

The method to avoid this situation is to add penalizing terms, the first will ensure we avoid
the prices to vary a lot, which means our first penalty term is the variance of our prices, our second penalty term
is a squared error term to ensure the average of our prices follow a target price. Both of the penalty terms are scaled
by a tunable weight which will be denoted by $lambda_v, lambda_e$ respectively.

Our reward term $R$ which is the total expected revenue will be a sum of all the prices across each platform,
multiplied by their royalty rate and then a demand function denoted as $D_i (x_i)$. This is denoted as:

$
  R(x) = sum_(i=1)^n p_i (x_i) dot r_i dot D_i (x_i)
$

The demand function will model the platform's utility
to attract customers to the platform considering their market share and is expressed
as a logit function:

$
  D_i (x_i) &= e^(V_i) / (sum_(j=1)^n e^(V_j - max V_j)), "where" V_i = -beta_i dot p_i (x_i)
$

To consider a platform's market share with respect to the royalty rate they provide, we use our term
$beta_i in (beta_"min", beta_"max")$, which is defined similarly to $p_i$, except instead of an $x_i$ term
we have $delta_i$ which is the sum of the ratio between market share and royalty rate with weights $omega_m, omega_r$ respectively:

$
  delta_i =  omega_m m_i + omega_r r_i
$<score>

We then use @score in defining $beta_i$:
$
  beta_i = beta_"min" + delta_i (beta_"max" - beta_"min")
$

We can then define our objective function as a minimization problem, with the variance and mean of $p_i (x_i)$ denoted as $sigma^2_p$ and $mu_p$ respectively and the target price
denoted as $hat(p)$:

$
  min_(upright(x in [0, 1]^n)) quad -R(x) + lambda_v sigma^2_p (x) + lambda_e (mu_p (x) - hat(p))^2
$


#align(center)[
  *Initialization Strategy*
]

To help acheive convergence faster and add bias to the optimization towards realistic solutions, we propose a smart initialization based on the ordinal rank of the royalty rate. Let $rho(r_i)$
denote the rank of format $i$'s royalty rate among all formats, with rank $0$ being the highest. Let $U$ denote the number of unique royalty tiers, then
the initial guess for each normalized price is given by:

$
x_i^((0)) = rho(r_i)/(U-1)
$

This initialization method places formats with higher royalty rates closer to the lower bound of the price range, thus having our model bias
towards our affordability goal.
= Application of Model

To apply our model, we introduce the platforms which we will be publishing our publications in, the royalty rate they provide,
their market share according to the 2022 Canadian Ebook study #ref(<booknet2022ebooks>), and their normalized market share respectively.

#figure(
  table(
    columns: 4,
    ..csv("figures/platforms.csv").flatten()
  ), caption: "Publishing Platforms"
)

Along with these, we have parameters in our model that also need to be set, one of them being the target
price $hat(p)$ which we define from the 2024 Canadian Study #ref(<booknet2024cbc>) which states that the average price Canadians
bought new ebooks was $\$13.69$. In our application, we have also set the ratio between market share and royalty rate in @score to be _50/50_, we will also
discuss after the different effects the ratio has on the price.

#figure(
  table(
    columns: 2, rows: auto,
    [Parameter], [Value],
    $(p_"min", p_"max")$, $(\$8.99, \$49.99)$,
    $hat(p)$, $\$13.69$,
    $lambda_v, lambda_e$, $0.1$,
    $omega_r, omega_m$, $0.5$,
    $(beta_"min", beta_"max")$, $(0.8, 1.5)$,
  ), caption: "Model Parameters"
)

The algorithm we chose to solve our optimization problem is Sequential Least Squares Programming which provides
the following optimized prices for each platform:

#figure(
  table(
    columns: 3,
    ..csv("figures/prices.csv").flatten()
  ), caption: "Optimal Prices per Platform"
)

The optimal prices determined will be the prices that we will use for each platform to price our ebooks, while other formats like
paperback and hardcover aren't included, we will follow the current rule of thumb to determine their prices.

#align(center)[
  *Impact by Royalty-Market Share Ratio*
]

In our model, we use $omega_r, omega_m$ to both be $0.5$, but what if the weights were different? Consider the weight
$omega$, then we can define $delta_i = omega dot r_i + (1-omega) m_i$, with this denotion we can look at the impact
different ratios have on the model.

@price_impact illustrates the sensitivity of optimal pricing strategies across six digital publishing platforms to variations in the weighting parameter between royalty rates and market share considerations. The x-axis represents the weight ratio where 0 indicates pure market share optimization and 1 represents pure royalty rate optimization. Each line represents a different platform's optimal price response to changes in this weighting scheme. The results demonstrate that platforms with higher royalty rates (MoKa Reads, Leanpub) exhibit steeper price increases as the model shifts toward royalty-focused optimization, while platforms with lower royalty rates (Amazon) show more modest price adjustments. This heterogeneous response pattern reflects the underlying trade-off between maximizing revenue through higher-royalty platforms versus maintaining competitive positioning in high-market-share channels.

#figure(
  image("figures/price_impact_by_weight.png", width: 90%),
  caption: "Optimal Price impact by Weight Ratios"
)<price_impact>

 @revenue_vs_weight presents the relationship between the royalty-market share weighting parameter and total expected revenue across all platforms. The analysis reveals an inverted-U relationship, suggesting an optimal balance between royalty and market share considerations that maximizes total revenue. The peak occurs at approximately 0.75 weight ratio, indicating that a strategy heavily weighted toward royalty rates (but not exclusively) generates superior financial outcomes compared to either pure market share optimization or pure royalty optimization. This finding suggests that while high-royalty platforms are important for revenue maximization, completely ignoring market share dynamics leads to suboptimal results due to reduced overall market penetration.

#figure(
  image("figures/revenue_vs_weight.png", width: 74%),
  caption: "Expected total revenue vs Weight ratio"
)<revenue_vs_weight>

@price_change displays the price deviations from the baseline 50/50 weighting scenario (equal consideration of royalty rates and market share) across different weighting strategies. The baseline represents the current balanced approach, with positive values indicating price increases and negative values indicating price decreases relative to this reference point. The analysis shows that shifting toward pure market share optimization (weight ratio 0) generally reduces prices across most platforms, while moving toward pure royalty optimization (weight ratio 1) increases prices, particularly for high-royalty platforms like MoKa Reads and Leanpub. This visualization helps quantify the magnitude of pricing adjustments required when adopting different strategic orientations.

#figure(
  image("figures/price_change_from_current.png"),
  caption: "Price change from 50/50 Mix"
)<price_change>

@input_data provides the foundational data context for the optimization analysis, displaying the royalty rates and market share proportions for each of the six digital publishing platforms examined in this study. The dual-bar chart reveals the inverse relationship between these two key variables: platforms offering higher royalty rates (MoKa Reads at 92.5%, Leanpub at 80%) tend to have smaller market shares, while platforms with larger market presence (Amazon KDP at 29% market share) offer substantially lower royalty rates (35%). This fundamental trade-off between royalty generosity and market dominance drives the complex optimization dynamics explored in the pricing model, highlighting the strategic challenge publishers face when selecting platform portfolios and pricing strategies.

#figure(
  image("figures/input_data_context.png"),
  caption: "Platform Royalty and Market Shares"
)<input_data>

= Conclusion

#pagebreak()
