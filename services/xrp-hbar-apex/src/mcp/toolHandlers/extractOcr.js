export async function extractOcr(input = {}) {
  const imageRef = input.image_url || input.file_id;
  if (!imageRef || typeof imageRef !== "string") {
    return {
      ok: false,
      error: { code: "INVALID_INPUT", message: "image_url or file_id is required." }
    };
  }

  return {
    ok: true,
    output: {
      status: "ocr_intake_recorded",
      source_record: { image_ref: imageRef, captured_at: new Date().toISOString() },
      ocr_text: null,
      proof_label: "OCR_PROVIDER_NOT_CONFIGURED",
      limitations: [
        "OCR provider access is not configured in this first MCP service version.",
        "No visible text should be inferred from this response."
      ],
      recommended_next_steps: ["Connect OCR_PROVIDER_API_KEY or supply extracted text for reprocess_transcript."]
    }
  };
}
