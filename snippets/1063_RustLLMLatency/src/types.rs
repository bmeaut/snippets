use serde::Serialize;

#[derive(Serialize, Clone)]
pub struct RunResult {
    pub timestamp_ms: u128,
    pub provider: String,
    pub model: String,
    pub mode: String,
    pub iteration: u32,
    pub status: String,
    pub ttft_ms: Option<f64>,
    pub total_ms: Option<f64>,
    pub input_tokens: Option<u64>,
    pub output_tokens: Option<u64>,
    pub error: Option<String>,
}

pub struct CallOutcome {
    pub ttft_ms: Option<f64>,
    pub total_ms: f64,
    pub input_tokens: Option<u64>,
    pub output_tokens: Option<u64>,
}
