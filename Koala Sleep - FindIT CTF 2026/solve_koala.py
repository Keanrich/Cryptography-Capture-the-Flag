from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import hashlib

BLOCK_SIZE = 16

def permute(n, s):
    indices = list(range(n))
    state = s
    for i in range(n - 1, 0, -1):
        state = (state * 0x41c64e6d + 12345) & 0xFFFFFFFF
        j = (state ^ (state >> 16)) % (i + 1)
        indices[i], indices[j] = indices[j], indices[i]
    return indices

def get_last_block_source(n, seed):
    """
    OPTIMASI: mapping[n-1] hanya ditentukan oleh iterasi PERTAMA permutasi.
    Karena setelah i=n-1, nilai j selalu <= i < n-1, jadi indices[n-1] tidak pernah
    disentuh lagi. Kita bisa hitung dalam O(1) tanpa loop penuh!
    """
    state = seed
    state = (state * 0x41c64e6d + 12345) & 0xFFFFFFFF
    j = (state ^ (state >> 16)) % n
    return j  # mapping[n-1] = j

def reverse_permute(shuffled_blocks, mapping):
    n = len(shuffled_blocks)
    original = [None] * n
    for i, pos in enumerate(mapping):
        original[i] = shuffled_blocks[pos]
    return original

def main():
    with open("koala-enc.ppm", "rb") as f:
        line1 = f.readline()
        line2 = f.readline()
        line3 = f.readline()
        header = line1 + line2 + line3
        encrypted_data = f.read()

    parts = line2.split()
    width, height = int(parts[0]), int(parts[1])
    expected_size = width * height * 3
    print(f"[*] Image size: {width}x{height}, expected pixel bytes: {expected_size}")

    n = len(encrypted_data) // BLOCK_SIZE
    shuffled_blocks = [encrypted_data[i*BLOCK_SIZE:(i+1)*BLOCK_SIZE] for i in range(n)] 
    # file enkripsi dipotong tiap 16 byte, dibaca apa adanya dari disk, dalam urutan yang sudah diacak.
    print(f"[*] Total blocks: {n}")
    print(f"[*] Brute-forcing dengan FAST padding check (O(1) per seed)...")

    found_seed = None
    for seed in range(65536):
        seed_bytes = seed.to_bytes(2, 'big')
        key = hashlib.sha256(seed_bytes).digest()[:16]
        cipher = AES.new(key, AES.MODE_ECB)

        # STEP 1: Cek padding blok terakhir saja (O(1) permutation!)
        last_src = get_last_block_source(n, seed)
        decrypted_last = cipher.decrypt(shuffled_blocks[last_src])

        # Validasi PKCS7 padding
        pad_byte = decrypted_last[-1]
        if pad_byte < 1 or pad_byte > 16:
            continue
        if decrypted_last[-pad_byte:] != bytes([pad_byte] * pad_byte):
            continue

        # STEP 2: Kandidat ditemukan! Verifikasi ukuran setelah full decrypt
        print(f"\n[+] Kandidat seed ditemukan: {seed}, verifikasi full decrypt...")

        mapping = permute(n, seed)
        original_blocks = reverse_permute(shuffled_blocks, mapping)

        cipher2 = AES.new(key, AES.MODE_ECB)
        decrypted_raw = b"".join(cipher2.decrypt(b) for b in original_blocks)

        try:
            decrypted = unpad(decrypted_raw, BLOCK_SIZE)
            if len(decrypted) == expected_size:
                found_seed = seed
                print(f"[+] CONFIRMED! Secret seed = {seed}")
                with open("koala-decrypted.ppm", "wb") as f:
                    f.write(header + decrypted)
                print(f"[+] File saved: koala-decrypted.ppm")
                break
        except Exception:
            print(f"    Padding valid tapi size salah, lanjut...")

    if found_seed is None:
        print("[-] Seed tidak ditemukan.")

if __name__ == "__main__":
    main()