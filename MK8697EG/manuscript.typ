#import "@preview/unequivocal-ams:0.1.2": ams-article, theorem, proof
#show par: set par(spacing: 1.75em)
#show: ams-article.with(
  title: [Wait Your Turn: A Queue-Theoretic Foundation for Processor Scheduling],
  authors: (
    (
      name: "Mustafif Khan",
      department: [],
      organization: [MoKa Reads Collective],
      location: [],
      email: "mustafif.khan@mokareads.org",
      url: "mokareads.org"
    ),
  ),
  abstract: include "abstract.typ",
  bibliography: none,
)

#outline()

#pagebreak()
= Introduction to Queue Theory

#include "introduction.typ"

#pagebreak()
= An Empirical Analysis of Scheduler Strategies

#include "strategies.typ"

= Single vs Multicore Processor Scheduling

#include "single_vs_multi.typ"

= Conclusion

#include "conclusion.typ"
#pagebreak()
#bibliography("refs.bib")
