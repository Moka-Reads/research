use crate::{Job, Scheduler};
use std::collections::VecDeque;

pub struct FCFSScheduler {
    queue: VecDeque<Job>,
    current_job: Option<Job>,
}

impl FCFSScheduler {
    pub fn new() -> Self {
        Self {
            queue: VecDeque::new(),
            current_job: None,
        }
    }
}

impl Scheduler for FCFSScheduler {
    fn add_job(&mut self, job: Job) {
        self.queue.push_back(job);
    }

    fn tick(&mut self, current_time: f64) -> Option<Job> {
        if self.current_job.is_none() {
            if let Some(mut job) = self.queue.pop_front() {
                job.start_time = Some(current_time);
                self.current_job = Some(job);
            }
        }

        if let Some(job) = &mut self.current_job {
            job.remaining_time -= 0.01;
            if job.remaining_time <= 0.0 {
                let mut finished = self.current_job.take().unwrap();
                finished.finish_time = Some(current_time);
                return Some(finished);
            }
        }

        None
    }

    fn is_idle(&self) -> bool {
        self.current_job.is_none() && self.queue.is_empty()
    }
}
