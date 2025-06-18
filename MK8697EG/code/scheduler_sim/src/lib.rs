use rand::rng;
use rand_distr::{Distribution, Exp};
use std::fmt;

pub mod fcfs;
pub mod heap_job;
pub mod mlfq;
pub mod pri;
pub mod rr;
pub mod sjf;
pub mod srpt;

pub use fcfs::FCFSScheduler;

#[derive(Debug, Clone)]
pub struct Job {
    pub id: usize,
    pub arrival_time: f64,
    pub service_time: f64,
    pub remaining_time: f64,
    pub start_time: Option<f64>,
    pub finish_time: Option<f64>,
    pub priority: usize,
}

pub trait Scheduler {
    fn add_job(&mut self, job: Job);
    fn tick(&mut self, current_time: f64) -> Option<Job>;
    fn is_idle(&self) -> bool;
}

pub fn simulate<S: Scheduler>(scheduler: &mut S, jobs: &mut [Job], name: &str) -> Metrics {
    let mut time = 0.0;
    let mut i = 0;
    let mut completed = Vec::new();

    while i < jobs.len() || !scheduler.is_idle() {
        while i < jobs.len() && jobs[i].arrival_time <= time {
            scheduler.add_job(jobs[i].clone());
            i += 1;
        }

        if let Some(job) = scheduler.tick(time) {
            completed.push(job);
        }

        time += 0.01;
    }

    let n = completed.len() as f64;
    let mut total_wait = 0.0;
    let mut total_turnaround = 0.0;
    let mut total_service = 0.0;

    let mut wait_times = Vec::new();
    let mut turnaround_times = Vec::new();
    let mut response_ratios = Vec::new();

    for job in &completed {
        let wait = job.start_time.unwrap() - job.arrival_time;
        let turnaround = job.finish_time.unwrap() - job.arrival_time;

        wait_times.push(wait);
        turnaround_times.push(turnaround);
        response_ratios.push(turnaround / job.service_time);

        total_wait += wait;
        total_turnaround += turnaround;
        total_service += job.service_time;
    }

    let starvation_threshold = 5.0;
    let starved_jobs = wait_times
        .iter()
        .filter(|&&w| w > starvation_threshold)
        .count();
    let starvation_rate = starved_jobs as f64 / n;

    let max_wait = wait_times.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
    let fairness = jains_index(&wait_times);
    let avg_response_ratio = response_ratios.iter().sum::<f64>() / n;

    Metrics {
        name: name.to_string(),
        mean_wait: total_wait / n,
        mean_turnaround: total_turnaround / n,
        utilization: 100.0 * total_service / time,
        throughput: n / time,
        starvation_rate,
        max_wait,
        fairness_index: fairness,
        avg_response_ratio,
    }
}

fn jains_index(xs: &[f64]) -> f64 {
    let sum: f64 = xs.iter().sum();
    let sum_sq: f64 = xs.iter().map(|x| x * x).sum();
    let n = xs.len() as f64;
    if sum_sq == 0.0 {
        return 1.0;
    }
    (sum * sum) / (n * sum_sq)
}

pub fn generate_jobs(n: usize, lambda: f64, mu: f64) -> Vec<Job> {
    let mut rng = rng();
    let arrival = Exp::new(lambda).unwrap();
    let service = Exp::new(mu).unwrap();

    let mut jobs = Vec::new();
    let mut current_time = 0.0;

    for i in 0..n {
        current_time += arrival.sample(&mut rng);
        let service_time = service.sample(&mut rng);
        jobs.push(Job {
            id: i,
            arrival_time: current_time,
            service_time,
            remaining_time: service_time,
            start_time: None,
            finish_time: None,
            priority: (rand::random::<u64>() % 3) as usize,
        });
    }

    jobs
}

#[derive(Debug)]
pub struct Metrics {
    pub name: String,
    pub mean_wait: f64,
    pub mean_turnaround: f64,
    pub utilization: f64,
    pub throughput: f64,
    pub starvation_rate: f64,
    pub max_wait: f64,
    pub fairness_index: f64,
    pub avg_response_ratio: f64,
}

impl fmt::Display for Metrics {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(
            f,
            "{},{:.4},{:.4},{:.2},{:.4},{:.4},{:.4},{:.4},{:.4}",
            self.name,
            self.mean_wait,
            self.mean_turnaround,
            self.utilization,
            self.throughput,
            self.starvation_rate,
            self.max_wait,
            self.fairness_index,
            self.avg_response_ratio,
        )
    }
}
