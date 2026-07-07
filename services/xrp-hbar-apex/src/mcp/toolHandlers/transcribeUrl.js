import { detectPlatform } from "./extractMetadata.js";

function isEnabled(value) {
  return String(value || "").trim().toLowerCase() === "true";
}

function hasValue(value) {
  return typeof value === "string" && value.trim().length > 0;
}

function videoCapability(env = process.env) {
  const providers = {
    openai: hasValue(env.OPENAI_API_KEY),
    deepgram: hasValue(env.DEEPGRAM_API_KEY),
    assemblyai: hasValue(env.ASSEMBLYAI_API_KEY),
    revai: hasValue(env.REVAI_API_KEY)
  };
  const providerConfigured = Object.values(providers).some(Boolean);
  return {
    mode: env.VIDEO_TRANSCRIPTION_MODE || "metadata_first",
    caption_first_enabled: isEnabled(env.ENABLE_CAPTION_EXTRACTION),
    ytdlp_enabled: isEnabled(env.ENABLE_YTDLP_EXTRACTION),
    local_ffmpeg_enabled: isEnabled(env.ENABLE_LOCAL_FFMPEG_TRANSCRIPTION),
    frame_ocr_enabled: isEnabled(env.ENABLE_VIDEO_FRAME_OCR),
    diarization_enabled: isEnabled(env.ENABLE_SPEAKER_DIARIZATION),
    provider_fallback_enabled: isEnabled(env.ENABLE_PROVIDER_TRANSCRIPTION),
    provider_configured: providerConfigured,
    providers,
    storage_mode: env.TRANSCRIPT_STORAGE_MODE || "memory_only",
    evidence_pack_enabled: isEnabled(env.ENABLE_TRANSCRIPT_EVIDENCE_PACK"),
    proof_label: providerConfigured || isEnabled(env.ENABLE_CAPTION_EXTRACTION) || isEnabled(env.ENABLE_LOCAL_FFMPEG_TRANSCRIPTION)
      ? "TRANSCRIPTION_PATH_CONFIGURED_NEEDS_LIVE_SMOKE"
      : "METADATA_ONLY_TRANSCRIPTION_NOT_CONFIGURED"
  };
}

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

  const capability = videoCapability();

  return {
    ok: true,
    output: {
      status: capability.proof_label === "TRANSCRIPTION_PATH_CONFIGURED_NEEDS_LIVE_SMOKE"
        ? "video_intake_ready_for_transcription_smoke"
        : "metadata_only",
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
      transcript_source: "not_generated_by_this_metadata_first_handler",
      ocr_text: null,
      metadata: {
        platform_hint: input.platform_hint || null,
        language_hint: input.language_hint || null,
        ocr_enabled: Boolean(input.ocr_enabled),
        speaker_diarization: Boolean(input.speaker_diarization)
      },
      video_transcription_capability: capability,
      proof_label: capability.proof_label,
      limitations: [
        "This MCP handler records URL intake and reports configured transcription paths; it does not yet fetch media or generate a transcript by itself.",
        "Claim live transcription only after caption/local/provider extraction is implemented and a route-level smoke test returns transcript_text with source and hash metadata."
      ],
      recommended_next_steps: [
        "Use reprocess_transcript with supplied transcript text now.",
        "Enable caption extraction, local FFmpeg/Whisper, or a paid STT provider in Railway only after credentials and cost limits are set.",
        "Run a live transcribe_url smoke test and verify transcript hash, source URL, platform, capture time, and proof label before upgrading capability status."
      ]
    }
  };
}
