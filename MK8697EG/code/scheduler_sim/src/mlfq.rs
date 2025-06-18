use crate::{Job, Scheduler};
use std::collections::VecDeque;

pub struct MLFQ {
    queues: Vec<VecDeque<Job>>,
    time_slices: Vec<f64>,
    current: Option<Job>,
    current_level: usize,
    time_slice: f64,
}

impl MLFQ {
    pub fn new() -> Self {
        Self {
            queues: vec![VecDeque::new(), VecDeque::new(), VecDeque::new()],
            time_slices: vec![0.05, 0.1, 0.2],
            current: None,
            current_level: 0,
            time_slice: 0.0,
        }
    }
}

impl Scheduler for MLFQ {
    fn add_job(&mut self, job: Job) {
        self.queues[0].push_back(job); // All jobs start at highest level
    }

    fn tick(&mut self, current_time: f64) -> Option<Job> {
        if self.current.is_none() {
            for (i, queue) in self.queues.iter_mut().enumerate() {
                if let Some(job) = queue.pop_front() {
                    self.current = Some(job);
                    self.current_level = i;
                    self.time_slice = 0.0;
                    break;
                }
            }

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

            if self.time_slice >= self.time_slices[self.current_level] {
                let  demoted = self.current.take().unwrap();
                let next_level = (self.current_level + 1).min(self.queues.len() - 1);
                self.queues[next_level].push_back(demoted);
            }
        }

        None
    }

    fn is_idle(&self) -> bool {
        self.current.is_none() && self.queues.iter().all(|q| q.is_empty())
    }
}