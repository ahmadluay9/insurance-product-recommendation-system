from google.adk.agents import Agent
from typing import Literal

def rekomendasi_asuransi_kesehatan(
    perlindungan_untuk: Literal["individu", "keluarga"],
    butuh_perlindungan_penyakit_kritis: bool = False
) -> dict:
    """
    Memberikan rekomendasi produk asuransi kesehatan berdasarkan kebutuhan nasabah.

    Args:
        perlindungan_untuk (Literal["individu", "keluarga"]): Target perlindungan, untuk perorangan atau keluarga.
        butuh_perlindungan_penyakit_kritis (bool): Apakah nasabah membutuhkan perlindungan untuk penyakit kritis. Defaults to False.

    Returns:
        dict: Berisi status dan pesan rekomendasi produk.
    """
    rekomendasi = []
    if butuh_perlindungan_penyakit_kritis:
        rekomendasi.append({
            "nama_produk": "Sequis Q Early Payout Critical Illness Plus Rider",
            "deskripsi": "Memberikan perlindungan menyeluruh hingga 120 kondisi penyakit kritis sejak tahap awal."
        })
    else:
        rekomendasi.append({
            "nama_produk": "Sequis Q Infinite Medcare Shield Rider",
            "deskripsi": "Menawarkan perlindungan kesehatan premium dengan limit tahunan hingga Rp90 Miliar."
        })
        rekomendasi.append({
            "nama_produk": "Sequis Health Protection",
            "deskripsi": "Memberikan manfaat rawat inap dan pembedahan. Cocok untuk perlindungan dasar."
        })

    return {
        "status": "sukses",
        "rekomendasi": f"Berdasarkan kebutuhan Anda untuk perlindungan {perlindungan_untuk}, berikut adalah rekomendasi produk yang cocok: {rekomendasi}"
    }


def rekomendasi_asuransi_pendidikan(usia_anak: int, jenjang_pendidikan: Literal["SD", "SMP", "SMA", "Perguruan Tinggi"]) -> dict:
    """
    Memberikan rekomendasi produk asuransi untuk dana pendidikan anak.

    Args:
        usia_anak (int): Usia anak saat ini.
        jenjang_pendidikan (Literal["SD", "SMP", "SMA", "Perguruan Tinggi"]): Jenjang pendidikan yang direncanakan.

    Returns:
        dict: Berisi status dan pesan rekomendasi produk.
    """
    if usia_anak > 10:
        return {
            "status": "gagal",
            "pesan_error": "Perencanaan asuransi pendidikan idealnya dimulai sebelum anak berusia 10 tahun untuk hasil yang lebih optimal."
        }

    rekomendasi = [
        {
            "nama_produk": "Sequis EduPlan Insurance",
            "deskripsi": f"Produk ini memberikan fleksibilitas masa asuransi dan memiliki nilai tunai yang dapat digunakan untuk dana pendidikan jenjang {jenjang_pendidikan}."
        },
        {
            "nama_produk": "Asuransi Sequis EduPlan",
            "deskripsi": "Dengan premi terjangkau, produk ini memberikan manfaat dana pendidikan yang pasti untuk masa depan anak Anda."
        }
    ]
    return {
        "status": "sukses",
        "rekomendasi": f"Untuk anak usia {usia_anak} tahun dengan rencana pendidikan {jenjang_pendidikan}, berikut rekomendasinya: {rekomendasi}"
    }


def rekomendasi_dana_pensiun(usia_saat_ini: int, usia_pensiun: int) -> dict:
    """
    Memberikan rekomendasi produk untuk perencanaan dana pensiun.

    Args:
        usia_saat_ini (int): Usia nasabah saat ini.
        usia_pensiun (int): Usia target nasabah untuk pensiun.

    Returns:
        dict: Berisi status dan pesan rekomendasi produk.
    """
    if usia_saat_ini >= usia_pensiun:
        return {
            "status": "gagal",
            "pesan_error": "Usia saat ini harus lebih kecil dari usia pensiun yang direncanakan."
        }

    return {
        "status": "sukses",
        "rekomendasi": {
            "nama_produk": "Sequis Q Heritage Income Protector",
            "deskripsi": f"Produk ini memberikan perlindungan seumur hidup dan manfaat dana pensiun yang bisa mulai dicairkan pada usia {usia_pensiun} untuk menjamin masa tua yang sejahtera."
        }
    }


def rekomendasi_asuransi_investasi(profil_risiko: Literal["konservatif", "moderat", "agresif"]) -> dict:
    """
    Memberikan rekomendasi produk asuransi yang dikaitkan dengan investasi (unit link).

    Args:
        profil_risiko (Literal["konservatif", "moderat", "agresif"]): Profil risiko investasi nasabah.

    Returns:
        dict: Berisi status dan pesan rekomendasi produk.
    """
    return {
        "status": "sukses",
        "rekomendasi": {
            "nama_produk": "SequislinQ Path Protector",
            "deskripsi": f"Produk ini menggabungkan manfaat asuransi jiwa dengan investasi. Untuk profil risiko {profil_risiko}, Anda dapat memilih alokasi dana yang sesuai untuk memaksimalkan potensi imbal hasil sambil tetap terlindungi."
        }
    }

# --- Inisialisasi Agen ---

root_agent = Agent(
    name="agen_rekomendasi_asuransi",
    model="gemini-1.5-flash",
    description="Agen yang membantu memberikan rekomendasi produk asuransi Sequis berdasarkan kebutuhan nasabah.",
    instruction=(
        "Anda adalah asisten asuransi virtual dari Sequis. "
        "Tugas Anda adalah memahami kebutuhan pengguna dan merekomendasikan produk asuransi yang paling sesuai. "
        "Gunakan tools yang tersedia untuk memberikan rekomendasi berdasarkan informasi yang diberikan pengguna. "
        "Selalu sapa pengguna dengan ramah dan berikan penjelasan yang jelas."
    ),
    tools=[
        rekomendasi_asuransi_kesehatan,
        rekomendasi_asuransi_pendidikan,
        rekomendasi_dana_pensiun,
        rekomendasi_asuransi_investasi,
    ],
)