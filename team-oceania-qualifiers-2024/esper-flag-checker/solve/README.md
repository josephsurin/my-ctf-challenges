We are given a dump of the entirety of the hypothetical device's flash. Running `strings` tells us that its an ESP-IDF project. We can start by looking for the partition table by looking for the magic bytes `\xaa\x50`:

```py
>>> flash = open('flash.bin','rb').read()
>>> hex(flash.index(b'\xaa\x50'))
>>> hexdump(flash[0x10000:0x10000+0x100])
00000000: AA 50 01 02 00 10 01 00  00 60 00 00 6E 76 73 00  .P.......`..nvs.
00000010: 00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  ................
00000020: AA 50 01 01 00 70 01 00  00 10 00 00 70 68 79 5F  .P...p......phy_
00000030: 69 6E 69 74 00 00 00 00  00 00 00 00 00 00 00 00  init............
00000040: AA 50 00 00 00 00 02 00  00 00 10 00 66 61 63 74  .P..........fact
00000050: 6F 72 79 00 00 00 00 00  00 00 00 00 00 00 00 00  ory.............
00000060: EB EB FF FF FF FF FF FF  FF FF FF FF FF FF FF FF  ................
00000070: 16 5F 84 4E 94 27 08 E7  7E 2C 2B 99 CA 96 49 4F  ._.N.'..~,+...IO
00000080: FF FF FF FF FF FF FF FF  FF FF FF FF FF FF FF FF  ................
00000090: FF FF FF FF FF FF FF FF  FF FF FF FF FF FF FF FF  ................
000000A0: FF FF FF FF FF FF FF FF  FF FF FF FF FF FF FF FF  ................
000000B0: FF FF FF FF FF FF FF FF  FF FF FF FF FF FF FF FF  ................
000000C0: FF FF FF FF FF FF FF FF  FF FF FF FF FF FF FF FF  ................
000000D0: FF FF FF FF FF FF FF FF  FF FF FF FF FF FF FF FF  ................
000000E0: FF FF FF FF FF FF FF FF  FF FF FF FF FF FF FF FF  ................
000000F0: FF FF FF FF FF FF FF FF  FF FF FF FF FF FF FF FF  ................
>>> open('partition-table.bin','wb').write(flash[0x10000:0x10000+0x100])
```

To carve an ELF out of the dump, https://github.com/tenable/esp32_image_parser/tree/master works well with a few patches:

```diff
diff --git a/esp32_firmware_reader.py b/esp32_firmware_reader.py
index b0ddf04..115590d 100644
--- a/esp32_firmware_reader.py
+++ b/esp32_firmware_reader.py
@@ -28,7 +28,7 @@ def print_verbose(verbose, value):
         print(value)
 
 def read_partition_table(fh, verbose=False):
-    fh.seek(0x8000)
+    fh.seek(0x10000)
     partition_table = {}
 
     print_verbose(verbose, "reading partition table...")
diff --git a/esp32_image_parser.py b/esp32_image_parser.py
index 6503cf7..685d620 100755
--- a/esp32_image_parser.py
+++ b/esp32_image_parser.py
@@ -8,6 +8,7 @@ from makeelf.elf import *
 from esptool import *
 from esp32_firmware_reader import *
 from read_nvs import *
+from esptool.bin_image import *
 
 def image_base_name(path):
     filename_w_ext = os.path.basename(path)
@@ -51,9 +52,12 @@ def image2elf(filename, output_file, verbose=False):
 
     # maps segment names to ELF sections
     section_map = {
-        'DROM'                      : '.flash.rodata',
-        'BYTE_ACCESSIBLE, DRAM, DMA': '.dram0.data',
-        'IROM'                      : '.flash.text',
+        'DROM'                 : '.flash.rodata',
+        'BYTE_ACCESSIBLE, DRAM': '.dram0.data',
+        'IROM'                 : '.flash.text',
+        # 'DROM'                      : '.flash.rodata',
+        # 'BYTE_ACCESSIBLE, DRAM, DMA': '.dram0.data',
+        # 'IROM'                      : '.flash.text',
         #'RTC_IRAM'                  : '.rtc.text' TODO
     }
```

We can use this tool to dump the partition table and also create an ELF from the app partition:

```
$ python esp32_image_parser/esp32_image_parser.py show_partitions flash.bin
reading partition table...
entry 0:
  label      : nvs
  offset     : 0x11000
  length     : 24576
  type       : 1 [DATA]
  sub type   : 2 [WIFI]

entry 1:
  label      : phy_init
  offset     : 0x17000
  length     : 4096
  type       : 1 [DATA]
  sub type   : 1 [RF]

entry 2:
  label      : factory
  offset     : 0x20000
  length     : 1048576
  type       : 0 [APP]
  sub type   : 0 [FACTORY]

MD5sum:
165f844e942708e77e2c2b99ca96494f
Done

$ python esp32_image_parser/esp32_image_parser.py create_elf -partition factory flash.bin -o chal.elf
Dumping partition 'factory' to factory_out.bin

Writing ELF to chal.elf...
```

Since Ghidra 11.0, there is native support for Xtensa, so we can just load this ELF into Ghidra.

We can find the main function by looking at xrefs for interesting strings like `"Enter flag"` or `"Correct"` (slightly cleaned up):

```c
void main(void) {
  int iVar1;
  undefined buf [288];
  
  iVar1 = nvs_flash_init();
  if (iVar1 != 0) {
    FUN_40085fbc(iVar1,s_./main/main.c_3f403348,0x51,s_`_@app_main_3f4078e5 + 3,
                 s_nvs_flash_init()_3f403334);
  }
  printf(s_Enter_flag:_3f403358);
  iVar1 = FUN_4008931c();
  fflush(*(undefined4 *)(iVar1 + 8));
  memset(buf,0,0x100);
  read_line(buf,0x32);
  puts(s_Checking..._3f403368);
  iVar1 = check_flag(buf);
  if (iVar1 == 0) {
    puts(s_Incorrect!_3f403388);
  }
  else {
    printf(s__Correct!_Flag:_%s_3f403374,buf);
  }
  return;
}
```

We can take note that the app uses [nvs](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/storage/nvs_flash.html) since it calls `nvs_flash_init`. The `check_flag` function looks something like this:

```c
undefined4 check_flag(char *flag) {
  undefined4 uVar1;
  int i;
  undefined4 local_30;
  char v;
  undefined hex_str [43];
  
  i = strlen(flag);
  if (i == 0x31) {
    FUN_400d7dd8(&"flag",1,&local_30);
    v = '\0';
    memset(hex_str,0,3);
    for (i = 0; i < 0x31; i = i + 1) {
      int_to_hex(flag[i],hex_str);
      FUN_400d7e18(local_30,hex_str,&v);
      if ((char)(v * '\a') != (&DAT_3ffb02a4)[i]) {
        return 0;
      }
    }
    uVar1 = 1;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}
```

The `FUN_400d7dd8` and `FUN_400d7e18` functions may be mysterious, but after some reversing we can determine that they are `nvs_open` and `nvs_get_u8` respectively (for example `FUN_400d7cc4` returns `0x1107` and [searching](https://github.com/search?q=repo%3Aespressif%2Fesp-idf+0x1107&type=code) for this is insightful).

Then, we dump the data from the default nvs partition which is what is used in the flag checker function:

```
$ python3 esp32_image_parser/esp32_image_parser.py dump_partition -partition nvs flash.bin
Dumping partition 'nvs' to nvs_out.bin

$ python3 esp-idf/components/nvs_flash/nvs_partition_tool/nvs_tool.py nvs_out.bin
Page no. 0, Status: Full, Version: 2, CRC32: b9ba2d84, Page address: 0x0
 Entry state bitmap: aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa fa 
 000. Written, Namespace Index: 000, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: f44672f4 | flag : 1
 001. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32:  ff31029 | 00 : 4
 002. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32:  540e635 | 01 : 14
 003. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 3ac28ceb | 02 : 63
 004. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: c4583a23 | 03 : 246
 005. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: b4fcd491 | 04 : 38
 006. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32:  8436524 | 05 : 237
 007. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32:  bd6df25 | 06 : 146
 008. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 63165ebe | 07 : 181
 009. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: dcaf48ba | 08 : 12
 010. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 4b04dd6b | 09 : 219
 011. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 46ceb326 | 0a : 180
 012. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 95b0a99c | 0b : 171
 013. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: aadf3d48 | 0c : 128
 014. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 284fe532 | 0d : 67
 015. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: fecfcc90 | 0e : 254
 016. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: f28cb29a | 0f : 62
 017. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: ee2ce400 | 10 : 117
 018. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 377a09a9 | 11 : 119
 019. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 28ae138d | 12 : 105
 020. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 3cd5a33d | 13 : 94
 021. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 443da21f | 14 : 213
 022. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 99ffdf23 | 15 : 91
 023. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: d0038dcf | 16 : 125
 024. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 184be2c1 | 17 : 253
 025. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 23b8fa3f | 18 : 64
 026. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 1843fe7e | 19 : 231
 027. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: deb9bb36 | 1a : 109
 028. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: afc6a990 | 1b : 137
 029. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: e3c4c864 | 1c : 13
 030. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: c3551802 | 1d : 53
 031. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: e7e10768 | 1e : 155
 032. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 71203134 | 1f : 98
 033. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: d152f7bd | 20 : 224
 034. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 371d71c5 | 21 : 196
 035. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32:  e826d07 | 22 : 37
 036. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 1621a2b2 | 23 : 197
 037. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: b2fa7c2e | 24 : 249
 038. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: e2b9bdff | 25 : 28
 039. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 8c89b472 | 26 : 241
 040. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 3b745159 | 27 : 9
 041. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 6e2c4125 | 28 : 78
 042. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: c719e2a2 | 29 : 139
 043. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: fc015529 | 2a : 173
 044. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 3d6f763a | 2b : 88
 045. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 62fa73e0 | 2c : 2
 046. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: e5796688 | 2d : 121
 047. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: adef97e9 | 2e : 113
 048. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 568b1239 | 2f : 26
 049. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 3bcf570a | 30 : 162
 050. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 19663e7c | 31 : 220
 051. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 73c2a764 | 32 : 189
 052. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: f8289290 | 33 : 11
 053. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: a5852e5a | 34 : 23
 054. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: d71979f8 | 35 : 129
 055. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: cbc3d8d2 | 36 : 247
 056. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32:  4119c47 | 37 : 147
 057. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: ab315563 | 38 : 156
 058. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 81d4d385 | 39 : 185
 059. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 80c6c2cd | 3a : 1
 060. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: b7084783 | 3b : 107
 061. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: a831a3ad | 3c : 111
 062. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: ac6293a4 | 3d : 244
 063. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: ab8e473a | 3e : 29
 064. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: eeaa6ad3 | 3f : 236
 065. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 8c14880e | 40 : 250
 066. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 262f9087 | 41 : 87
 067. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: ec03e70a | 42 : 145
 068. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: a495166b | 43 : 153
 069. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 753e4bcb | 44 : 218
 070. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: a5a31475 | 45 : 183
 071. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: da8d9f5f | 46 : 216
 072. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: c0a7b663 | 47 : 100
 073. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 23f3e1b6 | 48 : 226
 074. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: bc149bf7 | 49 : 110
 075. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 2d41cbf0 | 4a : 232
 076. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: cdfec59e | 4b : 6
 077. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 75d5e4be | 4c : 65
 078. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: c010b885 | 4d : 255
 079. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 51a65b48 | 4e : 248
 080. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: afd1138a | 4f : 43
 081. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 176d3b10 | 50 : 75
 082. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 7abe7799 | 51 : 212
 083. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: afdd1b3f | 52 : 27
 084. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: cdd893bd | 53 : 59
 085. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: a3b43ba3 | 54 : 214
 086. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: cd69cc24 | 55 : 33
 087. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: d4a0a01c | 56 : 239
 088. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 12b9569e | 57 : 228
 089. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32:  89b631d | 58 : 66
 090. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 4fdb5677 | 59 : 245
 091. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 51865c14 | 5a : 68
 092. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32:   af3e48 | 5b : 143
 093. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 5baeab07 | 5c : 89
 094. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 9f8fe495 | 5d : 20
 095. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 72823673 | 5e : 3
 096. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: d291d9e9 | 5f : 179
 097. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: f5a7aa94 | 60 : 93
 098. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: d70ec3e2 | 61 : 35
 099. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: b0f57878 | 62 : 161
 100. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: f1a83b0e | 63 : 198
 101. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 145859e1 | 64 : 144
 102. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32:  32d525f | 65 : 207
 103. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 4b565d34 | 66 : 221
 104. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: b1587b69 | 67 : 152
 105. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 3fa99f30 | 68 : 140
 106. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: c23d92f6 | 69 : 45
 107. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: ccf947b5 | 6a : 42
 108. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: c233df36 | 6b : 182
 109. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: dd0a3b18 | 6c : 178
 110. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 7e4bce1f | 6d : 106
 111. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 86cc0ecb | 6e : 115
 112. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 9447366d | 6f : 142
 113. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 3233585b | 70 : 211
 114. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 9e1536ce | 71 : 174
 115. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: cba8c407 | 72 : 233
 116. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 7a485730 | 73 : 193
 117. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 4085516f | 74 : 72
 118. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: a443319e | 75 : 48
 119. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: c422a19f | 76 : 86
 120. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 5a428659 | 77 : 238
 121. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32:  e9dcba2 | 78 : 157
 122. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 8e35aac8 | 79 : 24
 123. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: f8dede35 | 7a : 131
 124. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: e95b5d9d | 7b : 22
 125. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 64ac1e75 | 7c : 112

Page no. 1, Status: Full, Version: 2, CRC32: 389f48a3, Page address: 0x1000
 Entry state bitmap: aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa fa 
 000. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: bb56da59 | 7d : 184
 001. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 36a199b1 | 7e : 222
 002. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 943b90a2 | 7f : 50
 003. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: f76d5574 | 80 : 44
 004. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 85f102d6 | 81 : 186
 005. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 21767dd9 | 82 : 134
 006. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 8d50134c | 83 : 251
 007. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 935ff57c | 84 : 209
 008. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 9b65e5e9 | 85 : 135
 009. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: c10ed32b | 86 : 127
 010. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: c1782c2e | 87 : 114
 011. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: a9b0b10a | 88 : 79
 012. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: cda84f94 | 89 : 191
 013. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: d46f6e6c | 8a : 234
 014. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 8e0458ae | 8b : 18
 015. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: d01600f3 | 8c : 124
 016. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 83ea25b5 | 8d : 235
 017. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 6f60aad4 | 8e : 200
 018. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 6ffbabdb | 8f : 223
 019. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: b4b3a941 | 90 : 166
 020. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 15cae556 | 91 : 56
 021. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32:  15cabec | 92 : 21
 022. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: acfd98fe | 93 : 92
 023. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: ff01bdb8 | 94 : 203
 024. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 7e2e8155 | 95 : 122
 025. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 45387b1e | 96 : 199
 026. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 7dcdc451 | 97 : 8
 027. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 291289aa | 98 : 123
 028. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 630d9e42 | 99 : 47
 029. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32:  3624383 | 9a : 210
 030. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 28ed66e8 | 9b : 217
 031. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: d677d020 | 9c : 16
 032. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 1f09bd30 | 9d : 190
 033. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: ed4b74fd | 9e : 160
 034. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: e381ec7e | 9f : 60
 035. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 79b8879f | a0 : 40
 036. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 48868ac7 | a1 : 136
 037. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 6e568d2e | a2 : 96
 038. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 95dff6f4 | a3 : 17
 039. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 1c0d7a10 | a4 : 225
 040. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32:  ce25a35 | a5 : 90
 041. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 69900726 | a6 : 132
 042. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: b4527a1a | a7 : 10
 043. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: f6099edd | a8 : 31
 044. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: f2ebf14d | a9 : 158
 045. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 38c9cb00 | aa : 195
 046. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 723b22e2 | ab : 141
 047. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: e38dc12f | ac : 138
 048. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 29fd1731 | ad : 76
 049. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 27da71b8 | ae : 202
 050. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: b11b47e4 | af : 51
 051. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: a3f15651 | b0 : 252
 052. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 62728b48 | b1 : 19
 053. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 4d693eb6 | b2 : 148
 054. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 7c5733ee | b3 : 52
 055. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: f68b0404 | b4 : 172
 056. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32:  811b2cc | b5 : 101
 057. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 3fdf3782 | b6 : 15
 058. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 3833e31c | b7 : 230
 059. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: edb56d0f | b8 : 41
 060. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 1b633457 | b9 : 187
 061. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: e51a3155 | ba : 243
 062. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 655fae35 | bb : 108
 063. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 8adb9a5a | bc : 39
 064. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: af59872e | bd : 167
 065. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 7d4d3e19 | be : 150
 066. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 5914df79 | bf : 34
 067. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: c9b26889 | c0 : 54
 068. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32:  b3f0e9e | c1 : 177
 069. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 4f9c7ef0 | c2 : 116
 070. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: fffbb040 | c3 : 104
 071. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: a44b7a96 | c4 : 164
 072. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 59df7750 | c5 : 5
 073. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: d99ae830 | c6 : 154
 074. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 1055dab9 | c7 : 46
 075. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32:  bf0b2bd | c8 : 188
 076. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: cbf43223 | c9 : 103
 077. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 2e56bc9f | ca : 170
 078. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: ef389f8c | cb : 95
 079. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: ef4e6089 | cc : 82
 080. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: f4524bab | cd : 192
 081. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: deb7cd4d | ce : 229
 082. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: f9e09723 | cf : 57
 083. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: ad8cac38 | d0 : 102
 084. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 2abee6c9 | d1 : 7
 085. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 39b283e8 | d2 : 206
 086. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: b258b61c | d3 : 120
 087. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 22d857cf | d4 : 81
 088. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 5d1b22ef | d5 : 36
 089. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 6010aeb8 | d6 : 73
 090. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: ae45b7aa | d7 : 25
 091. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 54438d48 | d8 : 70
 092. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 3e0aea5a | d9 : 61
 093. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32:  9ca22d4 | da : 204
 094. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: ebfcca33 | db : 126
 095. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: b0fd5f7c | dc : 168
 096. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 5d41d203 | dd : 165
 097. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 30929e8a | de : 58
 098. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 1b1dbbe1 | df : 49
 099. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 27eb9d81 | e0 : 85
 100. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: c63e3062 | e1 : 149
 101. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: bd842bdd | e2 : 118
 102. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 4ad52f02 | e3 : 208
 103. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 873fd287 | e4 : 242
 104. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 706ed658 | e5 : 84
 105. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: ef645213 | e6 : 194
 106. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 25a5db94 | e7 : 30
 107. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: b59c7961 | e8 : 55
 108. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: c40e95cd | e9 : 201
 109. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 7310c32c | ea : 176
 110. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: a06ed996 | eb : 175
 111. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: b71bd228 | ec : 240
 112. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 33967c4e | ed : 227
 113. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 5cccd64e | ee : 32
 114. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 86797ee3 | ef : 80
 115. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 3c576e53 | f0 : 99
 116. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: dc059e37 | f1 : 151
 117. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 7905bcbf | f2 : 159
 118. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: f575a2d0 | f3 : 205
 119. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 626f6898 | f4 : 0
 120. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 4c1e7eeb | f5 : 169
 121. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 93b81b54 | f6 : 97
 122. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32:  f51da1b | f7 : 133
 123. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 41d241d9 | f8 : 71
 124. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 4b61b7c5 | f9 : 77
 125. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 9c85702a | fa : 69

Page no. 2, Status: Active, Version: 2, CRC32: 6081e18b, Page address: 0x2000
 Entry state bitmap: aa 0a f8 ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff 
 000. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: afdf65f1 | fb : 163
 001. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32:  170eded | fc : 130
 002. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: bd7e03c1 | fd : 83
 003. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: f17c6235 | fe : 215
 004. Written, Namespace Index: 001, Type: uint8_t   , Span: 001, Chunk Index: 255, CRC32: 331cfa28 | ff : 74
 ...
```

We are interested in the values which have two digit hex strings as their keys. From the flag checker function, we can see that this is essentially used as a substitution for checking the flag.

All that's left is to reverse the lookup and get the flag!

```py
CHECK = list(bytes.fromhex('E2 3B 6A 6A 0B DE F5 28 9A F5 25 E5 01 9D 0D A9 6A 3B F5 DE DE A8 E5 47 FA 3B DE DE A9 F0 E5 5F A9 5A A9 5F 47 A9 E5 A9 25 28 3B 25 A9 A9 5F 5C 08'))
PERM = list(map(int, '4 14 63 246 38 237 146 181 12 219 180 171 128 67 254 62 117 119 105 94 213 91 125 253 64 231 109 137 13 53 155 98 224 196 37 197 249 28 241 9 78 139 173 88 2 121 113 26 162 220 189 11 23 129 247 147 156 185 1 107 111 244 29 236 250 87 145 153 218 183 216 100 226 110 232 6 65 255 248 43 75 212 27 59 214 33 239 228 66 245 68 143 89 20 3 179 93 35 161 198 144 207 221 152 140 45 42 182 178 106 115 142 211 174 233 193 72 48 86 238 157 24 131 22 112 184 222 50 44 186 134 251 209 135 127 114 79 191 234 18 124 235 200 223 166 56 21 92 203 122 199 8 123 47 210 217 16 190 160 60 40 136 96 17 225 90 132 10 31 158 195 141 138 76 202 51 252 19 148 52 172 101 15 230 41 187 243 108 39 167 150 34 54 177 116 104 164 5 154 46 188 103 170 95 82 192 229 57 102 7 206 120 81 36 73 25 70 61 204 126 168 165 58 49 85 149 118 208 242 84 194 30 55 201 176 175 240 227 32 80 99 151 159 205 0 169 97 133 71 77 69 163 130 83 215 74'.split()))
flag = ''.join(chr(PERM.index(x * pow(7, -1, 256) % 256)) for x in CHECK)
print(flag)
# oiccflag{an_ESPecially_skilled_reverse_engineer!}
```

If you wanted to, you could also run the app on an emulated device using [`espressif/qemu`](https://github.com/espressif/qemu) along with gdb for dynamic analysis. There is a bug which causes it to crash a few times before properly starting, but after waiting for a bit and letting it hit reset a few times it will eventually shows a prompt.

Start QEMU in a terminal with serial port open on `tcp:9999`:

```sh
./qemu/build/qemu-system-xtensa -nographic \
  -machine esp32 \
  -drive file=./flash.bin,if=mtd,format=raw \
  -serial tcp::9999,server,nowait
```

Then connect (e.g. using `idf.py monitor` or something else):

```sh
$ idf.py monitor -p socket://localhost:9999 
Waiting for the device to reconnect...
ets Jul 29 2019 12:21:46

rst:0x1 (POWERON_RESET),boot:0x12 (SPI_FAST_FLASH_BOOT)
configsip: 0, SPIWP:0xee
clk_drv:0x00,q_drv:0x00,d_drv:0x00,cs0_drv:0x00,hd_drv:0x00,wp_drv:0x00
mode:DIO, clock div:2
load:0x3fff0030,len:7172
load:0x40078000,len:15556
load:0x40080400,len:4
ho 8 tail 4 room 4
load:0x40080404,len:3904
entry 0x40080640

I (1148) boot: ESP-IDF v5.3-dev-1353-gb3f7e2c8a4 2nd stage bootloader
I (1161) boot: compile time Jan 16 2024 11:01:26
I (1162) boot: Multicore bootloader
I (1252) boot: chip revision: v0.0
I (1279) boot.esp32: SPI Speed      : 40MHz
I (1281) boot.esp32: SPI Mode       : DIO
I (1283) boot.esp32: SPI Flash Size : 2MB
I (1335) boot: Enabling RNG early entropy source...
I (1407) boot: Partition Table:
I (1408) boot: ## Label            Usage          Type ST Offset   Length
I (1411) boot:  0 nvs              WiFi data        01 02 00011000 00006000
I (1416) boot:  1 phy_init         RF data          01 01 00017000 00001000
I (1419) boot:  2 factory          factory app      00 00 00020000 00100000
I (1460) boot: End of partition table
I (1487) esp_image: segment 0: paddr=00020020 vaddr=3f400020 size=0c16ch ( 49516) map
I (1666) esp_image: segment 1: paddr=0002c194 vaddr=3ffb0000 size=02328h (  9000) load
I (1747) esp_image: segment 2: paddr=0002e4c4 vaddr=40080000 size=01b54h (  6996) load
I (1835) esp_image: segment 3: paddr=00030020 vaddr=400d0020 size=17e70h ( 97904) map
I (2110) esp_image: segment 4: paddr=00047e98 vaddr=40081b54 size=0b490h ( 46224) load
I (2281) boot: Loaded app from partition at offset 0x20000
I (2284) boot: Disabling RNG early entropy source...
I (2346) cpu_start: Multicore app
I (4515) cpu_start: Pro cpu start user code
I (4527) cpu_start: cpu freq: 160000000 Hz
I (4530) cpu_start: Application information:
I (4532) cpu_start: Project name:     hello_world
I (4534) cpu_start: App version:      1
I (4536) cpu_start: Compile time:     Jan 16 2024 11:07:43
I (4541) cpu_start: ELF file SHA256:  23b87a5447e522d4...
I (4543) cpu_start: ESP-IDF:          v5.3-dev-1353-gb3f7e2c8a4
I (4546) cpu_start: Min chip rev:     v0.0
I (4548) cpu_start: Max chip rev:     v3.99
I (4552) cpu_start: Chip rev:         v0.0
I (4569) heap_init: Initializing. RAM available for dynamic allocation:
I (4581) heap_init: At 3FFAE6E0 len 00001920 (6 KiB): DRAM
I (4586) heap_init: At 3FFB2C40 len 0002D3C0 (180 KiB): DRAM
I (4588) heap_init: At 3FFE0440 len 00003AE0 (14 KiB): D/IRAM
I (4590) heap_init: At 3FFE4350 len 0001BCB0 (111 KiB): D/IRAM
I (4592) heap_init: At 4008CFE4 len 0001301C (76 KiB): IRAM
I (4874) spi_flash: detected chip: gd
I (4910) spi_flash: flash io: dio
W (4948) spi_flash: Detected size(8192k) larger than the size in the binary image header(2048k). Using the size in the binary image header.
I (5083) main_task: Started on CPU0
I (5153) main_task: Calling app_main()
E (10163) task_wdt: Task watchdog got triggered. The following tasks/users did not reset the watchdog in time:
E (10163) task_wdt:  - IDLE0 (CPU 0)
E (10163) task_wdt: Tasks currently running:
E (10163) task_wdt: CPU 0: main
E (10163) task_wdt: CPU 1: IDLE1
E (10163) task_wdt: Print CPU 0 (current core) backtrace


Backtrace: 0x400D7293:0x3FFB0F90 0x400D7658:0x3FFB0FB0 0x40083055:0x3FFB0FE0 0x4000BFED:0x3FFB4A70 0x40086BF3:0x3FFB4A80 0x40082337:0x3FFB4AA0 0x40083D37:0x3FFB4AC0 0x40084AFB:0x3FFB4AE0 0x40084B06:0x3FFB4B00 0x40084D01:0x3FFB4B20 0x4008452F:0x3FFB4B40 0x400DADBE:0x3FFB4B80 0x400D8F2B:0x3FFB4BB0 0x400E6A52:0x3FFB4BD0 0x400DA252:0x3FFB4BF0 0x400DA410:0x3FFB4C70 0x400DA65F:0x3FFB4CB0 0x400D8639:0x3FFB4D20 0x400D9116:0x3FFB4D80 0x400D9181:0x3FFB4DA0 0x400D7D52:0x3FFB4DD0 0x400D7D66:0x3FFB4E00 0x400D62E7:0x3FFB4E20 0x400E76A8:0x3FFB4F40 0x40086851:0x3FFB4F70


Enter flag: Checking... <input not echoed...>

Correct! Flag: oiccflag{an_ESPecially_skilled_reverse_engineer!}
I (61933) main_task: Returned from app_main()
```
