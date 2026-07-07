const PLATFORM_PATTERNS = [
  ["youtube", /(^|\.)youtube\.com$|(^|\.)youtu\.be$/i],
  ["x", /(^|\.)x\.com$|(^|\.)twitter\.com$/i],
  ["reddit", /(^|\.)reddit\.com$/i],
  ["tiktok", /(^|\.)tiktok\.com$/i],
  ["linkedin", /(^|\.)linkedin\.com$/i]
];

function parseUrl(url) {
  try {
    return new URL(url);
  } catch {
    return null;
  }
}

export function detectPlatform(url, platformHint = "") {
  if (platformHint) return String(platformHint).trim().toLowerCase();
  const parsed = parseUrl(url);
  if (!parsed) return "unknown";
  const host = parsed.hostname.replace(/^www\./, "");
  const match = PLATFORM_PATTERNS.find(([, pattern]) => pattern.test(host));
  return match ? match[0] : "web";
}

export async function extractMetadata(input = {}) {
  const url = typeof input.url === "string" ? input.url.trim() : "";
  const parsed = parseUrl(url);

  if (!parsed) {
    return {
      ok: false,
      error: { code: "INVALID_INPUT", message: "url must be a valid absolute URL." }
    };
  }

  return {
    ok: true,
    output: {
      status: "metadata_record_created",
      source_record: {
        original_url: url,
        canonical_url: parsed.toString(),
        captured_at: new Date().toISOString()
      },
      platform: detectPlatform(url, input.platform_hint),
      canonical_url: parsed.toString(),
      title: null,
      author: null,
      description: null,
      thumbnail: null,
      published_at: null,
      duration_seconds: null,
      visible_captions_status: "not_checked",
      proof_label: "METADATA_ONLY",
      extraction_limits: [
        "This first MCP implementation normalizes and records source metadata without fetching remote page contents.",
        "Use a transcript provider, user-supplied transcript, or future media connector to upgrade this record."
      ]
    }
  };
}
