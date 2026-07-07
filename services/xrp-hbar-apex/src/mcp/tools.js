import { extractMetadata } from "./toolHandlers/extractMetadata.js";
import { extractOcr } from "./toolHandlers/extractOcr.js";
import { reprocessTranscript } from "./toolHandlers/reprocessTranscript.js";
import { transcribeFile } from "./toolHandlers/transcribeFile.js";
import { transcribeUrl } from "./toolHandlers/transcribeUrl.js";

export const tools = [
  {
    name: "transcribe_url",
    description: "Record a media URL and return metadata-first transcript limitations when extraction is not configured.",
    requiredInput: ["url"],
    handler: transcribeUrl
  },
  {
    name: "transcribe_file",
    description: "Record a file reference and return honest transcription limitations when file providers are not configured.",
    requiredInput: ["file_url or file_id"],
    handler: transcribeFile
  },
  {
    name: "extract_metadata",
    description: "Normalize source URL metadata for later XRP/HBAR evidence review.",
    requiredInput: ["url"],
    handler: extractMetadata
  },
  {
    name: "extract_ocr",
    description: "Record an OCR intake request and return honest provider limitations when OCR is not configured.",
    requiredInput: ["image_url or file_id"],
    handler: extractOcr
  },
  {
    name: "reprocess_transcript",
    description: "Turn supplied transcript text into XRP/HBAR claim candidates for proof-gated review.",
    requiredInput: ["transcript_text"],
    handler: reprocessTranscript
  }
];

export function publicTools() {
  return tools.map(({ name, description, requiredInput }) => ({
    name,
    description,
    required_input: requiredInput
  }));
}

export function findTool(name) {
  return tools.find((tool) => tool.name === name);
}
