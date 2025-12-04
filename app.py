import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

GELIR_FILE = Path("gelirler.csv")
GIDER_FILE = Path("giderler.csv")

# ================== ŞİFRE KONTROLÜ ================== #

KULLANICI_ADI = "gundogans"
SIFRE = "1907"  # BURAYI KENDİ ŞİFRENLE DEĞİŞTİREBİLİRSİN


def check_password():
    """Basit kullanıcı adı + şifre kontrolü"""

    if "auth_ok" in st.session_state and st.session_state.auth_ok:
        return True

    st.markdown("### Giriş Yap")

    with st.form("login_form"):
        username = st.text_input("Kullanıcı Adı")
        password = st.text_input("Şifre", type="password")
        submitted = st.form_submit_button("Giriş")

    if submitted:
        if username == KULLANICI_ADI and password == SIFRE:
            st.session_state.auth_ok = True
            st.success("Giriş başarılı.")
            return True
        else:
            st.error("Kullanıcı adı veya şifre hatalı.")
            st.session_state.auth_ok = False
            return False

    st.stop()


# ================== VERİ FONKSİYONLARI ================== #

def load_gelir():
    if GELIR_FILE.exists():
        return pd.read_csv(GELIR_FILE, parse_dates=["tarih"])
    cols = [
        "tarih", "devreden", "pos", "online", "getir", "trendyol", "nakit", "genel",
        "gelen_tavuk", "gelen_lavas", "gelen_patates",
        "kalan_lavas", "satilan_lavas", "ziyan"
    ]
    return pd.DataFrame(columns=cols)


def load_gider():
    if GIDER_FILE.exists():
        return pd.read_csv(GIDER_FILE, parse_dates=["tarih"])
    cols = ["tarih", "kategori", "kime", "aciklama", "pos", "nakit", "toplam"]
    return pd.DataFrame(columns=cols)


def save_gelir(df):
    df.to_csv(GELIR_FILE, index=False)


def save_gider(df):
    df.to_csv(GIDER_FILE, index=False)


# ================== ANA UYGULAMA ================== #

def main():
    st.set_page_config(page_title="Dükkan Günlük Kapanış", layout="wide")

    # Önce şifre kontrolü
    if not check_password():
        return

    st.title("Dükkan Günlük Hesap Kapanışı")

    # Sağ üst köşe yazı + logo
    st.markdown("""
    <div style="position: absolute; top: 10px; right: 20px; text-align: right;">
        <h4 style="margin: 0; padding: 0; font-size:20px;">Ömer Gündoğan</h4>
        <p style="margin: 0; padding: 0; font-size:14px;">Gündoğans Ltd. Şti.</p>
        <img src="logo.jpg" width="120" style="margin-top: 5px; border-radius: 10px;">
    </div>
    """, unsafe_allow_html=True)

    st.caption("GENEL CİRO = Satış (POS+Online+Getir+Trendyol+Nakit) + Günlük kasa harcaması")

    tab1, tab2, tab3 = st.tabs(["Günlük Kayıt", "Gider Ekle", "Raporlar"])

    gelir_df = load_gelir()
    gider_df = load_gider()

    # ----------------- GÜNLÜK GELİR / STOK -----------------
    with tab1:
        st.subheader("Günlük Gelir ve Stok Kaydı")

        col1, col2 = st.columns(2)
        with col1:
            tarih = st.date_input("Tarih", value=date.today())
        with col2:
            mevcut_kayit = None
            mask = None
            if not gelir_df.empty:
                mask = gelir_df["tarih"] == pd.to_datetime(tarih)
                if mask.any():
                    mevcut_kayit = gelir_df[mask].iloc[0]

        devreden = st.number_input(
            "Devreden",
            min_value=0.0,
            value=float(mevcut_kayit["devreden"]) if mevcut_kayit is not None else 0.0,
            step=100.0,
        )

        col_pos, col_online, col_getir = st.columns(3)
        with col_pos:
            pos = st.number_input(
                "POS", min_value=0.0,
                value=float(mevcut_kayit["pos"]) if mevcut_kayit is not None else 0.0,
                step=100.0,
            )
        with col_online:
            online = st.number_input(
                "Online", min_value=0.0,
                value=float(mevcut_kayit["online"]) if mevcut_kayit is not None else 0.0,
                step=100.0,
            )
        with col_getir:
            getir = st.number_input(
                "Getir", min_value=0.0,
                value=float(mevcut_kayit["getir"]) if mevcut_kayit is not None else 0.0,
                step=100.0,
            )

        col_trendyol, col_nakit = st.columns(2)
        with col_trendyol:
            trendyol = st.number_input(
                "Trendyol", min_value=0.0,
                value=float(mevcut_kayit["trendyol"]) if mevcut_kayit is not None else 0.0,
                step=100.0,
            )
        with col_nakit:
            nakit = st.number_input(
                "Nakit", min_value=0.0,
                value=float(mevcut_kayit["nakit"]) if mevcut_kayit is not None else 0.0,
                step=100.0,
            )

        # Satıştan gelen genel (sadece satış toplamı)
        satis_genel = pos + online + getir + trendyol + nakit

        # Aynı tarihteki toplam kasa harcaması (giderler)
        if not gider_df.empty:
            gunluk_gider = gider_df[gider_df["tarih"] == pd.to_datetime(tarih)]["toplam"].sum()
        else:
            gunluk_gider = 0.0

        # GERÇEK GENEL CİRO = Satış + Günlük harcama
        genel = satis_genel + gunluk_gider

        st.info(f"Satıştan Genel (POS+Online+Getir+Trendyol+Nakit): {satis_genel:,.2f} TL")
        st.info(f"Bu tarihte girilmiş kasa harcaması (gider toplamı): {gunluk_gider:,.2f} TL")
        st.success(f"GENEL CİRO (Satış + Harcama): {genel:,.2f} TL")

        st.markdown("---")
        st.subheader("Stok (Lavaş / Tavuk / Patates)")

        col_tavuk, col_lavas, col_patates = st.columns(3)
        with col_tavuk:
            gelen_tavuk = st.number_input(
                "Gelen Tavuk (adet/kg)", min_value=0.0,
                value=float(mevcut_kayit["gelen_tavuk"]) if mevcut_kayit is not None else 0.0,
                step=1.0,
            )
        with col_lavas:
            gelen_lavas = st.number_input(
                "Gelen Lavaş (adet)", min_value=0.0,
                value=float(mevcut_kayit["gelen_lavas"]) if mevcut_kayit is not None else 0.0,
                step=1.0,
            )
        with col_patates:
            gelen_patates = st.number_input(
                "Gelen Patates (kg)", min_value=0.0,
                value=float(mevcut_kayit["gelen_patates"]) if mevcut_kayit is not None else 0.0,
                step=1.0,
            )

        col_kalan, col_satilan, col_ziyan = st.columns(3)
        with col_kalan:
            kalan_lavas = st.number_input(
                "Kalan Lavaş", min_value=0.0,
                value=float(mevcut_kayit["kalan_lavas"]) if mevcut_kayit is not None else 0.0,
                step=1.0,
            )
        with col_satilan:
            satilan_lavas = st.number_input(
                "Satılan Lavaş", min_value=0.0,
                value=float(mevcut_kayit["satilan_lavas"]) if mevcut_kayit is not None else 0.0,
                step=1.0,
            )
        with col_ziyan:
            ziyan = st.number_input(
                "Ziyan Lavaş", min_value=0.0,
                value=float(mevcut_kayit["ziyan"]) if mevcut_kayit is not None else 0.0,
                step=1.0,
            )

        if st.button("Günlük Gelir/Stok Kaydını Kaydet"):
            yeni_veri = {
                "tarih": pd.to_datetime(tarih),
                "devreden": devreden,
                "pos": pos,
                "online": online,
                "getir": getir,
                "trendyol": trendyol,
                "nakit": nakit,
                "genel": genel,  # GENEL CİRO = satış + gider
                "gelen_tavuk": gelen_tavuk,
                "gelen_lavas": gelen_lavas,
                "gelen_patates": gelen_patates,
                "kalan_lavas": kalan_lavas,
                "satilan_lavas": satilan_lavas,
                "ziyan": ziyan,
            }
            if mevcut_kayit is not None and mask is not None:
                idx = gelir_df.index[mask][0]
                for k, v in yeni_veri.items():
                    gelir_df.at[idx, k] = v
            else:
                gelir_df = pd.concat(
                    [gelir_df, pd.DataFrame([yeni_veri])],
                    ignore_index=True
                )
            save_gelir(gelir_df)
            st.success("Günlük kayıt kaydedildi.")

        if not gelir_df.empty:
            st.markdown("### Son 7 Gün Gelir/Stok Özeti")
            son7 = gelir_df.sort_values("tarih", ascending=False).head(7).copy()
            son7["tarih"] = son7["tarih"].dt.strftime("%d.%m.%Y")
            st.dataframe(son7)

    # ----------------- GİDER -----------------
    with tab2:
        st.subheader("Günlük Gider Ekle (Personel, Market, vb.)")
        tarih_gider = st.date_input("Tarih (Gider)", value=date.today(), key="gider_tarih")

        kategori = st.selectbox(
            "Kategori",
            ["Personel", "Market", "Tedarikçi", "Temizlik", "Fatura", "Diğer"],
        )
        kime = st.text_input("Kime / Nereden (isim / firma)")
        aciklama = st.text_input("Açıklama (opsiyonel)")
        col_pos_gider, col_nakit_gider = st.columns(2)
        with col_pos_gider:
            pos_gider = st.number_input("POS ile Ödenen", min_value=0.0, step=50.0)
        with col_nakit_gider:
            nakit_gider = st.number_input("Nakit Ödenen", min_value=0.0, step=50.0)

        toplam_gider = pos_gider + nakit_gider
        st.info(f"Toplam Gider: {toplam_gider:,.2f} TL")

        if st.button("Gideri Kaydet"):
            yeni_gider = {
                "tarih": pd.to_datetime(tarih_gider),
                "kategori": kategori,
                "kime": kime,
                "aciklama": aciklama,
                "pos": pos_gider,
                "nakit": nakit_gider,
                "toplam": toplam_gider,
            }
            gider_df = pd.concat(
                [gider_df, pd.DataFrame([yeni_gider])],
                ignore_index=True
            )
            save_gider(gider_df)
            st.success("Gider kaydedildi. (Bu gider, ilgili günün GENEL CİRO hesabına dahil edilecek)")

        if not gider_df.empty:
            st.markdown("### Son 7 Gün Gider Özeti")
            son7g = gider_df.sort_values("tarih", ascending=False).head(7).copy()
            son7g["tarih"] = son7g["tarih"].dt.strftime("%d.%m.%Y")
            st.dataframe(son7g)
            # ---------- GİDER DÜZENLE / SİL ----------
            if not gider_df.empty:
                st.markdown("---")
                st.markdown("### Gider Düzenle / Sil")

                # Her satır için seçim metni oluştur (Tarih | Kategori | Tutar)
                edit_df = gider_df.reset_index().copy()  # 'index' = orijinal satır numarası
                edit_df["secim"] = edit_df.apply(
                    lambda row: f"{row['tarih'].strftime('%d.%m.%Y')} | {row['kategori']} | {row['toplam']} TL",
                    axis=1
                )

                secim = st.selectbox(
                    "Düzenlemek / silmek istediğin gideri seç:",
                    edit_df["secim"]
                )

                secili_satir = edit_df[edit_df["secim"] == secim].iloc[0]
                satir_index = int(secili_satir["index"])  # gider_df içindeki gerçek index

                st.write("Seçili gideri düzenle:")

                col_tarih_edit, col_kat_edit = st.columns(2)
                with col_tarih_edit:
                    tarih_edit = st.date_input(
                        "Tarih (düzeltme)",
                        value=secili_satir["tarih"].date(),
                        key="edit_tarih"
                    )
                with col_kat_edit:
                    kategori_edit = st.text_input(
                        "Kategori (düzeltme)",
                        value=str(secili_satir["kategori"]),
                        key="edit_kategori"
                    )

                kime_edit = st.text_input(
                    "Kime / Nereden (düzeltme)",
                    value=str(secili_satir["kime"]),
                    key="edit_kime"
                )
                aciklama_edit = st.text_input(
                    "Açıklama (düzeltme)",
                    value=str(secili_satir["aciklama"]),
                    key="edit_aciklama"
                )

                col_pos_edit, col_nakit_edit = st.columns(2)
                with col_pos_edit:
                    pos_edit = st.number_input(
                        "POS ile Ödenen (düzeltme)",
                        min_value=0.0,
                        value=float(secili_satir["pos"]),
                        step=50.0,
                        key="edit_pos"
                    )
                with col_nakit_edit:
                    nakit_edit = st.number_input(
                        "Nakit Ödenen (düzeltme)",
                        min_value=0.0,
                        value=float(secili_satir["nakit"]),
                        step=50.0,
                        key="edit_nakit"
                    )

                toplam_edit = pos_edit + nakit_edit
                st.info(f"Düzenlenen Toplam Gider: {toplam_edit:,.2f} TL")

                col_kaydet, col_sil = st.columns(2)
                with col_kaydet:
                    if st.button("Değişiklikleri Kaydet"):
                        gider_df.at[satir_index, "tarih"] = pd.to_datetime(tarih_edit)
                        gider_df.at[satir_index, "kategori"] = kategori_edit
                        gider_df.at[satir_index, "kime"] = kime_edit
                        gider_df.at[satir_index, "aciklama"] = aciklama_edit
                        gider_df.at[satir_index, "pos"] = pos_edit
                        gider_df.at[satir_index, "nakit"] = nakit_edit
                        gider_df.at[satir_index, "toplam"] = toplam_edit
                        save_gider(gider_df)
                        st.success("Gider kaydı güncellendi. Sayfayı yenilersen tabloda yeni hali görünür.")

                with col_sil:
                    if st.button("Seçili Gideri Sil"):
                        gider_df = gider_df.drop(satir_index).reset_index(drop=True)
                        save_gider(gider_df)
                        st.success("Gider kaydı silindi. Sayfayı yenilersen listeden kaybolur.")
    # ----------------- RAPORLAR -----------------
    with tab3:
        st.subheader("Aylık Raporlar (1'inden Ay Sonuna)")

        if gelir_df.empty:
            st.warning("Henüz gelir kaydı yok.")
            return

        gelir_df["yil"] = gelir_df["tarih"].dt.year
        gelir_df["ay"] = gelir_df["tarih"].dt.month

        years = sorted(gelir_df["yil"].unique())
        secili_yil = st.selectbox("Yıl", years)
        months = sorted(gelir_df[gelir_df["yil"] == secili_yil]["ay"].unique())
        secili_ay = st.selectbox("Ay", months, format_func=lambda x: f"{x:02d}")

        aylik_gelir = gelir_df[
            (gelir_df["yil"] == secili_yil) &
            (gelir_df["ay"] == secili_ay)
        ]

        if aylik_gelir.empty:
            st.warning("Bu ay için gelir kaydı yok.")
        else:
            son_gun = int(aylik_gelir["tarih"].dt.day.max())
            st.markdown(
                f"### {secili_yil}-{secili_ay:02d} Gelir Özeti "
                f"(1 - {son_gun}. gün arası)"
            )
            gdf = aylik_gelir.sort_values("tarih").copy()
            gdf["tarih"] = gdf["tarih"].dt.strftime("%d.%m.%Y")
            st.dataframe(gdf)

            toplam_genel_ciro = float(aylik_gelir["genel"].sum())

            toplam_pos = float(aylik_gelir["pos"].sum())
            toplam_online = float(aylik_gelir["online"].sum())
            toplam_getir = float(aylik_gelir["getir"].sum())
            toplam_trendyol = float(aylik_gelir["trendyol"].sum())
            toplam_nakit = float(aylik_gelir["nakit"].sum())
            toplam_satis = toplam_pos + toplam_online + toplam_getir + toplam_trendyol + toplam_nakit

            st.write(f"**Toplam Satış Geliri (POS+Online+Getir+Trendyol+Nakit):** {toplam_satis:,.2f} TL")
            st.write(f"**Toplam GENEL CİRO (Satış + Günlük Harcamalar):** {toplam_genel_ciro:,.2f} TL")

        if not gider_df.empty:
            gider_df["yil"] = gider_df["tarih"].dt.year
            gider_df["ay"] = gider_df["tarih"].dt.month
            aylik_gider = gider_df[
                (gider_df["yil"] == secili_yil) &
                (gider_df["ay"] == secili_ay)
            ]

            st.markdown(f"### {secili_yil}-{secili_ay:02d} Gider Özeti")
            if aylik_gider.empty:
                st.info("Bu ay için gider kaydı yok.")
            else:
                gdr = aylik_gider.sort_values("tarih").copy()
                gdr["tarih"] = gdr["tarih"].dt.strftime("%d.%m.%Y")
                st.dataframe(gdr)
                toplam_gider_ay = float(aylik_gider["toplam"].sum())
                st.write(f"**Toplam Gider (ay içi kasa harcamaları):** {toplam_gider_ay:,.2f} TL")
                net_kar = toplam_genel_ciro - toplam_gider_ay
                st.success(f"**Aylık Net Kâr (GENEL CİRO - Giderler): {net_kar:,.2f} TL**")


if __name__ == "__main__":
    main()