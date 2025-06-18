use crate::{Job, Scheduler, heap_job::HeapJob};
use std::collections::BinaryHeap;

pub struct PRI {
    queue: BinaryHeap<HeapJob>,
    current: Option<Job>,
}

impl PRI {
    pub fn new() -> Self {
        Self {
            queue: BinaryHeap::new(),
            current: None,
        }
    }
}

impl Scheduler for PRI {
    fn add_job(&mut self, job: Job) {
        self.queue.push(HeapJob(job));
    }

    fn tick(&mut self, current_time: f64) -> Option<Job> {
        if self.current.is_none() {
            if let Some(HeapJob(mut job)) = self.queue.pop() {
                job.start_time = Some(current_time);
                self.current = Some(job);
            }
        }

        if let Some(job) = &mut self.current {
            job.remaining_time -= 0.01;
            if job.remaining_time <= 0.0 {
                let mut finished = self.current.take().unwrap();
                finished.finish_time = Some(current_time);
                return Some(finished);
            }
        }

        None
    }

    fn is_idle(&self) -> bool {
        self.current.is_none() && self.queue.is_empty()
    }
}
