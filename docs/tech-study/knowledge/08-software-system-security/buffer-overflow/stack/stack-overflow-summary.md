---
title: 栈溢出利用思路总结
description: 栈溢出利用思路总结，按 NX/Canary/PIE 与 system 入口等条件分类
tags: [栈溢出, 利用思路, rop, pwn]
status: 已完成
finish-date: 2026-10-12
difficulty: 困难
---

# 栈溢出利用思路总结

## 没有NX、stack canary、PIE
>如果缓冲区足够大可以直接在栈上改缓冲区直接构造shellcode，然后将RA覆盖成shellcode的地址

```
RA                 shellcode地址
|                       |
ebp                    ···
|                       |
···                  填充数据
|                       |
···                 shellcode
|                       |
···                    ···
|                       |
buf起始               填充数据   
```

## 有NX，没有stack canary、PIE
### 程序本身就执行了系统调用（call system）
#### 程序中含有类似/bin/sh字符串
>直接将RA覆盖为call system的地址，并传参/bin/sh的地址
```
参数               /bin/sh字符串地址
|                       |
RA                 call system地址
|                       |
ebp                    ···
|                       |
···                  填充数据
|                       |
···                    ··· 
|                       |
···                    ···
|                       |
buf起始               填充数据   
```

#### 程序中不含类似/bin/sh字符串
>在数据段中找到空白可写的位置，第一次溢出劫持RA手动调用gets函数将/bin/sh字符串写入数据段，并将RA指向call system的地址，传参刚刚写入/bin/sh的地址

```
ebp+16          已经写入的/bin/sh的地址（bss_addr）
|
ebp+12          准备写入/bin/sh的地址（bss_addr）
|
ebp+8             call system地址
|                       |
RA                   gets入口地址
|                       |
ebp                    ···
|                       |
buf起始               填充数据   

```

###  程序本身没有直接执行系统调用（call system）但有system的入口地址
#### 程序中有/bin/sh字符串
>直接劫持RA为system入口地址并手动构造返回地址（不重要）和参数（/bin/sh的地址）

```
ebp+12              /bin/sh的地址
|                       |
ebp+8               system的返回地址
|                       |
RA                  system入口地址
|                       |
ebp                    ···
|                       |
buf起始               填充数据  

```
#### 程序中没有/bin/sh字符串
>在数据段中找到空白可写的位置，第一次溢出劫持RA手动调用gets函数将/bin/sh字符串写入数据段，并将RA指向system的地址，传参刚刚写入/bin/sh的地址
```
ebp+16          已经写入的/bin/sh的地址（bss_addr）
|
ebp+12          准备写入/bin/sh的地址（bss_addr）
|
ebp+8             call system地址
|                       |
RA                   gets入口地址
|                       |
ebp                    ···
|                       |
buf起始               填充数据   

```

>利用二次溢出。在数据段中找到空白可写的位置，第一次溢出劫持RA手动调用gets函数将/bin/sh字符串写入数据段，并将RA指向main函数的起始地址然程序正常运行再来一次输入导致第二次溢出，本次溢出劫持RA为system的入口地址，并设置好system的返回地址和参数（刚刚写入/bin/sh的地址）

**buf1**
```
ebp+12          准备写入/bin/sh的地址（bss_addr）
|
ebp+8                 main地址
|                       |
RA                   gets入口地址
|                       |
ebp                    ···
|                       |
buf起始               填充数据   

```
**buf2**
```
ebp+12          已经写入的/bin/sh的地址（bss_addr）
|
ebp+8                system返回地址
|                       |
RA                   system入口地址
|                       |
ebp                    ···
|                       |
buf起始               填充数据   

```
#### 程序中有int 80指令和/bin/sh字符串
>利用rop给寄存器传参然后劫持RA为int 80的地址从而执行系统调用execve("/bin/sh",null,null)

```
ebp+36             int 80 地址
|                      |
ebp+32                 0
|                      |
ebp+28             pop_edx_ret
|                      |
ebp+24                 0
|                      |
ebp+20             pop_ecx_ret
|                      |
ebp+16             /bin/sh地址
|                      |
ebp+12              pop_ebx
|                      |
ebp+8                 0x0b
|                      |
RA                 pop_eax_ret
|                      |
ebp                   ···
|                      |
buf起始              填充数据   
```

### 程序中没有出现system和int 80
>第一次溢出利用已有的puts或者printf之类的函数打印出已调用的函数的真实地址从而泄露基地址，然后根据偏移量算出system的真实地址，重新计算偏移量后第二次溢出劫持RA到计算出的system的真实地址，设置好system的返回地址和参数

**buf1**
```
ebp+12             已调用函数的真实地址（如puts_got_addr）
|                       |
ebp+8                 main地址
|                       |
RA                   puts入口地址
|                       |
ebp                    ···
|                       |
buf起始               填充数据   

```

根据打印出来的puts_got_addr计算出基地址和system的真实地址
*公式*

puts_offset=libc.dump('puts')
system_offset=libc.dump('system')

- 基地址=puts_got_addr-puts_offset
- system的真实地址=基地址+system_offset
  
**buf2**
```
ebp+12               /bin/sh的地址
|
ebp+8                system返回地址
|                       |
RA                   system真实地址
|                       |
ebp                    ···
|                       |
buf起始               填充数据   

```

>可以通过rop来调整栈的布局