#include "../../vendor/IT8951-ePaper/Raspberry/lib/e-Paper/EPD_IT8951.h"

#include <stdint.h>

void print_help(void);

int str_ends_with(const char *str, const char *substr);

int display_bmp_image(
    IT8951_Dev_Info device_info,
    uint32_t target_memory_address,
    const char *file_path);

int display_4bpp_image(
    IT8951_Dev_Info device_info,
    uint32_t target_memory_address,
    const char *file_path);
