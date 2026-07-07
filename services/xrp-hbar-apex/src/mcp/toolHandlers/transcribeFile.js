export async function transcribeFile(input = {}) {
  const fileRef = input.file_url || input.file_id;
  if (!fileRef || typeof fileRef !== "string") {
    return {
      ok: false,
      error: { code: "INVALID_INPUT", message: "file_url or file_id is required." }
    };
  }

  return {
    ok: true,
    output: {
      status: "file_intake_recorded",
      source_record: { file_ref: fileRef, captured_at: new Date().toISOString() },
      platform: "file",
      canonical_url: input.file_url || null,
      title: input.title || null,
      author: null,
      published_at: null,
      duration_seconds: null,
      transcript_text: null,
      transcript_source: "not_configured",
      ocr_text: null,
      metadata: {},
      proof_label: "FILE_METADATA_ONLY",
      limitations: ["File download and transcription providers are not configured in this first MCP service version."],
      recommended_next_steps: [
        "Provide transcript_text to reprocess_transcript.",
        "Connect storage and transcription providers before treating file transcription as live."
      ]
    }
  };
}
