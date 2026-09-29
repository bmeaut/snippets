use anyhow::{bail, Result};
use futures_util::StreamExt;
use reqwest::Client;
use serde_json::{json, Value};
use std::time::Instant;

use crate::types::CallOutcome;

pub async fn call(
    client: &Client,
    api_key: &str,
    model: &str,
    prompt: &str,
    max_tokens: u32,
    stream: bool,
) -> Result<CallOutcome> {
    let start = Instant::now();
    let body = json!({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": max_tokens},
    });

    let url = if stream {
        format!(
            "https://generativelanguage.googleapis.com/v1beta/models/{}:streamGenerateContent?alt=sse&key={}",
            model, api_key
        )
    } else {
        format!(
            "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent?key={}",
            model, api_key
        )
    };

    let resp = client.post(&url).json(&body).send().await?;
    let status = resp.status();
    if !status.is_success() {
        let text = resp.text().await.unwrap_or_default();
        bail!("Gemini API error {}: {}", status, text);
    }

    if !stream {
        let v: Value = resp.json().await?;
        let total_ms = start.elapsed().as_secs_f64() * 1000.0;
        return Ok(CallOutcome {
            ttft_ms: None,
            total_ms,
            input_tokens: v
                .pointer("/usageMetadata/promptTokenCount")
                .and_then(|x| x.as_u64()),
            output_tokens: v
                .pointer("/usageMetadata/candidatesTokenCount")
                .and_then(|x| x.as_u64()),
        });
    }

    let mut ttft_ms: Option<f64> = None;
    let mut input_tokens: Option<u64> = None;
    let mut output_tokens: Option<u64> = None;
    let mut buf = String::new();
    let mut body_stream = resp.bytes_stream();

    while let Some(chunk) = body_stream.next().await {
        let chunk = chunk?;
        buf.push_str(&String::from_utf8_lossy(&chunk));

        // A Gemini SSE stream eseményeket "\r\n\r\n"-nel zárja (nem csak "\n\n"-nel).
        while let Some(pos) = buf.find("\r\n\r\n").or_else(|| buf.find("\n\n")) {
            let sep_len = if buf[pos..].starts_with("\r\n\r\n") { 4 } else { 2 };
            let event = buf[..pos].to_string();
            buf.drain(..pos + sep_len);

            for line in event.lines() {
                let Some(data) = line.strip_prefix("data: ") else {
                    continue;
                };
                let Ok(v) = serde_json::from_str::<Value>(data) else {
                    continue;
                };

                let has_text = v
                    .pointer("/candidates/0/content/parts/0/text")
                    .and_then(|x| x.as_str())
                    .map(|s| !s.is_empty())
                    .unwrap_or(false);
                if has_text && ttft_ms.is_none() {
                    ttft_ms = Some(start.elapsed().as_secs_f64() * 1000.0);
                }

                if let Some(u) = v.get("usageMetadata") {
                    input_tokens = u.get("promptTokenCount").and_then(|x| x.as_u64());
                    output_tokens = u.get("candidatesTokenCount").and_then(|x| x.as_u64());
                }
            }
        }
    }

    let total_ms = start.elapsed().as_secs_f64() * 1000.0;
    Ok(CallOutcome {
        ttft_ms,
        total_ms,
        input_tokens,
        output_tokens,
    })
}
