#include "../../vendor/IT8951-ePaper/Raspberry/lib/e-Paper/EPD_IT8951.h"

#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <endian.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#ifndef UNUSED
#define UNUSED(x) (void)(x)
#endif

typedef enum fread_mock_read_value_type_t {
    UINT8_T_TYPE,
    UINT16_T_TYPE
} fread_mock_read_value_type_t;

void __real_free(void *ptr);
int __real_strcmp(const char *s1, const char *s2);
size_t __real_strlen(const char *s);

void reset_fclose_mock(void);
void reset_fopen_mock(void);
void reset_fread_mock(void);
void reset_free_mock(void);
void reset_malloc_mock(void);
void reset_stat_mock(void);
void reset_strcmp_mock(void);
void reset_strlen_mock(void);
void reset_epd_it8951_4bp_refresh_mock(void);
void reset_epd_it8951_8bp_refresh_mock(void);
void reset_epd_it8951_clear_refresh_mock(void);
void reset_gui_read_bmp_mock(void);
void reset_mocks(void);

int __wrap_fclose(FILE *stream);

FILE *__wrap_fopen(const char *path, const char *mode);

size_t __wrap_fread(void *ptr, size_t size, size_t count, FILE *stream);

void __wrap_free(void *ptr);

void *__wrap_malloc(size_t size);

int __wrap___xstat(int ver, const char *path, struct stat *stat_buf);

int __wrap_strcmp(const char *str1, const char *str2);

size_t __wrap_strlen(const char *s);

void __wrap_EPD_IT8951_4bp_Refresh(
    uint8_t *frame_buffer,
    uint16_t x,
    uint16_t y,
    uint16_t width,
    uint16_t height,
    bool hold,
    uint32_t target_memory_address,
    bool packed_write);

void __wrap_EPD_IT8951_8bp_Refresh(
    uint8_t *frame_buffer,
    uint16_t x,
    uint16_t y,
    uint16_t width,
    uint16_t height,
    bool hold,
    uint32_t target_memory_address);

void __wrap_EPD_IT8951_Clear_Refresh(
    IT8951_Dev_Info device_info,
    uint32_t target_memory_address,
    uint16_t mode);

uint8_t __wrap_GUI_ReadBmp(const char *path, uint16_t x, uint16_t y);

void __wrap_Paint_Clear(uint16_t color);

void __wrap_Paint_NewImage(
    uint8_t *image,
    uint16_t width,
    uint16_t height,
    uint16_t rotate,
    uint16_t color);

void __wrap_Paint_SelectImage(uint8_t *image);

void __wrap_Paint_SetBitsPerPixel(uint8_t bits_per_pixel);

void __wrap_Paint_SetMirroring(uint8_t mirror);

void __wrap_Paint_SetRotate(uint16_t rotate);
