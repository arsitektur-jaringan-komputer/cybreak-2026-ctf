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

Dikarenakan CYBREAK 2026 hanya 1 ronde, repositori hanya memiliki 1 subfolder yaitu **challenges**, yang masing-masing di dalamnya ada kategorisasi folder sebagai berikut

```
challenges/
├── crypto
├── forensic
├── pwn
├── reverse
└── web
```

Berikut adalah struktur folder untuk setiap challenge yang ada

```
<name>/
├── release/
│   └── ...
├── source/
│   └── <name>/
│       └── ...
└── poc/
    └── ...
└── README.md
```

Penjelasan:

1. **\<name>** adalah nama challenge yang akan dibuat.
2. **release** adalah folder untuk attachment yang akan diberikan ke peserta.
3. **source** adalah folder yang digunakan menyimpan source code challenge asli, dan jika service maka folder ini yang akan dideploy ke server.

> Kenapa harus ada \<name> lagi di source?
> Untuk menghindari conflict docker compose agar tidak ter-sync satu sama lain (🥲)

4. **poc** adalah folder yang isinya adalah penjelasan cara solve dari setiap challenge **(wajib)**.
5. **README.md** digunakan untuk memberikan keterangan setiap challenge tersebut. Berikut template README.md yang dapat digunakan.

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
