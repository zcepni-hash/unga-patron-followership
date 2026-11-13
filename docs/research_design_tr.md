# Who Follows a Great Power? — Araştırma Tasarımı ve Kod Kitabı

Nov 13, 2026 · @zehra

## Genel mimari

Proje, bir büyük güç tekrarlanan bir kararda oyunu değiştirdiğinde (switch) diğer devletlerin patrona bağlarına mı (dikey kanal) yoksa oy partnerlerine mi (yatay kanal) göre hareket ettiğini test ediyor. Analiz birimi devlet × olay, model olay sabit etkili bir doğrusal olasılık modeli.

**Araştırma sorusu:** Bir büyük güç tekrarlanan bir BM Genel Kurulu kararında oyunu değiştirdiğinde, devletler bağlı oldukları patronu mu yoksa genelde birlikte oy verdikleri devletler ağını mı takip ediyor?

**Hipotezler**

- **H1 Dikey kanal:** Patrona bağımlılığı (güvenlik, ticaret, yardım) yüksek olan devletin patronun yönünde hareket etme olasılığı daha yüksektir.
- **H2 Yatay kanal:** Oy partnerlerinin daha büyük bir kısmı patronla birlikte hareket eden devletin, kendi patron bağlarından bağımsız olarak, patronun yönünde hareket etme olasılığı daha yüksektir.
- **H3 Koşul:** Bağımlılığın takip üzerindeki etkisi, patronun önemsediği oylarda daha güçlüdür.

Araştırma sorusunun cevabı, H1 bloğu ile H2 değişkeninin standartlaştırılmış etkilerinin ve açıklama güçlerinin karşılaştırılmasından gelir.

**Tasarımın mantığı: üç güvence**

1. **Switch tasarımı:** Devletin aynı karardaki bir önceki oyu kendi referans noktasıdır. O karara ilişkin sabit tercihler böylece analizden düşer. Bu, Bailey, Strezhnev & Voeten'in (2017) özdeş kararları köprü olarak kullanma mantığıyla aynı.
2. **Olay sabit etkisi:** Olaya ait her şey (patron, konu, yıl, o olayda kaç devletin hareket ettiği) modelden düşer. Etki, aynı olay içindeki devletler arasındaki farktan tahmin edilir.
3. **Gecikmeli ölçüm:** Bağlar ve oy ağı switch'ten önceki yıl ya da oturumdan ölçülür. Böylece aynı olay içinde ters nedensellik oluşmaz.

## Kavramlar sözlüğü

Her kavramın bu projedeki tanımı, dayandığı literatür ve kodda nasıl karşılandığı aşağıda. Kod sütunundaki adlar Kod kitabı bölümündeki değişken adlarıyla aynı.

| Kavram | Bu projedeki tanım | Literatür dayanağı | Kodda |
| --- | --- | --- | --- |
| Patron (P) | BM Güvenlik Konseyi'nin beş daimi üyesi: ABD, Çin, Rusya, Fransa, İngiltere | Lake (2009): baskın devlet–bağımlı devlet hiyerarşisi | `patron` |
| Tekrarlanan karar | Ardışık oturumlarda aynı başlık ve metinle oylanan karar | Bailey, Strezhnev & Voeten (2017): özdeş kararlar köprü gözlemi | `rcid_t`, `rcid_tm1` |
| Switch (olay) | P'nin tekrarlanan bir kararda oturum t'deki oyunun t−1'dekinden farklı olması | Voeten (2026): aynı kararda yıldan yıla oy değişikliği | `event_id`, `dir` |
| Takip | Devletin aynı olayda P ile aynı yönde oy değiştirmesi | Thacker (1999): ABD'ye doğru "hareket" | `Y` |
| Risk seti | Önceki oyu P yönünde hareket etmeye yer bırakan ve iki oturumda da oy kullanan devletler | Proposal tanımı | `in_risk` |
| Dikey bağ | Devletle P arasındaki maddi bağ: ittifak, silah, ticaret, yardım | Dreher vd. (2008); Flores-Macías & Kreps (2013); Kinne (2020) | `D_*` |
| Yatay bağ / oy partneri | Önceki oturumda devletle ağırlıklı κ'sı en yüksek 10 devlet (beş patron hariç) | Häge (2011); Pauls & Cranmer (2017) | `partners` |
| Partner maruziyeti | Risk setindeki partnerlerin aynı olayda P ile hareket edenlerinin payı | Ağlarda akran etkisi: Manski (1993); Bramoullé vd. (2009) | `E` |
| Formal blok | Oy koordinasyonu yapan kurumsal gruplar: AB, BM bölgesel grupları, NAM, İİT | AB'nin ortak dış politika kapsamında oy koordinasyonu (Luif 2003) | `bloc_*` |
| Topluluk | Oy ağında Leiden algoritmasıyla bulunan, iç bağları yoğun devlet grupları | Traag vd. (2019); Pauls & Cranmer (2017) | `comm` |
| Önem (salience) | P'nin o kararı özellikle önemsemesi; ABD için Dişişleri'nin "important votes" listesi | Thacker (1999); Dreher & Jensen (2013) | `S` |
| Yakınlık (kontrol) | Devletin önceki oturumda P ile genel oy benzerliği | Gartzke (1998); BSV ideal noktaları | `close_kappa`, `ideal_dist` |
| Multipleks ağ | Aynı devlet kümesi üzerinde birden fazla kenar türü (oy, ittifak, ticaret, silah) | Kivelä vd. (2014); Cranmer, Menninga & Mucha (2015) | `edges` tablosu, `layer` sütunu |
| Takipçi ağı | Devlet → patron yönlü ağ; ağırlık, devletin P'nin switch'lerinden takip ettiği pay | Bu projenin betimsel katkısı | `follow_net` |

**İki kavram arasındaki fark kritik:** *Takip* bir değişimdir ve olay düzeyinde ölçülür. *Yakınlık* bir düzeydir ve kontrol olarak modele girer. Literatürün çoğu yakınlığı etki gibi yorumladığı için, bu ayrımı proposal'da açıkça yazmak gerekiyor.

## Analiz birimi, olay ve sonuç değişkeni

Analiz birimi devlet × olaydır: 209 olay ve olay başına risk setinde ortalama \~120–190 devlet, toplamda yaklaşık 25.000–40.000 satır. Beş patron hiçbir olayda birim olarak yer almaz, çünkü onlar takipçi değil rakiptir.

### Oy kodlaması

Devlet i'nin oturum t'de karar r'ye verdiği oy:

```latex
v_{i,r,t} \in \{0,\ 0.5,\ 1\} \quad (\text{hayır},\ \text{çekimser},\ \text{evet})
```

Yokluk (BSV kodu 8) eksik veridir, 0.5 değildir. Üye olmayan (kod 9) ve Madde 19 nedeniyle oy hakkı askıya alınmış devletler o oturum için dışarıda kalır. Yalnızca kararların bütünü için yapılan oylamalar kullanılır; paragraf bazında yapılan ayrı oylamalar çıkarılır.

### Tekrarlanan karar eşleştirmesi

t'deki karar r ile t−1'deki karar r′ şu üç koşul sağlanırsa "aynı karar" sayılır:

1. Normalleştirilmiş başlıklar eşleşir (küçük harf, noktalama ve oturum numarası temizlenmiş).
2. Aynı komite ya da gündem maddesi.
3. Metin benzerliği (TF-IDF cosine) en az 0,80. 0,60 ile 0,80 arası vakalar elle kontrol edilir, 0,60'ın altı eşleşme sayılmaz.

Eşleştirmenin doğruluğu Voeten'in sayılarıyla kontrol edilir: ABD için 2018'de 4, 2019'da 3, 2025'te 12 switch.

### Olay

Olay e = (P, r, t), patronun oyunun değiştiği her tekrarlanan karardır. Olayın yönü:

```latex
d_e = \operatorname{sign}\left(v_{P,r,t} - v_{P,r',t-1}\right) \in \{-1,\ +1\}
```

### Risk seti

Devlet i, iki oturumda da oy kullandıysa ve önceki oyu P yönünde hareket etmeye yer bırakıyorsa risk setindedir:

```latex
R_e = \{\, i \notin P5 :\ v_{i,t-1} < 1 \text{ if } d_e = +1;\ \ v_{i,t-1} > 0 \text{ if } d_e = -1 \,\}
```

### Sonuç değişkeni

Ana sonuç, devletin P yönünde herhangi bir hareket yapıp yapmadığıdır:

```latex
Y_{ie} = \mathbf{1}\left[\, d_e \cdot \left(v_{i,t} - v_{i,t-1}\right) > 0 \,\right], \qquad i \in R_e
```

Robustluk için iki alternatif:

- **Sıralı sonuç:** −1 = ters yön, 0 = hareketsiz, 1 = kısmi takip (P yönünde hareket etti ama P'nin yeni oyuna ulaşmadı), 2 = tam takip (v\_{i,t} = v\_{P,t}). Sıralı logit ile tahmin edilir.
- **Sürekli sonuç:** Δ\_ie = d\_e · (v\_{i,t} − v\_{i,t−1}), −1 ile 1 arası. Çekimseri yarım adım sayan kodlamayı doğrudan kullanır.

**Örnek:** ABD bir kararda evetten hayıra geçerse (d = −1) ve devlet evetten çekimsere geçerse: Y = 1, sıralı sonuç = 1 (kısmi), Δ = 0,5. Devlet zaten hayır demişse risk setinde değildir.

## Ağ mimarisi: düğümler, kenarlar, katmanlar

Multipleks ağ burada bir ölçüm mimarisi olarak kullanılıyor: aynı devlet kümesi üzerinde dört kenar türü var ve dikey ile yatay kanal bu kenarların iki ayrı alt kümesi olarak tanımlanıyor. Tahmin edilen şey ağın kendisi değil, ağtan türetilen değişkenlerle devletin olay düzeyindeki davranışı.

### Düğümler

- **Düğüm kümesi V\_t:** Oturum t'de oy hakkı olan BM üyesi devletler (\~193). Yeni üyeler giriş yılından itibaren dahil (Karadağ 2006, Güney Sudan 2011).
- **Patron düğümleri:** P5 ⊂ V\_t. Her katmanda yer alırlar ama yatay kanalın partner listelerinden çıkarılırlar.
- **Kimlik:** Tüm kaynaklar ISO3 koduna çevrilir (R'da `countrycode`). ATOP COW kodu, IMF verisi IMF kodu kullanır.
- **Düğüm özellikleri (t−1):** V-Dem seçimsel demokrasi endeksi, log GSYH, log askeri harcama, BM bölgesel grubu, AB/NAM/İİT üyeliği, lider değişimi; olay düzeyinde önceki oy ve Y.

### Katmanlar

| Katman | Kenar | Yön / ağırlık | Kaynak | Zaman | Rol |
| --- | --- | --- | --- | --- | --- |
| L1 Ko-oylama | Ağırlıklı Cohen's κ → her devletin en yakın 10 partneri | Yönlü kNN (i → partnerleri), ağırlık κ | Oy verisi | Oturum t−1 | Yatay kanal (H2), topluluklar |
| L2 İttifak | ATOP savunma paktı | Yönsüz, ikili | ATOP v5.1 (2018 sonrası ileri taşınır) | Yıl t−1 | P'ye bağlı kenarlar: dikey (H1) |
| L3 Ticaret | İhracat ve ithalat payları | Yönlü, ağırlıklı | IMF IMTS | Yıl t−1 | P'ye bağlı kenarlar: dikey (H1) |
| L4 Silah | Ana tedarikçi ve TIV payı | Yönlü (tedarikçi → alıcı), ağırlıklı | SIPRI Arms Transfers | t−5 ile t−1 arası | P'ye bağlı kenarlar: dikey (H1) |

### Dikey ve yatay kanalın ağ tanımı

Multipleksteki kenarlar iki ayrık kümeye bölünüyor. Bu bölünme, araştırma sorusunun ağ dilindeki karşılığı:

- **Dikey kanal:** L2–L4 katmanlarında, olayın patronu P'ye bağlanan kenarlar. Devlet i için bunlar ego merkezli bir vektör oluşturur: (pakt, silah, ihracat payı, ithalat payı, yardım).
- **Yatay kanal:** L1 katmanında iki ucunda da patron olmayan kenarlar. Devlet i için bunlar partner listesi N\_i'dir.

### Neden tam bir multipleks istatistik modeli değil?

ERGM veya multipleks topluluk modelleri kenar oluşumunu açıklar; bizim sonucumuz ise düğüm davranışı (olaydaki hareket). Bu yüzden katmanlar üç şekilde kullanılıyor:

1. **Değişken türetme:** Dikey vektör ve partner maruziyeti regresyona girer (Tahmin modeli bölümü).
2. **Betimleme:** Katman örtüşmesi, QAP korelasyonu ve multislice topluluklar (Betimsel ağlar bölümü).
3. **Placebo:** L1'de 11–20. sıradaki devletler ("neredeyse partnerler"), partner maruziyetiyle aynı biçimde hesaplanır ve benzerlik itirazını test eder.

Seçilim ile etkiyi birlikte modelleyen stokastik aktör odaklı modeller (SAOM, RSiena; Steglich, Snijders & Pearson 2010) doğal bir uzantıdır, ama ana analiz için gerekli değildir.

### Koddaki temsil

Tüm katmanlar tek bir uzun kenar tablosunda tutulur, her ağ bundan filtrelenir:

```csv
t,layer,i,j,weight,directed
2024,L1_covote,TUR,AZE,0.71,1
2024,L2_alliance,TUR,USA,1,0
2024,L3_export,TUR,DEU,0.15,1
2024,L4_arms,USA,TUR,0.38,1
```

Python'da her (t, katman) için bir `igraph.Graph` oluşturulur. Multislice topluluk tespiti `leidenalg.optimise_partition_multiplex` ile yapılır.

&#91;embedded content: iki kanal · dikey bağlar L2–L4, yatay bağlar L1\]

Odak devlet i, P'ye doğrudan bağlı değil ama oy partnerleri A ve C bağlı. H2'yi en güçlü biçimde test eden vakalar bu tür devletler.

## Ölçümler

Tüm değişkenler switch'ten önceki oturum ya da yıldan (t−1) ölçülür. Tek istisna partner maruziyeti: partnerler t−1'den belirlenir, ama onların hareketi aynı olaydan gelir.

### Ağırlıklı Cohen's κ (L1 katmanı)

Oturum t−1'de iki devletin de oy kullandığı kararlar üzerinden hesaplanır. En az 20 ortak oy şartı aranır, altında κ eksik sayılır. Doğrusal uyum ağırlığı, oyların 0/0.5/1 kodlamasıyla uyumludur:

```latex
w(a,b) = 1 - |a-b|, \qquad p_o = \frac{1}{n}\sum_{r} w(v_{ir}, v_{jr}), \qquad p_e = \sum_{a}\sum_{b} \hat p_i(a)\,\hat p_j(b)\,w(a,b)
```

```latex
\kappa_{ij} = \frac{p_o - p_e}{1 - p_e}
```

Burada ̂p\_i(a), devlet i'nin o oturumda a oyunu verme payıdır (Cohen: ülkeye özgü marjinaller). Robustluk için Scott's π (havuzlanmış marjinaller) kullanılır. 2001–2015 değerleri Häge'in FPSIM v2 verisiyle karşılaştırılır.

### Backbone ve partner listesi

```latex
N_{i,t-1} = \text{top-}k \text{ of } \{\, j \notin P5,\ j \neq i \,\} \text{ by } \kappa_{ij,t-1}, \qquad k = 10
```

- Eşitlik durumunda ortak oy sayısı fazla olan seçilir.
- kNN ilişkisi yönlüdür: j, i'nin partneri olabilir ama tersi olmayabilir. Maruziyet i için i'nin kendi listesiyle hesaplanır.
- Topluluk tespiti için ağ simetrik hale getirilir (iki taraftan biri listedeyse kenar var, ağırlık κ).
- Duyarlılık: k = 5 ve k = 15.

### Partner maruziyeti (H2)

```latex
E_{ie} = \frac{1}{|N_i \cap R_e|} \sum_{j \in N_i \cap R_e} Y_{je}
```

- Payda yalnızca risk setindeki partnerlerdir. Hareket edemeyecek partnerler maruziyeti yapay olarak düşürmesin diye.
- Kontrol: m\_ie = |N\_i ∩ R\_e| / k, yani partnerlerin kaçının risk setinde olduğu. Hiçbiri değilse E eksik sayılır ve bir gösterge değişkeni eklenir.
- κ ağırlıklı versiyon: Eʷ = Σ κ\_ij Y\_je / Σ κ\_ij.
- **Blok dışı versiyonlar:** E^{−EU}, i ile aynı anda AB üyesi olan partnerleri çıkarır. E^{−reg} daha sıkıdır ve aynı BM bölgesel grubundaki partnerleri çıkarır.
- **Neredeyse partner maruziyeti:** Aynı formül, N\_i yerine κ sıralamasında 11–20. sıradaki devletlerle hesaplanır (E\_near). Bu devletler i'ye neredeyse partnerler kadar benzer ama doğrudan bağları yok.

**Partner özellikleri (bağlamsal kontroller):**

- `pD_mean`: N\_i'deki partnerlerin ortalama `D_index` değeri (t−1).
- `pclose_mean`: Partnerlerin P'ye ortalama yakınlığı, yani ortalama κ(j, P) (t−1).

Bu iki değişken, partnerlerin olaydaki davranışını partnerlerin tipinden ayırmak için modele girer (Nedensellik bölümü).

### Bağımlılık bloğu (H1)

| Değişken | Tanım | Kaynak | Not |
| --- | --- | --- | --- |
| `D_pact` | i ile P arasında savunma paktı (0/1) | ATOP v5.1 | 2019–2025 için 2018 değeri taşınır; ABD için Stimson listesiyle kontrol |
| `D_dca` | i ile P arasında 1980–2010 arasında en az bir savunma işbirliği anlaşması (0/1) | Kinne DCAD | Rusya ve Çin için daha bilgilendirici |
| `D_arms_main` | t−5 ile t−1 arasında i'nin silah ithalatında (TIV) en büyük pay P'de mi (0/1) | SIPRI | Hiç ithalatı olmayan = 0 |
| `D_arms_share` | Aynı penceredeki P payı (0–1) | SIPRI | Sürekli versiyon |
| `D_exp` | i'nin ihracatında P'nin payı | IMF IMTS | Pay, hacim değil (Flores-Macías & Kreps) |
| `D_imp` | i'nin ithalatında P'nin payı | IMF IMTS |  |
| `D_aid` | P'den gelen resmi yardım / i'nin GSMH'si | OECD CRS (ABD, FR, UK); AidData (Çin) | Rusya için yok; robustluk |
| `D_index` | Bileşenlerin standartlaştırılmış ortalaması | Türetilmiş | Ana H1 testi |

H1 iki şekilde test edilir: tek bir `D_index` katsayısı ve bileşenlerin blok halinde ortak Wald testi.

### Önem (H3)

- **Ana ölçü (yalnızca ABD olayları):** Karar, t yılında ABD Dışişleri'nin "Voting Practices in the UN" raporundaki "important votes" listesindeyse S = 1.
- **Vekil ölçü (tüm patronlar):** P kararın ana sponsoruysa ya da oylama bir acil özel oturumda yapıldıysa S = 1.
- S'nin ana etkisi olay sabit etkisi tarafından emilir; modelde yalnızca D × S etkileşimi tahmin edilir.

### Kontroller

| Değişken | Tanım | Neden |
| --- | --- | --- |
| `close_kappa` | κ(i, P) oturum t−1 | Bağların zaten var olan uyumu yansıtması |
| `ideal_dist` | \|θ\_i − θ\_P\|, BSV ideal noktaları | Ajandadan arındırılmış yakınlık (robustluk) |
| `v_prev` | v\_{i,t−1} | Hareket alanı |
| `regime_gap` | \|EDI\_i − EDI\_P\|, V-Dem | Tercih benzerliği |
| `ideo_gap` | Devletin ve P'nin yürütme ideolojisi arasındaki fark | Hükümet yakınlığı (Potrafke 2009) |
| `leader_change` | i'de t−1 ile t arasında hükümet başkanı değişti mi | Tesadüfi yeniden hizalanma (Dreher & Jensen 2013; Smith 2016) |
| `m_partners` | Risk setindeki partner payı | Maruziyetin paydası |
| `log_gdp`, `log_milex` | World Bank WDI, SIPRI | Büyüklük ve kapasite |

## Tahmin modeli ve hipotez testleri

Tüm hipotezler tek bir denklemle test ediliyor: olay sabit etkili doğrusal olasılık modeli. Standart hatalar devlet ve olay düzeyinde iki yönlü kümelenir.

### Ana denklem

```latex
Y_{ie} = \alpha_e + \beta\, D_{iP,t-1} + \gamma\, E_{ie} + \delta\,\left(D_{iP,t-1} \times S_e\right) + \theta' X_{i,t-1} + \mu_{g(i)} + \varepsilon_{ie}
```

- **α\_e (olay sabit etkisi):** Patron, karar, konu, yıl ve olaydaki genel hareket oranı gibi olaya ait her şeyi emer. Kimlik, aynı olay içinde devletler arasındaki farktan gelir.
- **μ\_g (BM bölgesel grup sabit etkisi):** Coğrafi ve bölgesel eğilimleri emer. H2'nin ana robustluğunda α\_e ve μ\_g yerine olay × bölge sabit etkisi kullanılır (fixest'te event\_id^un\_region): her olayda her bölgenin ortalama hareketi düşer ve γ yalnızca aynı olayda aynı bölgedeki devletler arasındaki farktan tahmin edilir. Bu yüzden ayrı bir coğrafya katmanına gerek yok.
- **Neden devlet sabit etkisi yok:** Bağlar bir devlet içinde zamanla çok az değiştiği için devlet sabit etkisi β'yi neredeyse tamamen emer. Robustluk olarak raporlanır.
- **Neden doğrusal olasılık modeli:** Katsayılar doğrudan olasılık puanı olarak okunur, etkileşimler basittir, 209 sabit etki sorun yaratmaz. Logit (`feglm`, binomial) robustluk olarak raporlanır.
- **Sürekli değişkenler z-skoruna çevrilir**, böylece β ile γ doğrudan karşılaştırılabilir.

R'da:

```
feols(Y ~ D_index + E + D_index:S + close_kappa + v_prev + regime_gap +
        ideo_gap + leader_change + m_partners + pD_mean + pclose_mean + log_gdp + log_milex
      | event_id + un_region,
      cluster = ~ iso3 + event_id, data = panel)
```

### Testler

| Hipotez | Katsayı | Desteklenir | Aleyhte | Ek test |
| --- | --- | --- | --- | --- |
| H1 Dikey | β (D\_index); bileşenler blok halinde | β > 0 (tek yönlü, α = 0,05); ortak Wald anlamlı | β ≈ 0, ya da önceki oturumda da aynı etki (pre-trend) | Yanlış patron placebosu |
| H2 Yatay | γ (E) | γ > 0, D, yakınlık ve partner özellikleri kontrol edilmişken; olay × bölge sabit etkisiyle ve E^{−EU} ile de pozitif | γ, neredeyse partner katsayısından (γ\_near) büyük değil; ya da olaylardaki birlikte hareket temel düzeyden güçlü değil | Neredeyse partner placebosu; olay dışı temel düzey; topluluk yoğunlaşması; Bramoullé IV |
| H3 Önem | δ (D × S) | δ > 0 | δ ≤ 0 | ABD alt örneklemi (ana); vekil ölçü (ikincil) |

### Kanal karşılaştırması (araştırma sorusu)

Dört iç içe model tahmin edilir:

1. **M0:** Kontroller + sabit etkiler.
2. **M1:** M0 + dikey blok.
3. **M2:** M0 + yatay değişken.
4. **M3:** Hepsi.

Karşılaştırma üç ölçütle yapılır:

- **Standartlaştırılmış etkiler:** M3'te β ile γ arasında eşitlik Wald testi.
- **Açıklama gücü:** Within-R² artışı ve dominance (Shapley) ayrıştırması. Bu, R²'yi bloklar arasında sıraya bağlı olmadan böler (R'da `domir`).
- **Örneklem dışı tahmin:** Olayları gruplara ayıran çapraz doğrulamayla, dikey, yatay ve birleşik logit modellerinin AUC değerleri.

### Topluluk yoğunlaşması testi (H2, olay düzeyi)

Bu test, takibin oy blokları içinde yoğunlaşıp yoğunlaşmadığını regresyondan bağımsız olarak soruyor.

1. Her oturum t−1 için simetrik backbone üzerinde Leiden (modularity, γ = 1, κ ağırlıklı). 100 farklı seed ile çalıştırılır, en yüksek modularity'li bölünme seçilir. Seed'ler arası kararlılık NMI ile raporlanır.
2. Her olay için risk setindeki devletler üzerinden η²\_e hesaplanır: Y'nin topluluklar arası varyansının toplam varyansına oranı.
3. **Null dağılımı:** Y değerleri BM bölgesel grupları içinde 1.000 kez karıştırılır. Böylece coğrafya sabit tutulmuş olur ve yoğunlaşma, bölgesel benzerliğin ötesinde test edilir.
4. Raporlanan: p < 0,05 olan olayların payı, null'a göre standartlaştırılmış η² dağılımı ve Fisher birleşik p değeri.

### Patron farkı

Ana model tüm patronları havuzlar. Çin için yalnızca 23 olay olduğu için patron bazında ayrı tahmin zayıf kalır. Patron farkları D × patron ve E × patron etkileşimleriyle gösterilir.

## Nedensellik: tanımlama stratejisi

Tasarım gözlemsel; iddia edilebilecek en güçlü şey, tasarım güvenceleriyle desteklenmiş bir ilişki. Proposal'da ve sonuçlarda "etki" yerine "takip olasılığı ile ilişkili" dili kullanılmalı. Nedensel yorum yalnızca placebo testleri geçtiğinde güçlenir.

### Tahmin edilen nicelik

β şunu söyler: aynı olayda, aynı bölgede, P ile benzer yakınlıktaki ve aynı önceki oya sahip iki devletten patrona bağımlılığı bir standart sapma yüksek olanın, P yönünde hareket etme olasılığı kaç puan daha yüksek. γ aynı şeyi partner maruziyeti için söyler.

### Tasarımın zaten ortadan kaldırdıkları

- **Karara özgü sabit tercihler:** Sonuç bir değişim, düzey değil. Bir devletin o karar hakkındaki kalıcı görüşü Y'yi belirlemez.
- **Olay düzeyindeki şoklar:** α\_e, olayı herkes için değiştiren her şeyi emer, örneğin bir savaş ya da karar metninin değişmesi.
- **Aynı olay içinde ters nedensellik:** Bağlar ve partnerler t−1'den ölçülür.

### Tehditler ve karşılıkları

| Tehdit | Neden sorun | Karşılık |
| --- | --- | --- |
| Ortak şok | Devlet ile P aynı dış gelişmeye tepki verir; bağlı devletler o gelişmeye daha duyarlı olabilir | (a) Pre-trend placebo; (b) P'nin iç siyasetinden doğan switch'ler alt örneklemi; (c) yanlış patron placebosu |
| Bağların seçilimi | İttifak ve ticaret, zaten uyumlu devletlerle kurulur (Akerman & Seim 2014) | Sonuç değişim olduğu için düzey seçilimi Y'yi doğrudan belirlemez; `close_kappa` ve `ideal_dist` kontrolü; pre-trend |
| Yansıma problemi (H2) | Partnerlerin ve devletin hareketi aynı nedenden gelir; benzer devletler zaten benzer tepki verir (Manski 1993) | (a) Partner özellikleri kontrolü; (b) neredeyse partner placebosu; (c) olay dışı temel düzey; (d) olay × bölge sabit etkisi. Bramoullé IV ve permütasyon testi robustluk olarak |
| Formal koordinasyon | AB üyeleri ortak dış politika kapsamında birlikte oy verir; bu takip değil | E^{−EU} ve E^{−reg}; blok üyeliği kontrolleri |
| Devletin kendi lider değişimi | Yeni hükümet, P'den bağımsız olarak oy değiştirebilir (Smith 2016) | `leader_change` kontrolü; bu gözlemler dışarıda bırakılarak yeniden tahmin |
| Eşleştirme hatası | Metni değişmiş karar sahte switch üretir | Benzerlik eşiği 0,90'a yükseltilerek yeniden tahmin |
| Konsensüs kararları | Konsensüsten oylamaya geçiş görünmez | Kapsam sınırı olarak açıkça yazılır; UNGA-DM ile betimsel rapor |
| Çoklu test | Çok sayıda robustluk testi tesadüfi anlamlılık üretir | Üç ana hipotez önceden belirlenir; geri kalanı robustluk olarak etiketlenir |

### Placebo testleri: nasıl kodlanır

**Pre-trend placebo.** Aynı olay için sonuç bir oturum geriye kaydırılır: devlet t−2'den t−1'e, P'nin t'de gideceği yönde hareket etmiş miydi? D, t−3'ten ölçülür. β burada da pozitif çıkarsa, bağlı devletler P'yi takip etmiyor, P'den önce zaten hareket ediyordur.

**P'nin iç siyaseti alt örneklemi.** Switch'in nedeni P'nin kendi hükümet değişimiyse, takipçilerin tercihlerinden bağımsız sayılabilir. Kodlama: P'de devlet ya da hükümet başkanı değişiminden sonraki ilk oturumdaki switch'ler (ABD için 2009, 2017, 2021, 2025; Fransa ve İngiltere için parti değişimleri). Model bu alt örneklemde yeniden tahmin edilir.

**Yanlış patron placebosu.** Her olayda D, switch yapan patron için değil, başka bir patron için hesaplanır (örneğin ABD switch ettiğinde devletin Çin'e bağımlılığı). Gerçek takip varsa β yalnızca doğru patronla pozitif çıkmalı. Yanlış patronla da pozitifse, sonuç genel bir "bağlılık" eğilimini yansıtıyordur.

**Yansıma problemine üç cevap (H2).** "Benzer devletler zaten benzer hareket eder" itirazı H2'nin en ciddi tehdidi. Aşağıdaki üç test, elimizdeki veriyle bu itirazı doğrudan sınıyor.

**1. Partner özellikleri kontrolü.** Manski (1993) partnerlerden gelen etkiyi üçe ayırır: davranışları (içsel etki), özellikleri (bağlamsal etki) ve ortak gözlenmeyen faktörler. Modele partnerlerin ortalama `D_index` değeri (`pD_mean`) ve P'ye ortalama yakınlığı (`pclose_mean`) eklenir. Bu kontrollerden sonra pozitif kalan γ, partnerlerin tipinden değil o olaydaki hareketlerinden gelir.

**2. Neredeyse partner placebosu.** Benzerlik itirazı doğruysa, i'ye neredeyse aynı ölçüde benzeyen ama ilk 10'a girmeyen devletlerin hareketi de i'yi aynı ölçüde açıklamalı. `E_near`, κ sıralamasında 11–20. sıradaki devletlerle hesaplanır ve E ile aynı modele girer. Test: γ − γ\_near > 0 (Wald). Bu, kohezyon ile yapısal eşdeğerlik ayrımının (Burt 1978) H2'ye uygulanması: etki doğrudan bağtan mı geliyor, benzer konumdan mı?

**3. Olay dışı temel düzey.** Benzer devletler her zaman birlikte hareket ediyorsa, bu P'nin oyunu değiştirmediği tekrarlanan kararlarda da görülür. Panel bu kararlar için de kurulur (`event_type = 0`). Karşılaştırılabilirlik için iki örneklemde de sonuç "devlet oy değiştirdi mi" (`Y_any`), maruziyet "oy değiştiren partnerlerin payı" (`E_any`) olarak tanımlanır. İki örneklem karar sabit etkisiyle birlikte tahmin edilir ve `E_any × event_type` etkileşimi test edilir. H2, P switch ettiğinde birlikte hareketin bu temel düzeyden güçlü olacağını öngörür.

**Sınır.** Gözlemsel ağ verisinde benzerlik ile etkilenme hiçbir zaman tamamen ayrılamaz (Shalizi & Thomas 2011). İddia bu yüzden şöyle kurulur: partnerlerin hareketi, gözlenen benzerliğin, partner özelliklerinin ve normal birlikte hareketin ötesinde takibi öngörür.

### Bramoullé araç değişkeni (H2 robustluğu)

Bramoullé, Djebbari & Fortin (2009), ağlarda akran etkisinin, "arkadaşın arkadaşı olup kendisi arkadaş olmayan" düğümlerin özellikleri araç olarak kullanılarak tanımlanabileceğini gösterdi. Bizdeki karşılığı:

- **Araç:** Z\_ie = i'nin partnerlerinin partnerleri olan ama i'nin partneri olmayan devletlerin (k ∉ N\_i ∪ {i}) ortalama `D_index` değeri.
- **Mantık:** Bu devletlerin P'ye bağımlılığı i'nin partnerlerinin hareketini etkiler, ama i'yi yalnızca partnerler aracılığıyla etkiler.
- **Varsayım:** Bu devletlerin P'ye bağları i'nin davranışını doğrudan etkilemez. Bu varsayım tartışılabilir olduğu için IV robustluk olarak sunulur, ana test olarak değil.
- **Kod:** `feols(Y ~ D_index + controls | event_id + un_region | E ~ Z, cluster = ~iso3 + event_id)`. İlk aşama F istatistiği raporlanır; 10'un altındaysa sonuç zayıf araç olarak işaretlenir.

## Betimsel ağlar

İki betimsel analiz hipotez testi değil, ama projenin "kim kimi takip ediyor" sorusuna görsel cevabını ve multipleks yapının tanıtımını veriyor.

### Takipçi ağı

- **Düğümler:** Devletler + beş patron (iki kısımlı ağ).
- **Kenar:** Devlet i → patron P, ağırlık:

```latex
w_{iP} = \frac{\sum_{e \in \mathcal{E}_P} Y_{ie}}{\left|\{\, e \in \mathcal{E}_P : i \in R_e \,\}\right|}
```

- E\_P, patron P'nin olaylarıdır. Kenar yalnızca devlet P'nin en az 5 olayında risk setindeyse oluşturulur; daha azında pay güvenilmez.
- **Ölçüler:** Patronun iç gücü (in-strength) = Σ\_i w\_iP, yani takibin genişliği. Devletin dış derecesi = kaç patronu anlamlı ölçüde takip ettiği.
- **Dönemler:** 2001–2016, 2017–2024 ve 2025 ayrı çizilir. Voeten'in 2025 gözlemi bu karşılaştırmada görünür olmalı.
- **"Takip blokları":** Devletlerin takip profilleri (w\_i· vektörleri) arasındaki benzerlikten bir devlet–devlet ağı kurulur ve Leiden ile gruplanır. Bu bloklar, oy bloklarıyla (L1 toplulukları) NMI ile karşılaştırılır.

### Multipleks betimleme

- **Katman örtüşmesi:** Her oturumda L1 backbone kenarlarının kaçı aynı zamanda L2 ittifak kenarı (Jaccard). Soru: oy partnerleri ile müttefikler ne kadar aynı devletler?
- **QAP korelasyonu:** Tam κ matrisi ile ittifak matrisi arasındaki korelasyon, düğüm permütasyonuyla test edilir (Krackhardt 1988; R'da `sna::qaptest`).
- **Multislice topluluklar:** L1 ve L2 aynı düğüm kümesi üzerinde iki katman olarak alınır ve katmanlar arası bağın gücü ω ile multislice modularity optimize edilir (Mucha vd. 2010; Cranmer, Menninga & Mucha 2015). Python'da `leidenalg.optimise_partition_multiplex`. ω = 0 iki bağımsız bölünme verir, ω büyüdükçe tek bir ortak bölünmeye yakınsar. Birkaç ω değeri raporlanır.

## Veri boru hattı ve kod kitabı

Boru hattı yedi adımdan oluşuyor. 1–6. adımlar Python'da yapılır ve Parquet dosyaları üretir; 7. adım R'da modelleri tahmin eder.

### Adımlar

1. **Ham oylar → `votes_long`:** UN Digital Library verisini uzun formata çevir, Voeten verisiyle karşılaştır (hedef: %99,6 eşleşme), yokluğu eksik olarak işaretle.
2. **Eşleştirme → `recurring_map`:** Başlık normalleştirme, komite eşleşmesi, TF-IDF cosine; 0,60–0,80 aralığını elle kontrol için Excel'e dışa aktar.
3. **Olaylar → `events`:** P5'in oy değişikliklerini bul, yönü hesapla, Voeten'in ABD sayılarıyla doğrula.
4. **Ağ → `kappa`, `backbone`, `communities`:** Oturum başına ağırlıklı κ matrisi, kNN listeleri, Leiden bölünmeleri.
5. **Bağlar → `ties`:** ATOP, DCAD, SIPRI, IMF, yardım verilerini devlet × patron × yıl formatında birleştir.
6. **Panel → `panel`:** Risk setini oluştur, Y'yi hesapla, maruziyeti ve placebo maruziyetleri hesapla, bağları ve kontrolleri t−1'den ekle.
7. **Modeller (R):** `fixest` ile ana model, robustluk tabloları, `modelsummary` ile çıktı.

### Tablolar

| Tablo | Satır birimi | Ana sütunlar | Kaynak |
| --- | --- | --- | --- |
| `votes_long` | Devlet × oylama | `rcid`, `session`, `date`, `iso3`, `vote` (0/0.5/1/NA) | UN Digital Library |
| `resolutions` | Oylama | `rcid`, `title`, `title_norm`, `committee`, `sponsor`, `important_us`, `ess`, `topic` | UN Digital Library; ABD Dışişleri raporları |
| `recurring_map` | Karar çifti | `rcid_t`, `rcid_tm1`, `sim`, `match_status` | Türetilmiş |
| `events` | Olay | `event_id`, `patron`, `rcid_t`, `rcid_tm1`, `session`, `dir`, `S`, `p_govchange` | Türetilmiş |
| `kappa` | Devlet çifti × oturum | `session`, `i`, `j`, `kappa_w`, `pi`, `n_shared` | Türetilmiş |
| `backbone` | Devlet × partner × oturum | `session`, `i`, `j`, `rank`, `kappa_w` | Türetilmiş |
| `communities` | Devlet × oturum | `session`, `iso3`, `comm`, `modularity` | Türetilmiş |
| `edges` | Kenar × yıl | `t`, `layer`, `i`, `j`, `weight`, `directed` | Tüm katmanlar |
| `ties` | Devlet × patron × yıl | `iso3`, `patron`, `year`, `D_pact`, `D_dca`, `D_arms_main`, `D_arms_share`, `D_exp`, `D_imp`, `D_aid` | ATOP, DCAD, SIPRI, IMF, OECD, AidData |
| `panel` | Devlet × olay | Aşağıdaki tüm değişkenler | Türetilmiş |

### `panel` değişkenleri

| Değişken | Tanım | Tip | Zaman |
| --- | --- | --- | --- |
| `event_id`, `iso3`, `patron` | Kimlikler | Metin | – |
| `Y` | P yönünde hareket | 0/1 | t |
| `Y_ord` | −1 / 0 / 1 / 2 | Sıralı | t |
| `Y_delta` | d · (v\_t − v\_{t−1}) | Sürekli | t |
| `v_prev` | Önceki oy | 0/0.5/1 | t−1 |
| `E`, `E_w`, `E_noEU`, `E_noreg` | Partner maruziyeti ve versiyonları | 0–1 | t (partnerler t−1) |
| E\_near | κ sıralamasında 11–20. sıradaki devletlerle hesaplanan placebo maruziyet | 0–1 | t (liste t−1) |
| pD\_mean, pclose\_mean | Partnerlerin ortalama D\_index değeri ve P'ye ortalama yakınlığı | Sürekli | t−1 |
| Y\_any, E\_any, event\_type | Olay dışı temel düzey: devlet oy değiştirdi mi; oy değiştiren partner payı; P switch etti mi | 0/1; 0–1; 0/1 | t |
| `Z_iv` | Partnerlerin partnerlerinin ortalama D\_index'i | Sürekli | t−1 |
| `m_partners` | Risk setindeki partner payı | 0–1 | t |
| `D_*`, `D_index` | Bağımlılık bileşenleri ve endeks | Karışık / z | t−1 |
| `D_index_wrong` | Yanlış patron için endeks | z | t−1 |
| `S` | Önem | 0/1 | t |
| `close_kappa`, `ideal_dist` | P'ye yakınlık | Sürekli | t−1 |
| `regime_gap`, `ideo_gap` | Rejim ve ideoloji farkı | Sürekli | t−1 |
| `leader_change` | Devlette lider değişimi | 0/1 | t−1 → t |
| `log_gdp`, `log_milex` | Büyüklük | Sürekli | t−1 |
| `un_region`, `eu`, `nam`, `oic` | Blok üyelikleri | Kategorik / 0/1 | t |
| `comm` | Leiden topluluğu | Kategorik | t−1 |
| `p_govchange` | Switch P'nin hükümet değişiminden sonra mı | 0/1 | t |

### Paketler

- **Python:** `pandas`, `numpy`, `pyarrow`, `scikit-learn` (TF-IDF), `python-igraph`, `leidenalg`, `networkx` (dışa aktarma), `geopandas`.
- **R:** `fixest`, `modelsummary`, `marginaleffects`, `domir`, `sna` (QAP), `countrycode`, `peacesciencer` (FPSIM, ATOP), `ggplot2`, `ggraph`.

## Araç–analiz eşlemesi

Her araç tek bir işi üstleniyor; böylece CV'de her biri farklı bir beceriyi gösteriyor.

| Araç | Analiz | Çıktı |
| --- | --- | --- |
| Excel | Olay listesi ve patron × yıl pivotları; eşleştirmede elle kontrol edilen vakalar; ağırlıklı κ'nın formüllerle çalışan örneği; veri kapsama matrisi | Betimsel tablolar, κ hesap sayfası |
| GIS (QGIS / `geopandas`) | Şubat 2025 Ukrayna olayının Y haritası; patron başına takip oranı haritaları; takip oranlarında Local Moran's I (bölgesel kümelenmenin görsel kontrolü) | Choropleth ve LISA haritaları |
| Python | Boru hattı (1–6. adımlar), κ ve backbone, Leiden ve permütasyon testi, multislice topluluklar, ağ çizimleri (Gephi'ye dışa aktarım) | Parquet tabloları, ağ figürleri |
| R | Ana model ve robustluk, katsayı grafiği, iç içe model karşılaştırması, H3 için marjinal etkiler, takipçi ağı (`ggraph`), QAP | Regresyon tabloları, yayın kalitesinde figürler |
| Tableau Public (opsiyonel) | 209 olayın filtrelenebilir görünümü | CV'ye konabilecek link |

## Kaynakça

Literatür taramasının ayrıntıları "Kavramsal Çerçeve ve Kodlama Kararları" dokümanında. Burada yalnızca bu tasarımda doğrudan kullanılanlar var.

- Akerman, A. & Seim, A. (2014). The global arms trade network 1950–2007. *Journal of Comparative Economics* 42(3).
- Bailey, M., Strezhnev, A. & Voeten, E. (2017). Estimating dynamic state preferences from United Nations voting data. *Journal of Conflict Resolution* 61(2).
- Bramoullé, Y., Djebbari, H. & Fortin, B. (2009). Identification of peer effects through social networks. *Journal of Econometrics* 150(1).
- Burt, R. (1978). Cohesion versus structural equivalence as a basis for network subgroups. *Sociological Methods & Research* 7(2).
- Cranmer, S., Menninga, E. & Mucha, P. (2015). Kantian fractionalization predicts the conflict propensity of the international system. *PNAS* 112(38).
- Dreher, A. & Jensen, N. (2013). Country or leader? Political change and UN General Assembly voting. *European Journal of Political Economy* 29.
- Dreher, A., Nunnenkamp, P. & Thiele, R. (2008). Does US aid buy UN General Assembly votes? *Public Choice* 136.
- Flores-Macías, G. & Kreps, S. (2013). The foreign policy consequences of trade. *Journal of Politics*.
- Gartzke, E. (1998). Kant we all just get along? *American Journal of Political Science*.
- Häge, F. (2011). Choice or circumstance? Adjusting measures of foreign policy similarity for chance agreement. *Political Analysis* 19.
- Häge, F. & Hug, S. (2016). Consensus decisions and similarity measures in international organizations. *International Interactions* 42(3).
- Kinne, B. (2020). The Defense Cooperation Agreement Dataset (DCAD). *Journal of Conflict Resolution* 64(4).
- Kivelä, M. vd. (2014). Multilayer networks. *Journal of Complex Networks* 2(3).
- Krackhardt, D. (1988). Predicting with networks: nonparametric multiple regression analysis of dyadic data. *Social Networks* 10(4).
- Lake, D. (2009). *Hierarchy in International Relations*. Cornell University Press.
- Manski, C. (1993). Identification of endogenous social effects: the reflection problem. *Review of Economic Studies* 60(3).
- Mucha, P., Richardson, T., Macon, K., Porter, M. & Onnela, J.-P. (2010). Community structure in time-dependent, multiscale, and multiplex networks. *Science* 328(5980).
- Pauls, S. & Cranmer, S. (2017). Affinity communities in United Nations voting. *Physica A* 484.
- Potrafke, N. (2009). Does government ideology influence political alignment with the US? *Review of International Organizations* 4(3).
- Shalizi, C. & Thomas, A. (2011). Homophily and contagion are generically confounded in observational social network studies. Sociological Methods & Research 40(2).
- Smith, A. (2016). Leader turnover, institutions, and voting at the UN General Assembly. *Journal of Conflict Resolution* 60(1).
- Steglich, C., Snijders, T. & Pearson, M. (2010). Dynamic networks and behavior: separating selection from influence. *Sociological Methodology* 40(1).
- Thacker, S. (1999). The high politics of IMF lending. *World Politics* 52(1).
- Traag, V., Waltman, L. & van Eck, N. (2019). From Louvain to Leiden: guaranteeing well-connected communities. *Scientific Reports* 9.
- Voeten, E. (2026, 17 Şubat). [The world isn't moving away from the U.S. The U.S. is moving away from the world](https://goodauthority.org/news/the-world-isnt-moving-away-from-the-u-s-the-u-s-is-moving-away-from-the-world/). *Good Authority*.
