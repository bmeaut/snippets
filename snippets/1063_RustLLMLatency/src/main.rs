mod gemini;
mod stats;
mod types;

use clap::Parser;
use reqwest::Client;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use types::RunResult;

/// Rust benchmark: méri egy prompt Gemini API-n (ingyenes, Google AI Studio
/// kulcsos) keresztüli válaszidejét (TTFT és teljes idő), streaming és
/// nem-streaming módban.
#[derive(Parser, Debug)]
struct Args {
    /// stream | nonstream | both
    #[arg(long, default_value = "both")]
    mode: String,

    /// Free tier modellnév (ellenőrizd: ai.google.dev/gemini-api/docs/models)
    #[arg(long, default_value = "gemini-3.5-flash-lite")]
    model: String,

    #[arg(long, default_value_t = 10)]
    iterations: u32,

    /// A gemini-3.8-flash "gondolkodó" (thinking) modell, a láthatatlan
    /// gondolkodási tokenek is ebbe a keretbe számítanak be, ezért ne legyen
    /// túl alacsony, különben a válasz MAX_TOKENS-nél csonkolva érkezik.
    #[arg(long, default_value_t = 1024)]
    max_tokens: u32,

    /// Szünet (ms) két hívás között. A gemini-3.8-flash free tier kvótája
    /// mindössze 5 kérés/perc (a válasz fejlécéből derült ki), ezért az
    /// alapérték 13000 ms (~4.6 RPM, biztonsági ráhagyással).
    #[arg(long, default_value_t = 13000)]
    delay_ms: u64,

    #[arg(
        long,
        default_value = "Írj egy rövid, 3 mondatos összefoglalót arról, miért fontos a szoftverek tesztelése."
    )]
    prompt: String,

    #[arg(long, default_value = "results.csv")]
    output: String,
}

fn now_ms() -> u128 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_millis()
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    dotenvy::dotenv().ok();
    let args = Args::parse();

    let modes: Vec<bool> = match args.mode.as_str() {
        "stream" => vec![true],
        "nonstream" => vec![false],
        "both" => vec![false, true],
        other => anyhow::bail!("Ismeretlen --mode: {other} (stream|nonstream|both)"),
    };

    let api_key = std::env::var("GEMINI_API_KEY")
        .map_err(|_| anyhow::anyhow!("Hiányzik a GEMINI_API_KEY (.env)"))?;

    let client = Client::builder().timeout(Duration::from_secs(120)).build()?;

    let mut all_results: Vec<RunResult> = Vec::new();

    for &stream in &modes {
        let mode_label = if stream { "stream" } else { "nonstream" };
        println!(
            "\n== gemini / {} / {} ({} iteráció) ==",
            args.model, mode_label, args.iterations
        );

        let mut totals: Vec<f64> = Vec::new();
        let mut ttfts: Vec<f64> = Vec::new();
        let mut errors = 0u32;

        for i in 0..args.iterations {
            let outcome =
                gemini::call(&client, &api_key, &args.model, &args.prompt, args.max_tokens, stream)
                    .await;

            let row = match outcome {
                Ok(o) => {
                    totals.push(o.total_ms);
                    if let Some(t) = o.ttft_ms {
                        ttfts.push(t);
                    }
                    println!(
                        "  [{:>3}] total={:>7.1} ms  ttft={}",
                        i + 1,
                        o.total_ms,
                        o.ttft_ms
                            .map(|t| format!("{:.1} ms", t))
                            .unwrap_or_else(|| "-".to_string())
                    );
                    RunResult {
                        timestamp_ms: now_ms(),
                        provider: "gemini".to_string(),
                        model: args.model.clone(),
                        mode: mode_label.to_string(),
                        iteration: i + 1,
                        status: "ok".to_string(),
                        ttft_ms: o.ttft_ms,
                        total_ms: Some(o.total_ms),
                        input_tokens: o.input_tokens,
                        output_tokens: o.output_tokens,
                        error: None,
                    }
                }
                Err(e) => {
                    errors += 1;
                    println!("  [{:>3}] HIBA: {}", i + 1, e);
                    RunResult {
                        timestamp_ms: now_ms(),
                        provider: "gemini".to_string(),
                        model: args.model.clone(),
                        mode: mode_label.to_string(),
                        iteration: i + 1,
                        status: "error".to_string(),
                        ttft_ms: None,
                        total_ms: None,
                        input_tokens: None,
                        output_tokens: None,
                        error: Some(e.to_string()),
                    }
                }
            };
            all_results.push(row);

            if args.delay_ms > 0 {
                tokio::time::sleep(Duration::from_millis(args.delay_ms)).await;
            }
        }

        if let Some(s) = stats::summarize(&totals) {
            println!(
                "  -> total_ms: n={} mean={:.1} median={:.1} p95={:.1} min={:.1} max={:.1} stddev={:.1}",
                s.n, s.mean, s.median, s.p95, s.min, s.max, s.stddev
            );
        }
        if let Some(s) = stats::summarize(&ttfts) {
            println!(
                "  -> ttft_ms:  n={} mean={:.1} median={:.1} p95={:.1} min={:.1} max={:.1} stddev={:.1}",
                s.n, s.mean, s.median, s.p95, s.min, s.max, s.stddev
            );
        }
        if errors > 0 {
            println!("  -> hibák száma: {errors}");
        }
    }

    let mut wtr = csv::Writer::from_path(&args.output)?;
    for row in &all_results {
        wtr.serialize(row)?;
    }
    wtr.flush()?;
    println!("\nNyers eredmények kiírva: {}", args.output);

    Ok(())
}
