import { detectPlatform } from "./extractMetadata.js";

export async function transcribeUrl(input = {}) {
  const url = typeof input.url === "string" ? input.url.trim() : "";
  let parsed;
  try {
    parsed = new URL(url);
  } catch {
    return {
      ok: false,
      error: { code: "INVALID_INPUT", message: "url must be a valid absolute URL." }
    };
  }

  return {
    ok: true,
    output: {
      status: "metadata_only",
      source_record: {
        original_url: url,
        canonical_url: parsed.toString(),
        captured_at: new Date().toISOString()
      },
      platform: detectPlatform(url, input.platform_hint),
      canonical_url: parsed.toString(),
      title: null,
      author: null,
      published_at: null,
      duration_seconds: null,
      transcript_text: null,
      transcript_source: "not_configured",
      ocr_text: null,
      metadata: {
        platform_hint: input.platform_hint || null,
        language_hint: input.language_hint || null,
        ocr_enabled: Boolean(input.ocr_enabled),
        speaker_diarization: Boolean(input.speaker_diarization)
      },
      proof_label: "METADATA_ONLY",
      limitations: [
        "Transcript extraction is not wired to a provider in this first MCP service version.",
        "No transcript text should be inferred from this response."
      ],
      recommended_next_steps: [
        "Provide transcript_text to reprocess_transcript or connect a transcript provider.",
        "Use extract_metadata for metadata-only source intake."
      ]
    }
  };
}
