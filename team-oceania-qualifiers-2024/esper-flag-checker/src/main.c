#include <stdio.h>
#include <inttypes.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "nvs_flash.h"
#include "nvs.h"

uint8_t CHECK[49] = { 226, 59, 106, 106, 11, 222, 245, 40, 154, 245, 37, 229, 1, 157, 13, 169, 106, 59, 245, 222, 222, 168, 229, 71, 250, 59, 222, 222, 169, 240, 229, 95, 169, 90, 169, 95, 71, 169, 229, 169, 37, 40, 59, 37, 169, 169, 95, 92, 8 };

void readline(char buf[], size_t len) {
    memset(buf, 0, len);
    fpurge(stdin);
    char *bufp;
    bufp = buf;
    while(true) {
        vTaskDelay(100/portTICK_PERIOD_MS);
        *bufp = getchar();
        if(*bufp != '\0' && *bufp != 0xFF && *bufp != '\r') {
            if(*bufp == '\n') {
                *bufp = '\0';
                break;
            }
            else if (*bufp == '\b') {
                if(bufp-buf >= 1)
                    bufp--;
            }
            else {
                bufp++;
            }
        }
        if(bufp-buf > (len)-2) {
            bufp = buf + (len -1);
            *bufp = '\0';
            break;
        }
    } 
}

void int_to_hex(int x, char* buf) {
    int c1 = (x >> 4) & 0xf;
    int c2 = x & 0xf;

    if(0 <= c1 && c1 < 10) {
        buf[0] = '0' + c1;
    } else {
        buf[0] = 'a' + (c1 - 10);
    }

    if(0 <= c2 && c2 < 10) {
        buf[1] = '0' + c2;
    } else {
        buf[1] = 'a' + (c2 - 10);
    }
}

int check_flag(char* input) {
    if(strlen(input) != 49) {
        return 0;
    }

    nvs_handle_t my_handle;
    nvs_open("flag", NVS_READWRITE, &my_handle);

    uint8_t v = 0;
    char hex[3] = { 0 };
    for(int i = 0; i < 49; i++) {
        int_to_hex(input[i], hex);
        nvs_get_u8(my_handle, hex, &v);
        if((v * 7) % 256 != CHECK[i]) {
            return 0;
        }
    }

    return 1;
}

void app_main(void)
{
    ESP_ERROR_CHECK(nvs_flash_init());

    printf("Enter flag: ");
    fflush(stdout);

    char buf[0x100] = { 0 };
    readline(buf, 50);
    printf("Checking...\n");
    if(check_flag(buf)) {
        printf("\nCorrect! Flag: %s\n", buf);
    } else {
        printf("Incorrect!\n");
    }

}
