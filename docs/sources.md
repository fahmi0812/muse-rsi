# Lampiran C — Sumber desain (URL kanonis)

Satu sumber daftar rujukan desain muse-rsi v3.0, dengan URL kanonis
lengkap — bukan hanya judul — supaya verifikasi ulang mudah saat
sensus model bulanan atau audit CI.

**Tanggal cek:** 22 Nov 2026. Setiap URL di bawah ini dilihat langsung
lewat search dan/atau dibuka pada tanggal itu. URL yang tidak
ditemukan ditulis "tidak ditemukan" — tidak ada URL yang ditebak.
Cek ulang berikutnya: sensus model bulanan (lihat
`scripts/model_census.py`).

## Model & pengumuman resmi

| Rujukan | URL kanonis | Status | Catatan |
|---|---|---|---|
| Meta — Introducing Muse Wonder and Muse Wonder Full | https://about.fb.com/news/2026/10/introducing-muse-wonder-models/ | resmi | Dibuka; 12 Okt 2026. Active Memory / Active Focus. Halaman model: https://dev.meta.ai/models/muse-wonder |
| Google — Introducing Gemini 4 Neon | https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-neon/ | resmi | 18 Nov 2026; skor 61 Artificial Analysis Intelligence Index (xhigh) |
| OpenAI — GPT-6.2 Astra and Sol are now available | https://community.openai.com/t/gpt-6-2-astra-and-sol-are-now-available/1417531 | resmi | Forum resmi OpenAI, 17 Nov 2026 (API ID `gpt-6.2-astra`, `gpt-6.2-sol`). URL halaman openai.com-nya belum dipulihkan dari hasil search |
| GPT-6.2 Astra/Sol (sekunder) | https://www.cognativ.com/blog/gpt-6-2-astra-and-sol/ | sekunder | Ulasan Cognativ, 17 Nov 2026 |
| Google — Introducing Gemini 4 Carbon | https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-carbon/ | resmi | Dibuka; 28 Okt 2026. GA 10 Nov 2026: https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-4-carbon-now-available/ |
| Gemini 4 Carbon (sekunder) | https://www.datastudios.org/post/gemini-4-carbon-vs-gpt-6-astra-comparison | sekunder | Perbandingan datastudios.org |
| Anthropic — Introducing Claude Fable 5.2 and Claude Mythos 5.2 | https://www.anthropic.com/claude-fable-and-mythos-5-2 | resmi | Dibuka; 9 Nov 2026. Model ID `claude-fable-5-2`. Dokumen model: https://platform.claude.com/docs/en/models/fable-5-2/overview |

## Koreksi terhadap Bab 1.3 design (cek ulang 22 Nov 2026)

- **Fable 5.2 — dari "belum terverifikasi" menjadi RESMI** (pengumuman Anthropic 9 Nov 2026 ditemukan dan dibuka).
- **Gemini 4 Carbon — dari "sekunder" menjadi RESMI** (blog.google 28 Okt 2026 ditemukan dan dibuka).
- **GPT-6.2 — dari "sekunder" menjadi RESMI dengan catatan** (forum resmi OpenAI terkonfirmasi; URL openai.com belum dipulihkan).
- **Muse Wonder Full dan Gemini 4 Neon — tetap RESMI**, kini terverifikasi langsung.

Slug peran di `config/MODELS.yaml` TIDAK diganti atas dasar ini:
pergantian slug adalah kelas A4 (Fahmi memutuskan, setelah eval
kalibrasi per peran). Model-model terverifikasi di atas tercatat di
`MODELS.yaml` bagian `candidates_verified` sebagai kandidat,
bukan sebagai pengganti.

## Riset & harness

| Rujukan | URL kanonis | Status |
|---|---|---|
| Snell et al. — Scaling LLM Test-Time Compute Optimally (ICLR 2025) | https://arxiv.org/abs/2408.03314 | resmi |
| Yao et al. — τ-bench (pass^k) | https://arxiv.org/abs/2406.12045 | resmi |
| Wu et al. — Meta-Rewarding Language Models | https://arxiv.org/abs/2407.19594 | resmi |
| Greenblatt et al. — Alignment faking in large language models | https://arxiv.org/abs/2412.14093 | resmi |
| DeepSeek-AI — DeepSeek-R1 | https://arxiv.org/abs/2501.12948 | resmi |
| Zhao et al. — Absolute Zero | https://arxiv.org/abs/2505.03335 | resmi |
| Zweiger et al. — Self-Adapting Language Models (SEAL) | https://arxiv.org/abs/2506.10943 | resmi |
| pstack — Lauren Tan (@poteto), Cursor plugin | https://github.com/cursor/plugins/tree/main/pstack | resmi |
| tstack — Theo Browne (@t3dotgg) | https://github.com/t3dotgg/tstack | resmi |
| T3 Code — Theo Browne / Ping.gg | https://github.com/pingdotgg/t3code | resmi |
| Anthropic — Effective harnesses for long-running agents | https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents | resmi |
| Anthropic — Harness design for long-running apps | https://www.anthropic.com/engineering/harness-design-long-running-apps | resmi |
| "The judge is the product" | tidak ditemukan | belum terverifikasi |
| Repo fahmi0812/muse-rsi (baseline design) | https://github.com/fahmi0812/muse-rsi | resmi |

Catatan "The judge is the product": dua pencarian frasa persis
tidak menemukan sumber berjudul itu. Kandidat terdekat (bukan judul
yang sama): esai Eugene Yan "An LLM-as-Judge Won't Save The Product"
dan artikel Medium tentang judge klinis. Perlu klarifikasi dari
penulis design rujukan mana yang dimaksud — jangan kutip sebagai
sumber sampai jelas.
