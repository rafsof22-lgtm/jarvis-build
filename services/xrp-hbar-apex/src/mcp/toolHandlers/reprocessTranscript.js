const XRP_HBAR_TERMS = /\b(XRP|XRPL|Ripple|RLUSD|HBAR|Hedera|Hidden Road|Ripple Prime|Bitnomial|collateral|settlement|tokenization|stablecoin|RWA|ETF|custody)\b/i;

function splitSentences(text) {
  return text
    .split(/(?<=[.!?])\s+|\n+/)
    .map((item) => item.trim())
    .filter(Boolean);
}

export async function reprocessTranscript(input = {}) {
  const transcriptText = typeof input.transcript_text === "string" ? input.transcript_text.trim() : "";
  if (!transcriptText) {
    return {
      ok: false,
      error: { code: "INVALID_INPUT", message: "transcript_text is required." }
    };
  }

  const claimCandidates = splitSentences(transcriptText)
    .filter((sentence) => XRP_HBAR_TERMS.test(sentence))
    .slice(0, 25)
    .map((claim, index) => ({
      id: `claim_${index + 1}`,
      text: claim,
      evidence_level: "UNVERIFIED_TRANSCRIPT_CLAIM",
      recommended_action: "Verify against official, filing, on-chain, or primary-source evidence before upgrading."
    }));

  return {
    ok: true,
    output: {
      status: "processed",
      source_record: {
        source_url: input.source_url || null,
        source_title: input.source_title || null,
        captured_at: new Date().toISOString()
      },
      transcript_length_chars: transcriptText.length,
      claim_candidates: claimCandidates,
      proof_label: claimCandidates.length > 0 ? "TRANSCRIPT_LEAD_ONLY" : "NO_XRP_HBAR_CLAIMS_FOUND",
      limitations: [
        "Transcript text is treated as a lead, not proof.",
        "Claims require official, filing, on-chain, or other primary-source verification before tracker upgrade."
      ],
      recommended_next_steps: [
        "Run official-source verification for each material claim.",
        "Route verified claims into XRP-direct, XRPL-direct, RLUSD-direct, Ripple-corporate, HBAR-related, competitor-related, or indirect buckets."
      ]
    }
  };
}
