**RSA common Modulo Attack**

Soal: George droid hendak pulang kembali ke agartha setelah bekerja di kebun sawitnya, di tengah perjalanannya kembali ke agartha, dia lupa secret phrase untuk masuk ke agratha, namun bahlinus, si penjaga pintu agartha, tau droid suka lupa, jadi dia memberi droid catatan berisi sandi aneh, RSA modulus, yang berisikan secret phrasenya. 

release.txt 

n \= 65621244306653319670872009812479216556253539637757012684247326929337446029691949229830476009336324085576381980962409932835777704841875948755620309035826526718252935851707644029182010811923912024332263063320474435206957030905287233900554131266746644303012869033868346154962019095877474062849704039936163171519  
   
e1 \= 3  
c1 \= 4105931817714585546497262196126228765774747581873311887305453434266838391287108553391387157504909553136096865866521360681945219809348271859677395206127927734410477669438652581050897860699569762295858375013954260208805208594575707901219384284893069846994938217  
   
e2 \= 65537  
c2 \= 5243776788607977912607186503410037199569145142332695425831937859544540040996262696184528670956624577919073391021809450507327272297435046801815065538981326146894350676101027549009511804525444015269785480390765263800156021463103944845372299272838235762577979029844373619729965521134404669451262632798052638846

Disoal ini dijelaskan bahwa ada scretphase yang menggunakan RSA, dan didalam attachment terdapat 1 nilai n (kemungkinan nilai modulusnya) 2 ciphertext dengan 2 kunci berbeda. Secara teori RSA memiliki kunci publik dan privat dan kunci yang diberikan kemungkinan besar adalah kunci publiknya dan secret phasenya adalah kunci privatnya. Dalam RSA terdapat serangan common modulus attack yang dimana modulus dan pesan yang dienkripsi digunakan secara berulang, hal ini menyebabkan pesan asli dapat di-*retrieve*

Syarat dari serangan ini adalah   
gcd(e1, e2) \= 1  
gcd(3, 65537\) \= 1

Kemudian serangan dilanjutkan dengan mencari r dan s  
Karena rumus utama untuk mendapatkan pesan asli adalah 

Cr1 x Cs2 \= mre1 \+ se2

Jika gcd(e1, e2) \= 1 maka re1\+ se2 \= 1

m \= Cr1 x Cs2 

R dan S bisa didapatkan dengan melakukan perhitungan extended euclidean algorithm dimana r merupakan remaider hasil bagi, dan s merupakan keofisien bezout yang merupakan pengalinya

Extended euclidean algorithm di python

**def** extended\_gcd(**a,** **b**)**:**  
    **if** a **\==** 0**:**  
        **return** b**,** 0**,** 1  
     
    gcd**,** x1**,** y1 **\=** extended\_gcd(b **%** a**,** a)  
    r **\=** y1 **\-** (b **//** a) **\*** x1  
    s **\=** x1  
     
    **return** gcd**,** r**,** s

Untuk perkalian C1 dan C2  
**def** mod\_exp(**base,** **exp,** **mod**)**:**  
    **if** exp **\<** 0**:**  
        base **\=** pow(base**,** **\-**1**,** mod)  
        exp **\=** **\-**exp  
    **return** pow(base**,** exp**,** mod)

m **\=** (mod\_exp(c1**,** r**,** n) **\*** mod\_exp(c2**,** s**,** n)) **%** n

Pada titik ini, pesan sudah berhasil didapatkan tetapi perlu ada step lanjutan dalam kriptografi modern pesan merupakan bentuk hex maka perlu diubah ke bytes, dan di decode

*\# STEP 3: convert ke bytes*  
hex\_msg **\=** format(m**,** 'x')  
**if** len(hex\_msg) **%** 2**:**  
    hex\_msg **\=** '0' **\+** hex\_msg

raw **\=** binascii**.**unhexlify(hex\_msg)

print("\[+\] Raw:"**,** raw)

*\# STEP 4: REMOVE PKCS\#1 v1.5 padding*  
*\# format: 00 02 ... 00 MESSAGE*

**if** raw**.**startswith(b'\\x00\\x02')**:**  
    msg **\=** raw**.**split(b'\\x00'**,** 2)\[**\-**1\]  
**else:**  
    msg **\=** raw

print("\[+\] Message:"**,** msg)  
print("\[+\] Decode:"**,** msg**.**decode())

s **\=** msg  
print(base64**.**b64decode(s))

Maka flag dari challenge ini adalah  
\[+\] Raw: b'RmluZElUQ1RGe1BBNVNXMFJETlk0XzEyMzR9'  
\[+\] Message: b'RmluZElUQ1RGe1BBNVNXMFJETlk0XzEyMzR9'  
\[+\] Decode: RmluZElUQ1RGe1BBNVNXMFJETlk0XzEyMzR9  
b'FindITCTF{PA5SW0RDNY4\_1234}'

