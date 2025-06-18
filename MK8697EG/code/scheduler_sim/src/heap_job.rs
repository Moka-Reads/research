use crate::Job;
use std::cmp::Ordering;

pub struct HeapJob(pub Job);

impl PartialEq for HeapJob {
    fn eq(&self, other: &Self) -> bool {
        self.0.remaining_time == other.0.remaining_time
    }
}

impl Eq for HeapJob {}

impl PartialOrd for HeapJob {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        // Reverse for min-heap
        other.0.remaining_time.partial_cmp(&self.0.remaining_time)
    }
}

impl Ord for HeapJob {
    fn cmp(&self, other: &Self) -> Ordering {
        self.partial_cmp(other).unwrap()
    }
}
