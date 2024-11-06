# monitoring-BPJS
Bagaimana distribusi kunjungan pasien ke berbagai poli sepanjang bulan Juli?

Konteks: Berguna untuk mengetahui poliklinik yang paling sibuk untuk alokasi sumber daya.
Dokter mana yang memiliki tingkat kunjungan tertinggi dan bagaimana performa keberhasilan konfirmasi pasiennya?

Konteks: Menentukan efisiensi setiap dokter dalam menangani pasien, membantu alokasi dokter di klinik tersibuk.
Apakah terdapat perbedaan jumlah kunjungan berdasarkan jenis pembayaran, misalnya BPJS vs pembayaran pribadi?

Konteks: Untuk mengetahui ketergantungan pada skema pembayaran tertentu dan dampaknya terhadap beban operasional.
Apakah pasien yang datang untuk kunjungan kontrol lebih sering mengalami "status kirim" gagal dibandingkan dengan kunjungan pertama?

Konteks: Mengidentifikasi kendala logistik atau komunikasi dalam proses konfirmasi untuk kunjungan lanjutan.
Apakah ada tren waktu tertentu dalam sehari atau dalam bulan di mana tingkat kegagalan "status kirim" lebih tinggi?

Konteks: Mengetahui waktu-waktu kritis dalam pengiriman konfirmasi atau teknis terkait.


"SELECT pasien.no_peserta,pasien.no_rkm_medis,pasien.no_ktp,pasien.no_tlp,reg_periksa.no_reg,reg_periksa.no_rawat,reg_periksa.tgl_registrasi,reg_periksa.kd_dokter,dokter.nm_dokter,reg_periksa.kd_poli,poliklinik.nm_poli,reg_periksa.stts_daftar,reg_periksa.no_rkm_medis
      FROM reg_periksa INNER JOIN pasien ON reg_periksa.no_rkm_medis=pasien.no_rkm_medis INNER JOIN dokter ON reg_periksa.kd_dokter=dokter.kd_dokter INNER JOIN poliklinik ON reg_periksa.kd_poli=poliklinik.kd_poli WHERE reg_periksa.tgl_registrasi='$date' AND reg_periksa.kd_poli NOT IN ('$exclude_taskid')
      ORDER BY concat(reg_periksa.tgl_registrasi,' ',reg_periksa.jam_reg)"
