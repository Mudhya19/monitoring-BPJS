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


        SELECT
            r.no_rawat,
            mr.tanggal_periksa,
            r.jam_reg,
            pl.nm_poli,
            d.nm_dokter,
            p.nm_pasien,
            p.no_rkm_medis,
            r.status_lanjut,
            # r.status_bayar,
            pj.png_jawab,
            # r.kd_dokter,
            mr.nomor_kartu,
            mr.nomor_referensi,
            mr.kodebooking,
            mr.jenis_kunjungan,
            mr.status_kirim,
            mr.keterangan
        FROM
            reg_periksa r
            INNER JOIN pasien p ON r.no_rkm_medis = p.no_rkm_medis
            INNER JOIN penjab pj ON r.kd_pj = pj.kd_pj
            INNER JOIN dokter d ON r.kd_dokter = d.kd_dokter
            INNER JOIN poliklinik pl ON r.kd_poli = pl.kd_poli
            INNER JOIN mlite_antrian_referensi mr ON r.no_rkm_medis = mr.no_rkm_medis
        WHERE
            mr.tanggal_periksa BETWEEN '{start_date}' AND '{end_date}'
            AND pl.nm_poli != 'INSTALASI GAWAT DARURAT'
            AND (mr.tanggal_periksa, r.jam_reg) IN (
                SELECT MIN(mr_inner.tanggal_periksa), MIN(r_inner.jam_reg)
                FROM reg_periksa r_inner
                INNER JOIN mlite_antrian_referensi mr_inner ON r_inner.no_rkm_medis = mr_inner.no_rkm_medis
                WHERE mr_inner.tanggal_periksa BETWEEN '{start_date}' AND '{end_date}'
                GROUP BY r_inner.no_rkm_medis
            )
        GROUP BY
            r.no_rawat
        ORDER BY
            mr.tanggal_periksa, r.jam_reg;