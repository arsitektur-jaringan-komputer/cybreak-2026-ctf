# 『intoretlib』

(kinda lazy to make my own template... so here is simple)

This challs is simple. Afterall i let you allow bypass the warning and this binary is strip, so here is the step:

```asm
0040124a    int64_t sub_40124a(int32_t* arg1)

00401271        char var_28[0x20]
00401271        
00401271        if (fgets(buf: &var_28, n: 0x14, fp: stdin) == 0)
00401273            return 0
00401273        
00401290        var_28[strcspn(&var_28, "\n")] = 0
00401290        
004012a3        if (sub_40119f(&var_28) != 0)
004012cb            *arg1 = atoi(nptr: &var_28)
004012cd            return 1
004012cd        
004012af        puts(str: "Blacklisted input detected! Numbers only.")
004012b4        return 0
```

It will check all your input. If there is any string text => got blacklist. So only number. 

After that, you can read from here: https://learn.microsoft.com/en-us/cpp/cpp/integer-limits?view=msvc-170 to gain max value of int

after you know the maximum value of int from website, you can overflow it and gain some buffer overflow after it:

```asm
004012d4    int32_t sub_4012d4()

004012eb        printf(format: "How many numbers do you want to enter?: ")
004012f7        int32_t var_3c
004012f7        int32_t result = sub_40124a(&var_3c)
004012f7        
004012fe        if (result == 0)
00401352            return result
00401352        
00401309        if (var_3c + 2 s> 0xc)
00401315            return puts(str: "Too many numbers! Max is 10.")
00401315        
0040132b        printf(format: "Enter your numbers as raw bytes now: ")
00401349        void buf
00401349        return read(fd: 0, &buf, nbytes: sx.q(var_3c) << 2)
```

Overflow until the offset is 56, then you can escalate to ret2lib using old ways: https://ir0nstone.gitbook.io/notes/binexp/stack/aslr/ret2plt-aslr-bypass 

leaks the puts, then you can get shell. So there are 2 ways to gain shell. using double ret or rdi directly instead. Also i gave `libc` and `ld` too to solve it on local first!

# 『source:』

- [basic int maximum](https://learn.microsoft.com/en-us/cpp/cpp/integer-limits?view=msvc-170)
- [ret2lib bypass aslr](https://ir0nstone.gitbook.io/notes/binexp/stack/aslr/ret2plt-aslr-bypass )
