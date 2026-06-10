Sebuah koala genius yang mengantuk telah mengenkripsi foto rahasianya sebelum tidur. Ia mengklaim bahwa memorinya hanya cukup untuk mengingat angka 16-bit, dan menggunakan satu angka tersebut untuk mengenkripsikan semuanya — mulai dari key AES hingga posisi setiap blok gambar. Kita diminta untuk memulihkan gambar aslinya.

Hint: "...time is precious, don't get stuck counting the entire forest if you only need to check the tips of the leaves." 

Attachment:  
1 file ppm koala\_enc.ppm

**from** Crypto**.**Cipher **import** AES  
**from** Crypto**.**Util**.**Padding **import** pad  
**import** os  
**import** hashlib  
**import** random

*\# W, H \= 1920, 800*  
BLOCK\_SIZE **\=** 16

**def** permute(**n,** **s**)**:**  
    indices **\=** list(range(n))  
    state **\=** s  
    **for** i **in** range(n **\-** 1**,** 0**,** **\-**1)**:**  
        state **\=** (state **\*** 0x41c64e6d **\+** 12345) **&** 0xFFFFFFFF  
        j **\=** (state **^** (state **\>\>** 16)) **%** (i **\+** 1)  
        indices\[i\]**,** indices\[j\] **\=** indices\[j\]**,** indices\[i\]  
    **return** indices

**def** main()**:**  
    **with** open("plain.ppm"**,** "rb") **as** f**:**  
        header **\=** f**.**readline() **\+** f**.**readline() **\+** f**.**readline()  
        pixel\_data **\=** f**.**read()  
         
    secret\_seed **\=** random**.**randint(0**,** 65535)  
    seed\_bytes **\=** secret\_seed**.**to\_bytes(2**,** 'big')  
    key **\=** hashlib**.**sha256(seed\_bytes)**.**digest()\[**:**16\]  
    cipher **\=** AES**.**new(key**,** AES**.**MODE\_ECB)

    raw **\=** pad(pixel\_data**,** BLOCK\_SIZE)  
    blocks **\=** \[cipher**.**encrypt(raw\[i**:**i**\+**BLOCK\_SIZE\]) **for** i **in** range(0**,** len(raw)**,** BLOCK\_SIZE)\]  
     
    n **\=** len(blocks)  
    mapping **\=** permute(n**,** secret\_seed)  
     
    shuffled\_blocks **\=** \[None\] **\*** n  
    **for** i**,** pos **in** enumerate(mapping)**:**  
        shuffled\_blocks\[pos\] **\=** blocks\[i\]  
     
    **with** open("koala-enc.ppm"**,** "wb") **as** f**:**  
        f**.**write(header **\+** b""**.**join(shuffled\_blocks))

**if** \_\_name\_\_ **\==** "\_\_main\_\_"**:**  
    main()

Dalam kode dapat terlihat bahwa:

1. Secret seed dibangun secara acak dengan random.randint (0, 65535\) \-\> 16 bit  
2. Kunci dibangun dari secret seed ini dengan mode AES-ECB

Kelemahan yang ada:

1. Seed yang hanya 16 bit bisa saja dilakukan bruteforce  
2. AES-ECB bersifat deterministi, plaintext yang sama akan menghasilkan ciphertext yang sama, tidak ada IV, sehingga proses dekripsi hanya perlu kunci yang benar   
3. Seed yang sama digunakan untuk key AES dan permutasi blok, jadi menemukan seed permutasi sama dengan seed AES

Solusi:

1. Cara brute force bisa dengan mencoba semua 65536 seed untuk setiap seed dilakukan permutasi balik dan dekripsi. \-\> tapi ini memiliki masalah, misal untuk setiap iterasi permutasi diperlukan m kali (288.000 iterasi) dan terdapat n blok (2888.001) yang harus didekripsi maka kompleksitas untuk menjalankan bruteforce adalah O(N x M) atau dalam konteks ini O(n2) ini sangat lama, perlu ada optimisasi  
2. Berdasarkan algoritma permutasi blok akhir dari pesan terenkripsi tidak berubah, jadi untuk mengetahui apakah seed benar cukup cek padding dari blok terakhir aja. Pada cara ini mapping\[n-1\] hanya bergantung pada iterasi pertama saja, dan bisa dihitung dalam waktu konstan O(1) dikarenakan Pada iterasi pertama (i \= n-1), terjadi swap antara indices\[n-1\] dan indices\[j\]. Pada semua iterasi berikutnya (i \< n-1), nilai j selalu ≤ i \< n-1, sehingga indices\[n-1\] TIDAK PERNAH disentuh lagi  
     
   def get\_last\_block\_source(n, seed):  
       state \= seed  
       state \= (state \* 0x41c64e6d \+ 12345\) & 0xFFFFFFFF  
       j \= (state ^ (state \>\> 16)) % n  
       return j  \# mapping\[n-1\] \= j  
     
   Kemudian untuk aplikasi solusi ini jadi:   
     
1. Sebelum itu pastikan file ppm bisa terbaca ya

   BLOCK\_SIZE \= 16 

   

   with open("koala-enc.ppm", "rb") as f:

           line1 \= f.readline()

           line2 \= f.readline()

           line3 \= f.readline()

           header \= line1 \+ line2 \+ line3

           encrypted\_data \= f.read()

   

2. Memotong pesan menjadi 16 bagian

   n \= len(encrypted\_data) // BLOCK\_SIZE

   shuffled\_blocks \= \[encrypted\_data\[i\*BLOCK\_SIZE:(i+1)\*BLOCK\_SIZE\] for i in range(n)\]

   

3. Kemudian brute force untuk di check last block nya

   found\_seed \= None

       for seed in range(65536):

           seed\_bytes \= seed.to\_bytes(2, 'big')

           key \= hashlib.sha256(seed\_bytes).digest()\[:16\]

           cipher \= AES.new(key, AES.MODE\_ECB)

   

4. Cek padding blok terakhir saja (O(1) permutation\!)

           last\_src \= get\_last\_block\_source(n, seed)

           decrypted\_last \= cipher.decrypt(shuffled\_blocks\[last\_src\])

   

           \# Validasi PKCS7 padding

           pad\_byte \= decrypted\_last\[-1\]

           if pad\_byte \< 1 or pad\_byte \> 16:

               continue

           if decrypted\_last\[-pad\_byte:\] \!= bytes(\[pad\_byte\] \* pad\_byte):

               Continue

   

5. Kalau berhasil atau 2 kondisi ini continue bisa lakukan permutasi untuk mappingnya dan reverse permute untuk mendapatkan original block, kemudian di dekripsi secara full 

   mapping \= permute(n, seed)

   original\_blocks \= reverse\_permute(shuffled\_blocks, mapping)

   

   cipher2 \= AES.new(key, AES.MODE\_ECB)

   decrypted\_raw \= b"".join(cipher2.decrypt(b) for b in original\_blocks)

   

   

6. Kemudian tulis hasil dekripsi ke file ppm baru

           try:

               decrypted \= unpad(decrypted\_raw, BLOCK\_SIZE)

               if len(decrypted) \== expected\_size:

                   found\_seed \= seed

                   print(f"\[+\] CONFIRMED\! Secret seed \= {seed}")

                   with open("koala-decrypted.ppm", "wb") as f:

                       f.write(header \+ decrypted)

                   print(f"\[+\] File saved: koala-decrypted.ppm")

                   Break

   

7. Selanjutnya setelah mendapatkan decrypted ppm bisa memasukannya ke jumpshare ppm reader: [https://jumpshare.com/viewer/ppm](https://jumpshare.com/viewer/ppm)

   ![][image1]

   

[image1]: <data:image/png;base64,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7LbbbtVwG3bVVVd1rHNcfi+6JQpWb3tvr6I+qmXq9a677qqGz5o1q62NXv3qV3csM87LD6vzlre8Ja1jNzb/K664oprW9ivVrS5RMOqHL33pS6vpFBrut0+vhj1RGKiD+8bcd999ix/84Afl6xe/+MW2Mhq2zz77FPvvv3/x8pe/vBz2jW98o3jooYfKy2YnnnhiumHUEJpeBwB1Is1HjTaURCHWWZTwWMT1tbKqgzJW62x2qfGVr3xltfF9B1N57dxxWfqsZMIv78Ybb+xYnvGJQrbj+WVnbAfWq64kxPHytre9rWxbtbX4A83uu+9eDd9mm23a1tWGy0c+8pGq4/qDhraHldf4hx9+uBqnS2m2rK9+9avVcG2zVVddtarfpptuWg63bWDh18GfzLSNemmbOn19fWUSonrqRKkrH8cff3yx8cYbd5SNEcdr+TFiGVEbfOc73yluuOGG8vKtkqtbbrml2Hvvvdu+vWeJgr45qy11JetrX/vakNbb0/Q6CSrUrttuu23bcv38rZ19X1h33XWreei+s+6vHnXUUUPeJt7LXvayql7af31/iImC+PE63miY1cHCJ+G68mjjtb9omPWtj370o9V8rT/7z/Zq8zKxTvKjH/2o+Pvf/172VbWRnrtaf/31y3F+/1PYOvjbjHrVvmXLUB192+r44beJxr3mNa8ppk+fXvaV+A1bCcj1119f9vnf//73xate9aq2+sbkwI/T5xixTC+yREHzesUrXlGti45V3//+98vhn/nMZ6r20atP7n2ip7j66qvblqf2Pumkk4prr7227DtqQ52XtP/rVkasnww1UVD7vetd76r62gMPPNBW726Jgk0/lOVGw54odKuMfXu0zxZa4XjrQWHZ+oc+9KFiyZIlbQd125C+A9qrb0jLGuXCCy+splf45XVLFCIdkH3E8VYXXfqzuih04hjKjhC/4fhEIfKJgta97jJz3U4b+R3ls5/9bMd40cnIr5/maQcGfw9WbRkPYhY2r1122aVaZtyumvaAAw6oprGDm9/eouFqc1uWDm4WdjlZMXbs2LZprZ8deOCBHevYjdVBBw2F73cW9t7XN0bdfGPE8UqsfXv50GddxrXyPlHQer797W93pZuhaf70pz911KVXqpPdctAydABTHXzEPhfX87DDDmt7NsDC+kNcZi+sL1i9NH8dh/yxpC5R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>