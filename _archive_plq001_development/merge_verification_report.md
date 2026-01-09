
# Laporan Verifikasi Penggabungan PRK (Merge Report)

Berikut adalah rincian detail bagaimana nilai Anggaran/Realisasi digabungkan dari file PLQ001 ke Dashboard.
Tujuannya adalah membuktikan bahwa penggabungan **Carry-Over (242/232)** ke **2025 (252)** sudah dilakukan dengan benar dan nilainya klop.

## 1. Rincian Penggabungan (Merged Projects)
Hanya PRK yang memiliki komponen "titipan" (carry-over) atau penyesuaian yang ditampilkan di sini. PRK murni 2025 lainnya sudah pasti sama.

| Kode PRK (Dashboard) | Nilai di Database (Rp) | Komposisi (Dari File PLQ001) |
| :--- | :--- | :--- |
| **PL252G0101** | `2,959,648,780` | `242G0101` (+144) <br> `252G0101` (+2,959,648,636) |
| **PL252G0102** | `43,980,526,369` | `242G0102` (-41,636,194) <br> `252G0102` (+44,022,162,563) |
| **PL252I0204** | `0` | `PL- (Reversal)` (-136,530,000) <br> `242I0204` (+136,530,000) |
| **PL252J0102** | `752,663,789` | `242J0102` (+96,875,000) <br> `252J0102` (+655,788,789) |
| **PL252L0101** | `1,436,330,574` | `242L0101` (+233,827,494) <br> `252L0101` (+1,202,503,080) |
| **PL252P0102** | `3,160,288,105` | `232P0102` (+16,074,576) <br> `242P0102` (-9,208,640) <br> `252P0102` (+3,153,422,169) |
| **PL252P0108** | `332,055,751` | `252P0108` (+551,894,542) <br> `(Reversal)` (-219,838,791) |

## 2. Kesimpulan Status Data
*   **Total Realisasi Dashboard:** `Rp 108,436,047,458.10`
*   **Total Laporan PLQ001:** `Rp 108,436,047,458.10`
*   **Selisih:** `Rp 0` (Sama Persis/Exact Match)

## 3. Catatan
*   Nilai yang Anda lihat di Dashboard untuk PRK di atas adalah **Nilai Netto** (Total setelah ditambah/dikurang saldo carry-over).
*   Jika Anda merasa nilai `PL252G0102` terlalu kecil, itu karena dikurangi pengembalian biaya tahun lalu sebesar 41 Juta.
