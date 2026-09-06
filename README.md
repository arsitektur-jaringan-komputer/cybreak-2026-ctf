# CYBREAK 2026 CTF CHALLENGES

## Overview

Repository ini digunakan untuk dokumentasi dan tracking challenge CTF untuk CYBREAK 2026. Setiap probset harus mengimplementasi peraturan yang dipaparkan pada section-section berikut.

## General Rules

1. Challenge yang dibuat disesuaikan dengan pembagian probset di masing-masing kategori challenge.
2. Challenge yang dibuat dilarang untuk menyinggung, dan/atau memiliki konten yang isinya mengenai SARA/Politik/Agama/Bad Words, dan/atau konten lainnya yang melanggar etika digital.
3. Probset bertanggung jawab atas setiap challenge yang dibuat.

## Technical Rules

1. Format flag CYBREAK 2026 adalah `CYB26{.+}`.
2. Setiap probset wajib melakukan uji testing challenge yang dibuat dan memastikan challenge tersebut benar-benar dapat dikerjakan.
3. Setiap probset dilarang membuat challenge dengan sifat **guessy**.
4. Setiap challenge yang memerlukan sebuah connection service wajib menggunakan **docker** dan **docker compose** sebagai otomasi dari docker tersebut.
5. Challenge yang diupload dalam repository ini harus mengikuti aturan struktur folder yang telah ditentukan.

## Folder Structure

Kategori challenge berada langsung di root repositori. File `kona.yaml` di root
menyimpan konfigurasi global Konata untuk sinkronisasi ke rCTF, sedangkan setiap
challenge memiliki `kona.yaml` sendiri yang berisi metadata, flag, attachment,
dan endpoint challenge.

```text
cybreak-2026-ctf/
├── .github/
│   └── workflows/
│       └── sync-challenges.yaml
├── crypto/
├── forensics/
├── pwn/
├── reverse/
├── web/
├── kona.yaml
└── README.md
```

Berikut adalah struktur folder untuk setiap challenge:

```text
<category>/
└── <name>/
    ├── release/
    │   └── ...
    ├── source/
    │   └── <name>/
    │       └── ...
    ├── poc/
    │   └── ...
    ├── kona.yaml
    └── README.md
```

Penjelasan:

1. **\<name>** adalah nama challenge yang akan dibuat.
2. **release** adalah folder untuk attachment yang akan diberikan ke peserta.
3. **source** adalah folder yang digunakan menyimpan source code challenge asli, dan jika service maka folder ini yang akan dideploy ke server.

> Kenapa harus ada \<name> lagi di source?
> Untuk menghindari conflict docker compose agar tidak ter-sync satu sama lain (🥲)

4. **poc** adalah folder yang isinya adalah penjelasan cara solve dari setiap challenge **(wajib)**.
5. **kona.yaml** berisi konfigurasi challenge yang akan disinkronkan ke rCTF.
6. **README.md** digunakan untuk memberikan keterangan setiap challenge tersebut. Berikut template README.md yang dapat digunakan.

```md
# <name>

## Author

(username discord)

## Difficulty

Easy/Medium/Hard

## Description

lorem ipsum dolor sit amet.

## Flag

CYB26{sample}
```

## tia 💖

# Challenges

> Untuk Author gunakan username Discord

| Name          | Author       | Difficulty | Category |
| ------------- | ------------ | ---------- | -------- |
| DB Administrator | nbl.irwn     | Easy       | Web      |
| classroom     | abdiery      | Medium     | Web      |
|               | rootkids     | Hard       | Web      |
| i LINK summon!| lylera       | Easy       | Pwn      |
| intoretlib    | lylera       | Medium     | Pwn      |
|               | mirai        | Hard       | Pwn      |
|     Viewer    | kokguebitici | Easy       | Forensic |
| nodemation    | UrSourceCode | Medium     | Forensic |
| dont be like that crazy | pujow        | Hard       | Forensic |
|               | UrSourceCode | Easy       | Reverse  |
| Ziggy Zagga   | djumanto     | Medium     | Reverse  |
| stop, wait a minute | \_\_honque   | Hard       | Reverse  |
| I CAST ARCANE LOCK... TWICE! | tsakuyaiba   | Easy       | Crypto   |
|               | dailycisea   | Medium     | Crypto   |
|               | tsakuyaiba   | Hard       | Crypto   |
