pub struct Summary {
    pub n: usize,
    pub mean: f64,
    pub median: f64,
    pub p95: f64,
    pub min: f64,
    pub max: f64,
    pub stddev: f64,
}

pub fn summarize(values: &[f64]) -> Option<Summary> {
    if values.is_empty() {
        return None;
    }
    let mut sorted: Vec<f64> = values.to_vec();
    sorted.sort_by(|a, b| a.partial_cmp(b).unwrap());

    let n = sorted.len();
    let mean = sorted.iter().sum::<f64>() / n as f64;
    let variance = sorted.iter().map(|v| (v - mean).powi(2)).sum::<f64>() / n as f64;

    Some(Summary {
        n,
        mean,
        median: percentile(&sorted, 50.0),
        p95: percentile(&sorted, 95.0),
        min: sorted[0],
        max: sorted[n - 1],
        stddev: variance.sqrt(),
    })
}

fn percentile(sorted: &[f64], p: f64) -> f64 {
    let n = sorted.len();
    if n == 1 {
        return sorted[0];
    }
    let rank = (p / 100.0) * (n as f64 - 1.0);
    let lo = rank.floor() as usize;
    let hi = rank.ceil() as usize;
    if lo == hi {
        sorted[lo]
    } else {
        let frac = rank - lo as f64;
        sorted[lo] + (sorted[hi] - sorted[lo]) * frac
    }
}
