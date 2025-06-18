Queueing theory is the mathematical study of waiting lines or queues, the model is constructed so that queue lenght's and waiting time can be predicted
#ref(<palaniammalProbabilityQueueingTheory2011>).
The theory has a broad range of applications, including hospital check-up systems and call center queue management.
These systems are influenced by the duration of wait times and the associated level of customer's patience.
As such, optimizing and reducing wait times is essential for improving service quality.
This discussion will primarily focus on another application of queue theory: processor scheduling, specifically addressing how a computer's
CPU manages processes within the operating system.

== Kendall's Notation

The way that queue models are described is under Kendall's Notation which was firstly proposed in 1953
that had three factors written as *A/S/c*. Firstly, *A* denotes the time between arrivals to the queue or the arrival process which for example
can be Markovian, General, Degenerate distrubition. Secondly, *S* denotes the service time distribution which gives the distribution of time
of the service of a customer, some common ones are exponential (Markovian), deterministic (Degenerate), etc. Lastly, *c* represents the number of servers
or service channels.

Kendall's Notation has since been extended to *A/S/c/K/N/D*, where *K* is the capacity of the queue, *N* is the size of the population of jobs to be served,
and *D* is the queue discipline. When these additional three are not specified, it is assumed, $K=infinity$, $N=infinity$, $D="FIFO"$.


== Single Queue Node

A queue or queue node can be thought of as nearly a _black box_, where jobs arrive to the queue, wait some time being processed in the queue, then depart from it.
Consider @single_node which shows an arrival stream of jobs be sent to the queue system or node, which is directed to a buffer and then a system (or can be a blackbox),
then departs from the node #ref(<QueueingTheory2025>).

#figure(
  image("figures/queue_diagram.png", width: 110%),
  caption: [A Single Queue Node including a Buffer and Server]
)<single_node>

An analogy thats great to understand is a cashier in a grocery store, the customers
are waiting in line to get their items scanned, then paid, once the customer has paid and their items packed, they depart and the next customer gets processed. In this instance
each cashier processes one customer at a time, this this is a queueing node with only one server. When the cashier is really busy, and the customer will leave immediately,
is referred to as a queue with no buffer (or no waiting area), while a setting with a waiting area for upto $n$ customers is called a queue with a buffer
of size $n$ #ref(<QueueingTheory2025>).

// === Birth and Death Process
// The behaviour of a single queue can be described by a birth and death process, which describes the arrival and departures of the queue along with the number of jobs currently in the system.

// Let $k$ denote the number of jobs in the system (which are either being serviced or waiting in the queue if it has a buffer of waiting jobs) then an arrival increases
// $k$ by $1$ and a departure decreases $k$ by $1$. The system transitions between values of $k$ by "births" and "deaths" which occur at the arrival rates $lambda_i$ and
// the departure rate $mu_i$ for each job $i$.

// For a queue, these rates are generally considered not to vary with the number of jobs in the queue, so a single average rate of arrivals/departures per unit time is considered.
// Under this assumption, these process has an arrival rate of $lambda = bb(E)[lambda_1, lambda_2, ..., lambda_k]$ and departure rate of $mu = bb(E)[mu_1, mu_2, ..., mu_k]$
