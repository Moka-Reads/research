use crate::{Job, Scheduler};
use std::collections::VecDeque;

pub struct RR {
    queue: VecDeque<Job>,
    current: Option<Job>,
    quantum: f64,
    time_slice: f64,
}

impl RR {
    pub fn new(quantum: f64) -> Self {
        Self {
            queue: VecDeque::new(),
            current: None,
            quantum,
            time_slice: 0.0,
        }
    }
}

impl Scheduler for RR {
    fn add_job(&mut self, job: Job) {
        self.queue.push_back(job);
    }

    fn tick(&mut self, current_time: f64) -> Option<Job> {
        if self.current.is_none() {
            self.current = self.queue.pop_front();
            self.time_slice = 0.0;

            if let Some(job) = &mut self.current {
                if job.start_time.is_none() {
                    job.start_time = Some(current_time);
                }
            }
        }

        if let Some(job) = &mut self.current {
            job.remaining_time -= 0.01;
            self.time_slice += 0.01;

            if job.remaining_time <= 0.0 {
                let mut finished = self.current.take().unwrap();
                finished.finish_time = Some(current_time);
                return Some(finished);
            }

            if self.time_slice >= self.quantum {
                let job = self.current.take().unwrap();
                self.queue.push_back(job);
            }
        }

        None
    }

    fn is_idle(&self) -> bool {
        self.current.is_none() && self.queue.is_empty()
    }
}
